"""
Methods for fetching tweets from the Twitter API
"""

import datetime
import json
import redis
import requests
import time

import accounts
import config


def fetch_recent_tweets(query, start_time=None, end_time=None, max_results=100):
    """Fetches recent Tweets (up to past 7 days) from the Twitter API v2"""
    search_endpoint = "https://api.twitter.com/2/tweets/search/recent"
    headers = {
        'content-type': 'application/json',
        'authorization': 'Bearer {}'.format(config.TWITTER_BEARER_TOKEN)
    }
    params = {
        'query': '{} lang:en'.format(query),
        'max_results': max_results,
        'tweet.fields': 'created_at,entities'
    }
    if start_time:
        params['start_time'] = start_time
    if end_time:
        params['end_time'] = end_time
    r = requests.get(search_endpoint, headers=headers, params=params)
    return r.json()

def next_fetch_interval(minutes_ago=5):
    """Returns the next time interval to fetch Tweets from"""
    cache = redis.Redis(host='localhost', port=6379)
    req_time_format = '%Y-%m-%dT%H:%M:00Z'
    end = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
    end_time = end.strftime(req_time_format)
    start_time = cache.get('last_fetch_time')
    if start_time is None:
        start = end - datetime.timedelta(minutes=minutes_ago)
        start.strftime(req_time_format)
    cache.set('last_fetch_time', end_time)
    return start_time, end_time

def process_tweets(tweets):
    """Calculates sentiment and reformats time"""
    

if __name__ == "__main__":

    start_time, end_time = next_fetch_interval()

    # Fetch ISP tweets
    isp_tweets = dict()
    for isp in accounts.ISPs:
        query = ' OR '.join([account['handle'] for account in isp['accounts']])
        recent_tweets = fetch_recent_tweets(query, start_time, end_time)

















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





