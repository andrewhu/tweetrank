
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


from flask import Flask, abort
import json
import redis

app = Flask(__name__)

@app.route('/data/<string:name>')
def _data(name):
    # Load data from cache
    cache = redis.Redis()
    data = cache.get(name)
    if data is None:
        abort(500)
    data = json.loads(data)

    # Compute average sentiment per day from (total,count) pairs
    avg_sent = dict()
    for key in data:
        total, count = data[key]
        avg_sent[key] = round(total/count, 4)
    return avg_sent
    # print(category, company)

# @app.route('/data/company/<string:company>')
# def _company(company):
#     return 'company ok'



