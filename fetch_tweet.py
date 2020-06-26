import os
import tweepy as tw

'''
import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
'''


def fetch_tweet():
    api_key = '7vesX9myLzoksEZv3FQpn5W6A'
    api_secret = 'PrmccmOuZiblexYKhVoT3Uf2uHlpfGnSWMpECh2dvQqxfFZIcb'
    access_token = '594435039-ywwbbW3e5X9jVvYmqcXH1HL2GG7JoYE9XCqPMkKQ'
    access_token_secret = 'cRanZpNrGwsmKyiUBYqMYambl2BByrjnT0LLcmQIBJR4u'

    auth = tw.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)
    
    users = ["@dominos", "@ChickfilA"]
    date_since = "2020-06-24"
    
    for username in users:
        tweets = tw.Cursor(api.search,
                  q=f"from:{username}",
                  lang="en",
                  tweet_mode='extended',
                  since=date_since).items(1)
        for tweet in tweets:
            print(tweet.full_text)


if __name__ == '__main__':
    #create_connection("tweet.db")
    fetch_tweet()