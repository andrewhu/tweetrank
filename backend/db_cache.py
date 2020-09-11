"""
Methods for storing and fetching Tweets from the database and cache
"""

from collections import defaultdict
from datetime import datetime
import glob
import json
import os.path
import redis
from shutil import copyfile
import sqlite3

def store_to_cache(tweets, category):
    """Stores Tweet sentiments to cache.
    Key structure: Category/Company (dict) -> YYYY-MM-DD (Avg sentiment for that day)"""
    cache = redis.Redis(host='localhost', port=6379)

    category_sentiment = json.loads(cache.get(category) or '{}')
    for company in tweets.keys():
        company_sentiment = json.loads(cache.get(company) or '{}')
        for tweet in tweets[company]:
            ymd = tweet['datetime'].strftime('%Y-%m-%d')
            cat_total, cat_count = category_sentiment.get(ymd, (0,0))
            category_sentiment[ymd] = cat_total+tweet['sentiment'], cat_count+1
            cmp_total, cmp_count = company_sentiment.get(ymd, (0,0))
            company_sentiment[ymd] = cmp_total+tweet['sentiment'], cmp_count+1
        cache.set(company, json.dumps(company_sentiment))
    cache.set(category, json.dumps(category_sentiment))


def store_to_db(tweets, category):
    """Stores tweets into the database, one db file per month"""
    # Organize tweets by date

    tweets_by_month = defaultdict(list)
    for company in tweets.keys():
        for tweet in tweets[company]:
            tweet['company'] = company
            year_month = tweet['datetime'].strftime('%Y-%m')
            tweets_by_month[year_month].append(tweet)

    for year_month in tweets_by_month.keys():
        db_filename = "data/tweet_sentiment_{}.db".format(year_month)
        if not os.path.exists(db_filename):
            copyfile("data/templates/tweet_sentiment_template.db", db_filename)

        conn = sqlite3.connect(db_filename)
        c = conn.cursor()
        sql = """
        INSERT INTO tweet_sentiment(
            tweet_id, 
            company, 
            category,
            text,
            created_at,
            sentiment
        ) VALUES (?,?,?,?,?,?)"""
        for tweet in tweets_by_month[year_month]:
            c.execute(sql, (tweet['id'],
                            tweet['company'],
                            category,
                            tweet['text'],
                            int(tweet['datetime'].timestamp()),
                            tweet['sentiment']))
        conn.commit()
        conn.close()

def clear_cache(cache):

    for key in cache.scan_iter():
        cache.delete(key)

def reload_cache():
    cache = redis.Redis(host='localhost', port=6379)
    clear_cache(cache)

    category_tweets = defaultdict(dict)
    company_tweets = defaultdict(dict)

    db_files = glob.glob("data/tweet_sentiment_*.db")

    for db_file in db_files:
        conn = sqlite3.connect(db_file)
        conn.row_factor = sqlite3.Row
        c = conn.cursor()
        c.execute("""
        SELECT (
            company,
            category, 
            created_at, 
            sentiment) 
        FROM tweet_sentiment
        WHERE sentiment != 0.0""")
        tweets = c.fetchall()
        for tweet in tweets:
            dt = datetime.fromtimestamp(tweet['created_at'])
            ymd = dt.strftime("%Y-%m-%d")
            cat_sentiment, cat_count = category_tweets[tweet['category']].get(ymd, (0,0))
            category_tweets[tweet['category']][ymd] = cat_sentiment+tweet['sentiment'], cat_count+1
            cmp_sentiment, cmp_count = company_tweets[tweet['company']].get(ymd, (0,0))
            company_tweets[tweet['company']][ymd] = cmp_sentiment+tweet['sentiment'], cmp_count+1

        conn.close()














