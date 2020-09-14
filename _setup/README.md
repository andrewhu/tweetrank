


## Database Schema
```
CREATE TABLE tweet_sentiment (
    tweet_id INTEGER,
    company TEXT,
    category TEXT,
    text TEXT,
    created_at INTEGER,
    sentiment REAL,
    PRIMARY KEY (tweet_id, company)
);
```
Note: It may be useful to create a separate database ignoring text if you plan to share the data (Twitter TOS) or if the
      database files are getting too large.