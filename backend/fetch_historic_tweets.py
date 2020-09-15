from collections import defaultdict
import datetime
import json
import requests
import sqlite3
import time
import pytz

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import accounts
import db_cache
import config

def fetch_tweets(query, to_date, bearer_token, environment, timespan='30day'):
    headers = {
        # 'authorization': f'Bearer {config.TWITTER_MATH189}',
        'authorization': f'Bearer {bearer_token}',
        'content-type': 'application/json'
    }
    data = {
        'query': f"{query} lang:en",
        'maxResults': "100",
        'toDate': to_date
    }
    r = requests.post(f"https://api.twitter.com/1.1/tweets/search/{timespan}/{environment}", headers=headers, data=json.dumps(data))
    return r.json()

def do_it():
    earliest_tweet = "Sep 01 00:00:00 +0000 2020"  # Earliest date to fetch tweets from
    timespan = '30day'
    category = 'Restaurant'  # Restaurant or ISP

    # DB Coneection
    conn = sqlite3.connect("data/tweet_sentiment_2020-09.db")
    c = conn.cursor()

    # Sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    # Earliest date to fetch from
    earliest_date = datetime.datetime.strptime(earliest_tweet,"%b %d %H:%M:%S %z %Y" )

    # Earliest Tweet date we have stored
    timestamps = db_cache.get_earliest_timestamps()

    sql = """INSERT INTO tweet_sentiment(tweet_id, company, category, text, created_at, sentiment) VALUES (?,?,?,?,?,?)"""

    utc = pytz.UTC

    total_fetched = 0

    # List of tokens
    tokens = config.TWITTER_TOKENS
    token_idx = 0
    token = tokens[token_idx]
    bearer_token = token['token']
    environment = token['env']

    for company in accounts.categories[category]:
        company_name = company['name']
        print(f"===== Fetching Tweets for {company_name} =====")
        query = ' OR '.join([x['handle'] for x in company['accounts']])

        # Get time of earliest tweet we have for this company
        to_date = utc.localize(datetime.datetime.fromtimestamp(timestamps[company_name]))

        if to_date < earliest_date:
            print(f"Skipping {company_name} bc earliest time is {to_date.strftime('%b %d, %Y %I:%M%p')}")
            continue

        while to_date > earliest_date:
            to_date_str = to_date.strftime("%Y%m%d%H%M")
            response = fetch_tweets(query=query,
                                    to_date=to_date_str,
                                    bearer_token=bearer_token,
                                    environment=environment,
                                    timespan=timespan)

            # Try to switch token if our quota is reached
            while 'error' in response:
                print("switching tokens")
                time.sleep(0.5)
                token_idx += 1
                if token_idx >= len(tokens):
                    print("Exhausted tokens")
                    return
                token = tokens[token_idx]
                bearer_token = token['token']
                environment = token['env']

                response = fetch_tweets(query=query,
                                        to_date=to_date_str,
                                        bearer_token=bearer_token,
                                        environment=environment,
                                        timespan=timespan)

            if 'results' not in response:
                print(response)
                break
            tweets = response['results']
            total_fetched += len(tweets)
            to_date = datetime.datetime.strptime(tweets[-1]['created_at'], "%a %b %d %H:%M:%S %z %Y")
            print(f"Earliest for {company_name}: {to_date.strftime('%b %d %I:%M%p')}", end=' - ')

            # Store tweets to db
            for tweet in tweets:
                # Ignore retweets
                if 'retweeted_status' in tweet:
                    continue
                tweet_id = tweet['id']
                created_at = datetime.datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S %z %Y")

                # Ignore august
                if created_at.month < 9:
                    continue

                created_at_ts = int(created_at.timestamp())
                sentiment = analyzer.polarity_scores(tweet['text'])['compound']
                c.execute(sql, (tweet_id, company_name, category, tweet['text'], created_at_ts, sentiment))
            conn.commit()
            print(f"New db size: {db_cache.get_db_size()}", end=' - ')
            print(f"Total tweets fetched: {total_fetched}")
            time.sleep(2.05)


if __name__ == "__main__":
    do_it()


