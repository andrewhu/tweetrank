
# import atexit
# from apscheduler.schedulers.background import BackgroundScheduler
#
# def foo():
#     pass
#
# # Create background scheduler for fetching tweets
# scheduler = BackgroundScheduler()
# scheduler.add_job(func=foo, trigger="interval", seconds=3)
# scheduler.start()
#
# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())


from flask import Flask, abort, jsonify
import json
import redis
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

cache = redis.Redis()

@app.route('/api/')
def _index():
    return "ok"

@app.route('/api/data/')
def _data():
    # Load data from cache

    data = json.loads(cache.get("all") or '{}')

    response = defaultdict(list)

    for key in data:
        for ymd in data[key]:
            total, count = data[key][ymd]
            avg = round(total/count, 4)
            timestamp = int(datetime.strptime(ymd, "%Y-%m-%d").timestamp())*1000
            response[key].append((timestamp, avg, count))
            # data[key][ymd] = (round(total/count, 4), count)
        response[key] = sorted(response[key], key=lambda x: x[0])
    return response

    # Compute average sentiment per day from (total,count) pairs
    # result = []
    # for key in data:
    #     total, count = data[key]
    #     result.append({
    #         'date': key,
    #         'avg_sentiment': round(total/count, 4),
    #         'count': count
    #     })

    # return jsonify(sorted(result, key=lambda x: x['date']))
    # print(category, company)

# @app.route('/data/company/<string:company>')
# def _company(company):
#     return 'company ok'



