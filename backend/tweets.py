# decompyle3 version 3.3.2
# Python bytecode 3.8 (3413)
# Decompiled from: Python 3.8.2 (default, Jul 16 2020, 14:00:26) 
# [GCC 9.3.0]
# Embedded file name: /var/www/tweetrank/backend/tweets.py
# Compiled at: 2020-09-09 23:26:46
# Size of source mod 2**32: 6528 bytes
import collections, datetime, json, os.path, redis, requests
from shutil import copyfile
import sqlite3, time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import accounts, config
CATEGORIES = accounts.CATEGORIES


def fetch_recent_tweets(minutes_ago=10):
    """Fetch tweets since the last fetch and store them in the database and cache
    Note: Using Twitter API v2"""

            resp = requests.get(search_url, headers=headers, params=params).json()
            if 'data' in resp:
                tweets[category][company['name']] = resp['data']
        else:
            return tweets


def compute_sentiment(tweets):
    analyzer = SentimentIntensityAnalyzer()
    for category in tweets:
        for company in tweets[category]:
            for tweet in tweets[category][company]:
                tweet['sentiment'] = analyzer.polarity_scores(tweet['text'])['compound']


def update_cache(tweets):
    cache = redis.Redis(host='localhost', port=6379)

    def new_average(average, count, val):
        return (average * count + val) / (count + 1)

    for category in tweets:
        category_data = cache.get(category)
        category_data = json.loads(category_data) if category_data else {}
        for company in tweets[category]:
            company_data = cache.get(company)
            company_data = json.loads(company_data) if company_data else {}
            for tweet in tweets[category][company]:
                created_at = datetime.datetime.strptime(tweet['created_at'], '%Y-%m-%dT%H:%M:%S.000Z')
                ymd = created_at.strftime('%Y_%m_%d')
                category_sentiment, category_count = category_data.get(ymd, (0, 0))
                new_category_sentiment = category_sentiment * category_count + tweet['sentiment']
                company_sentiment, company_count = company_data.get(ymd, (0, 0))
                category_data[ymd] = ((category_sentiment * category_count + sentiment) / (category_count + 1), category_count + 1)
                company_data[ymd] = ((company_sentiment * company_count + sentiment) / (company_count + 1), company_count + 1)
            else:
                cache.set(company, json.dumps(company_data))

        else:
            cache.set(category, json.dumps(category_data))


def update_db_and_cache():
    """Fetches new Tweets and stores them into the database and cache"""
    tweets = fetch_recent_tweets(minutes_ago=5)
    tweets_by_month = collections.defaultdict(list)
    sentiment_by_day = dict()
    for category in tweets.keys():
        category_data = cache.get(category)
        category_data = json.loads(category_data) if category_data else {}
        for company in tweets[category]:
            company_data = cache.get(company)
            company_data = json.loads(company_data) if company_data else {}
            for tweet in tweets[category][company]:
                created_at = datetime.datetime.strptime(tweet['created_at'], '%Y-%m-%dT%H:%M:%S.000Z')
                ymd = created_at.strftime('%Y_%m_%d')
                ym = created_at.strftime('%Y_%m')
                timestamp = int(created_at.timestamp())
                tweet['timestamp'] = timestamp
                category_sentiment, category_count = category_data.get(ymd, (0, 0))
                company_sentiment, company_count = company_data.get(ymd, (0, 0))
                category_data[ymd] = ((category_sentiment * category_count + sentiment) / (category_count + 1), category_count + 1)
                company_data[ymd] = ((company_sentiment * company_count + sentiment) / (company_count + 1), company_count + 1)
                tweets_by_month[ym].append(tweet)
            else:
                cache.set(company, json.dumps(company_data))

        else:
            cache.set(category, json.dumps(category_data))
# okay decompiling __pycache__/tweets.cpython-38.pyc
