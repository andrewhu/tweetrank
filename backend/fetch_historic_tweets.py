import datetime
import requests
import sqlite3
import time

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import accounts
import config


def fetch_tweets_v2(query, end_time=None, until_id=None):
    """Fetches tweets from the Twitter API v2"""
    search_endpoint = "https://api.twitter.com/2/tweets/search/recent"
    headers = {
        'content-type': 'application/json',
        'authorization': 'Bearer {}'.format(config.TWITTER_TOKEN_2)
    }
    params = {
        'query': '{} -is:retweet lang:en'.format(query),
        'max_results': 100,
        'tweet.fields': 'created_at,entities'
    }
    if until_id:
        params['until_id'] = until_id
    else:
        params['end_time']: end_time

    return requests.get(search_endpoint, headers=headers, params=params).json()

def get_all_tweets_week(name, query, category):

    # DB Coneection
    conn = sqlite3.connect("data/tweet_sentiment_2020-09.db")
    c = conn.cursor()

    # SEntiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    start_dt = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
    end_time = start_dt.strftime('%Y-%m-%dT%H:%M:00Z')

    # Initial fetch
    tweets = fetch_tweets_v2(query, end_time)
    until_id = tweets['meta']['oldest_id']


    while True:
        # print(f"===== Fetching tweets until {until_id} =====")
        # Fetch tweets
        tweets = fetch_tweets_v2(query, until_id=until_id)

        if 'errors' in tweets:
            print(tweets)
            break
        elif 'meta' in tweets and tweets['meta']['result_count'] == 0:
            print("done")
            break
        else:
            try:
                until_id = tweets['meta']['oldest_id']
                tweets = tweets['data']
            except:
                print(tweets)
        oldest_dt = datetime.datetime.strptime(tweets[-1]['created_at'], '%Y-%m-%dT%H:%M:%S.000Z')

        print("Oldest tweet:", oldest_dt.strftime("%b %d, %Y %I:%M%p"), end=' - ')

        error_count = 0
        for tweet in tweets:
            # Calculate sentiment
            sentiment = analyzer.polarity_scores(tweet['text'])['compound']

            # Calculate timestamp
            timestamp = datetime.datetime.strptime(tweet['created_at'], '%Y-%m-%dT%H:%M:%S.000Z').timestamp()

            # Store in db
            sql = """INSERT INTO tweet_sentiment( tweet_id,  company,  category, text, created_at, sentiment) VALUES (?,?,?,?,?,?)"""

            try:
                c.execute(sql, (tweet['id'], name, category, tweet['text'], timestamp, sentiment))
            except:
                error_count += 1
        print("errors:", error_count, end=' - ')
        conn.commit()

        # Get new db size
        c.execute("SELECT COUNT(*) FROM tweet_sentiment")
        new_size = c.fetchone()[0]

        print("New db size:", new_size)

        time.sleep(2.1)

    conn.close()


if __name__ == "__main__":
    # fetch_week()
    for company in accounts.categories['ISP']:
        handles = [x['handle'] for x in company['accounts']]
        query = ' OR '.join(handles)
        # print(company['name'], query)
        print(f"==== Fetching {company['name']} =====")
        # break
        get_all_tweets_week(company['name'], query, category="ISP")







def fetch_month():
    pass

def fetch_historic():
    pass


API_v1_URL = "https://api.twitter.com/1.1"

def fetch_historic_tweets(query, timespan, max_results=100, from_date=None, to_date=None):
    """Fetch tweets from Twitter's historical endpoints (30-day and all-time) API (v1)"""
    assert timespan in ('30day', 'fullarchive')

    request_url = f"{API_v1_URL}/tweets/search/{timespan}/{config.TWITTER_ENV}.json"

    headers = {
        'authorization': f"Bearer {config.TWITTER_BEARER_TOKEN}",
        'content-type': "application/json"
    }

    # Request parameters
    data = {
        'query': f"{query} lang:en",
        'maxResults': str(max_results)
    }
    if from_date:
        data['fromDate'] = from_date
    if to_date:
        data['toDate'] = to_date

    r = requests.post(request_url, headers=headers, data=json.dumps(data))

    now = int(time.time())

    return r.json(), now







