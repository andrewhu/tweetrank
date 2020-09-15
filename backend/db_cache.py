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

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

def store_to_cache(tweets, company, category, cache):
    """Stores Tweet sentiments to cache.
    key -> (total_sentiment, count) """

    data = json.loads(cache.get("all") or '{}')

    if company not in data:
        data[company] = dict()

    if category not in data:
        data[category] = dict()

    # category_data = json.loads(cache.get(category) or '{}')
    # company_data = json.loads(cache.get(company) or '{}')

    for tweet in tweets:
        ymd = tweet['datetime'].strftime('%Y-%m-%d')

        total, count = data[company].get(ymd, (0,0))
        data[company][ymd] = total+tweet['sentiment'], count+1

        total, count = data[category].get(ymd, (0,0))
        data[category][ymd] = total+tweet['sentiment'], count+1

    cache.set("all", json.dumps(data))

    # cache.set(category, json.dumps(category_data))
    # cache.set(company, json.dumps(company_data))


def store_to_db(tweets, company, category):
    """Stores tweets into the database, one db file per month"""

    success_count, error_count = 0, 0

    # Group tweets by month
    tweets_by_month = defaultdict(list)
    for tweet in tweets:
        year_month = tweet['datetime'].strftime('%Y-%m')
        tweet['timestamp'] = int(tweet['datetime'].timestamp())
        tweets_by_month[year_month].append(tweet)

    # Store tweets to database
    for year_month in tweets_by_month.keys():
        db_filename = f"{DIR_PATH}/data/tweet_sentiment_{year_month}.db"

        # Create database file if it doesn't already exist
        if not os.path.exists(db_filename):
            template_filename = f"{DIR_PATH}/data/tweet_sentiment_template.db"
            copyfile(template_filename, db_filename)

        # Insert Tweets
        conn = sqlite3.connect(db_filename)
        c = conn.cursor()
        sql = """INSERT INTO tweet_sentiment(tweet_id, company, category, text, created_at, sentiment) VALUES (?,?,?,?,?,?)"""
        for tweet in tweets_by_month[year_month]:
            try:
                c.execute(sql, (tweet['id'], company, category, tweet['text'], tweet['timestamp'], tweet['sentiment']))
                success_count += 1
            except:
                error_count += 1
        conn.commit()
        conn.close()
    return {
        'success_count': success_count,
        'error_count': error_count
    }

def clear_cache(cache):
    """Deletes all keys in cache"""
    for key in cache.scan_iter():
        cache.delete(key)

def reload_cache(cache):
    """Reloads data to cache from database"""

    # Clear cache
    clear_cache(cache)

    data = defaultdict(dict)

    db_filenames = glob.glob(f"{DIR_PATH}/data/tweet_sentiment_*.db")

    # num_tweets = 0

    for db_filename in db_filenames:
        conn = sqlite3.connect(db_filename)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT company, category, created_at, sentiment FROM tweet_sentiment""")
        tweets = c.fetchall()
        # num_tweets += len(tweets)
        for tweet in tweets:
            ymd = datetime.fromtimestamp(tweet['created_at']).strftime("%Y-%m-%d")

            total, count = data[tweet['company']].get(ymd, (0,0))
            data[tweet['company']][ymd] = total+tweet['sentiment'], count+1

            total, count = data[tweet['category']].get(ymd, (0,0))
            data[tweet['category']][ymd] = total+tweet['sentiment'], count+1

        conn.close()

    cache.set("all", json.dumps(data))

def get_db_size():
    """Returns number of Tweets stored in all databases"""
    count = 0
    db_files = glob.glob("{}/data/tweet_sentiment_*.db".format(DIR_PATH))
    for db_file in db_files:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM tweet_sentiment")
        count += c.fetchone()[0]
    return count

def load_since_ids(cache):
    """Loads most recent Tweet IDs from database to cache"""
    since_ids = dict()
    db_filenames = glob.glob(os.path.join(DIR_PATH, "data/tweet_sentiment_*.db"))
    for db_filename in db_filenames:
        conn = sqlite3.connect(db_filename)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT tweet_id, company FROM tweet_sentiment""")
        rows = c.fetchall()
        for row in rows:
            tweet_id = row['tweet_id']
            company_name = row['company']
            if company_name not in since_ids:
                since_ids[company_name] = float('-inf')
            since_ids[company_name] = max(since_ids[company_name], tweet_id)

    # Store to cache
    cache.set("since_ids", json.dumps(since_ids))

    return since_ids

def get_earliest_timestamps():
    """Returns earliest Tweet timestamps for each company we have stored in the database"""
    timestamps = dict()
    db_filenames = glob.glob(os.path.join(DIR_PATH, "data/tweet_sentiment_*.db"))
    for db_filename in db_filenames:
        conn = sqlite3.connect(db_filename)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT created_at, company FROM tweet_sentiment""")
        rows = c.fetchall()
        for row in rows:
            timestamp = row['created_at']
            company_name = row['company']
            if company_name not in timestamps:
                timestamps[company_name] = float('inf')
            timestamps[company_name] = min(timestamps[company_name], timestamp)
    return timestamps


def init_cache(cache):
    reload_cache(cache)
    load_since_ids(cache)
    

# def get_since_id(company_name, cache):
#     """Returns most recent Tweet ID stored referencing the company"""
#


#
# def set_since_id(company_name, since_id):
#     """Sets most recent Tweet ID referencing company"""


