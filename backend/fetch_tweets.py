"""
Methods for fetching tweets from the Twitter API
"""

import datetime
import json
import logging
import os.path
import redis
import requests

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import db_cache

import accounts
import config

def fetch_recent_tweets(query, since_id=None, max_results=100):
    """Returns Tweets from within the past 7 days (API v2)"""
    endpoint = "https://api.twitter.com/2/tweets/search/recent"
    headers = {
        'content-type': 'application/json',
        'authorization': f"Bearer {config.TWITTER_BEARER_TOKEN}"
    }
    params = {
        'query': f"{query} -is:retweet lang:en",
        'max_results': max_results,
        'tweet.fields': "created_at,entities"
    }
    if since_id:
        params['since_id'] = since_id
    try:
        return requests.get(endpoint, headers=headers, params=params).json()
    except:
        return None

def process_tweets(tweets, analyzer):
    """Calculates sentiment and reformats time"""
    for tweet in tweets:
        tweet['datetime'] = datetime.datetime.strptime(tweet['created_at'], '%Y-%m-%dT%H:%M:%S.000Z')
        tweet['sentiment'] = analyzer.polarity_scores(tweet['text'])['compound']
    return tweets

# Log settings
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
now_dt = datetime.datetime.utcnow()
year_month = now_dt.strftime("%Y-%m")
log_filename = "{}/logs/fetch_tweets_{}.log".format(DIR_PATH, year_month)
logging.basicConfig(filename=log_filename, level=logging.INFO)

if __name__ == "__main__":
    logging.info("===== Started fetch at {} =====".format(now_dt.strftime("%b %d, %Y %I:%M%p")))

    # cache
    cache = redis.Redis(host='localhost', port=6379)

    # Since IDs
    since_ids = json.loads(cache.get("since_ids") or '{}')

    # Sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    # Fetch tweets from each company and category
    for category_name in accounts.categories:
        for company in accounts.categores[category_name]:
            all_handles = ' OR '.join([account['handle'] for account in company['accounts']])
            response = fetch_recent_tweets(query=all_handles, since_id=since_ids.get(company['name']))
            try:
                result_count = response['meta']['result_count']
                if result_count == 0:
                    continue
                tweets = response['data']

                # Process tweets
                tweets = process_tweets(tweets, analyzer)

                # Store to db and cache
                db_cache.store_to_cache(tweets, company['name'], category_name, cache)
                db_cache.store_to_db(tweets, company['name'], category_name)

                # Update since IDs
                since_ids[company['name']] = response['meta']['newest_id']

            except:
                logging.error(f"Something went wrong fetching Tweets for {all_handles}. Response: {tweets}")

    cache.set("since_ids", since_ids)

    