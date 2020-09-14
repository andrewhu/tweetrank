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

    category_data = json.loads(cache.get(category) or '{}')
    company_data = json.loads(cache.get(company) or '{}')

    for tweet in tweets:
        ymd = tweet['datetime'].strftime('%Y-%m-%d')

        total, count = category_data.get(ymd, (0,0))
        category_data[ymd] = total+tweet['sentiment'], count+1

        total, count = company_data.get(ymd, (0,0))
        company_data[ymd] = total+tweet['sentiment'], count+1

    cache.set(category, json.dumps(category_data))
    cache.set(company, json.dumps(company_data))


def store_to_db(tweets, company, category):
    """Stores tweets into the database, one db file per month"""

    success_count, error_count = 0, 0

    # Group tweets by month
    tweets_by_month = defaultdict(list)
    for tweet in tweets:
        year_month = tweet['datetime'].strftime('%Y-%m')
        tweet['timestamp'] = int(tweet['datetime'].timestamp())
        tweets_by_month[year_month].append(tweet)

    for year_month in tweets_by_month.keys():
        db_filename = f"{DIR_PATH}/data/tweet_sentiment_{year_month}.db"

        # Create database file if it doesn't already exist
        if not os.path.exists(db_filename):
            template_filename = f"{DIR_PATH}/data/templates/tweet_sentiment_template.db"
            copyfile(template_filename, db_filename)

        # Insert Tweets into database
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

    category_tweets = defaultdict(dict)
    company_tweets = defaultdict(dict)

    db_filenames = glob.glob("{}/data/tweet_sentiment_*.db".format(DIR_PATH))

    # num_tweets = 0

    for db_filename in db_filenames:
        conn = sqlite3.connect(db_filename)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT (company, category, created_at, sentiment) FROM tweet_sentiment""")
        tweets = c.fetchall()
        # num_tweets += len(tweets)
        for tweet in tweets:
            ymd = datetime.fromtimestamp(tweet['created_at']).strftime("%Y-%m-%d")

            total, count = category_tweets[tweet['category']].get(ymd, (0,0))
            category_tweets[tweet['category']][ymd] = total+tweet['sentiment'], count+1

            total, count = company_tweets[tweet['company']].get(ymd, (0,0))
            company_tweets[tweet['company']][ymd] = total+tweet['sentiment'], count+1

        conn.close()

    for category_name in category_tweets.keys():
        cache.set(category_name, json.dumps(category_tweets[category_name]))
    for company_name in company_tweets.keys():
        cache.set(company_name, json.dumps(company_tweets[company_name]))

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


# def get_since_id(company_name, cache):
#     """Returns most recent Tweet ID stored referencing the company"""
#


#
# def set_since_id(company_name, since_id):
#     """Sets most recent Tweet ID referencing company"""


