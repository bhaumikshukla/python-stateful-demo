import pymysql
from flask import jsonify, make_response
from flask import flash, request
from flaskext.mysql import MySQL
from flask import jsonify
from flask import flash, request

from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics
import logging
import sys
import json_logging
import json
import os
import datetime

# checking the port mentioned in env, if not then let's exit
if os.environ.get("SERVE_PORT") == None or os.environ.get("MYSQL_SERVICE_HOST") == None or os.environ.get("DB_PW") == None:
    print("Environment variable SERVE_PORT or MYSQL_SERVICE_HOST or DB_PW is not defined. Exiting.")
    exit()

app = Flask(__name__)

# logging
json_logging.init_flask(enable_json=True)
json_logging.init_request_instrument(app)
# Init logger
logger = logging.getLogger("test-logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

# For collecting metrics from flask to prometheus
metrics = PrometheusMetrics(app)


mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ.get("DB_PW")
app.config['MYSQL_DATABASE_DB'] = 'new_schema'
app.config['MYSQL_DATABASE_HOST'] = os.environ.get("MYSQL_SERVICE_HOST")
mysql.init_app(app)

'''
Status
'''
STATUS_PROCESSING = 1
STATUS_COMPLETED = 2
STATUS_FAILED = -1

MAX_TRANSACTION_AMOUNT = 0


@app.route('/getall')
def getall():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM sample")
        rows = cursor.fetchall()
        resp = jsonify(rows)
        

        resp.status_code = 200
        logger.info("Logging response", extra={
                'props': {"response": resp.json}})
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route('/starttransaction', methods=['POST'])
def starttransaction():
    body = request.get_json()
    try:
        amount = body["amount"]
        description = body["desc"]
    except Exception as e:
        resp = make_response(
                jsonify(
                    {"message": "Can not read properties 'amount' and 'desc'"}
                ),
                400,
            )
        resp.headers["Content-Type"] = "application/json"
        return resp

    
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        now = datetime.datetime.now()
        cursor.execute(""" insert into sample (amount, `desc`, ts, status) values ('%s', '%s', '%s', '%s')  """ % (amount,description, now.strftime('%Y-%m-%d %H:%M:%S'), str(STATUS_PROCESSING)   )) 
        conn.commit()
        newid = cursor.lastrowid

        global MAX_TRANSACTION_AMOUNT
        if MAX_TRANSACTION_AMOUNT < amount:
            MAX_TRANSACTION_AMOUNT = amount

        resp = make_response(
                jsonify(
                    {"message": "Transaction is under progress" , "transaction_id": newid}
                ),
                200,
            )
        resp.headers["Content-Type"] = "application/json"
        
        logger.info("Logging response", extra={
                'props': {"response": resp.json}})
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

'''
This will return Max transaction. This data is in-memory. Gets vanished everytime server restarts.
Sample usecase to demonstrate the statefulness of the application.
'''
@app.route('/maxtrans')
def getmaxtran():
    resp = make_response(
                jsonify(
                    {"message": "Maximum transaction amount in this session. This will get reset to 0 on application restart." , "amount": MAX_TRANSACTION_AMOUNT}
                ),
                200,
            )
    resp.headers["Content-Type"] = "application/json"
        
    logger.info("Logging response", extra={
                'props': {"response": resp.json}})
    return resp


@app.route('/complete', methods=['POST'])
def complete():
    body = request.get_json()
    try:
        rid = body["ID"]
    except Exception as e:
        resp = make_response(
                jsonify(
                    {"message": "Can not read properties 'ID'"}
                ),
                400,
            )
        resp.headers["Content-Type"] = "application/json"
        return resp

    
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute(""" UPDATE sample set status= %s  where ID = %s and status=1""" % (STATUS_COMPLETED, rid)) 
        conn.commit()
        
        resp = make_response(
                jsonify(
                    {"message": "Transaction marked as completed."}
                ),
                200,
            )
        resp.headers["Content-Type"] = "application/json"
        
        logger.info("Logging response", extra={
                'props': {"response": resp.json}})
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


if __name__ == '__main__':

    # Running the app
    app.run(host='0.0.0.0', port=os.environ.get("SERVE_PORT"))
