import os
import tweepy as tw

api_key = '7vesX9myLzoksEZv3FQpn5W6A'
api_secret = 'PrmccmOuZiblexYKhVoT3Uf2uHlpfGnSWMpECh2dvQqxfFZIcb'
access_token = '594435039-ywwbbW3e5X9jVvYmqcXH1HL2GG7JoYE9XCqPMkKQ'
access_token_secret = 'cRanZpNrGwsmKyiUBYqMYambl2BByrjnT0LLcmQIBJR4u'

auth = tw.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

search_words = "#blm"
date_since = "2020-06-24"

# Collect tweets
tweets = tw.Cursor(api.search,
              q=search_words,
              lang="en",
              since=date_since).items(5)

# Iterate and print tweets
for tweet in tweets:
    print(tweet.text)