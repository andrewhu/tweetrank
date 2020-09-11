
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


from flask import Flask

app = Flask(__name__)

@app.route('/data/category/<string:category>')
def _category(category):
    return 'category ok'
    # print(category, company)

@app.route('/data/company/<string:company>')
def _company(company):
    return 'company ok'



