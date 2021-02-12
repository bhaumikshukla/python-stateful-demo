# python-stateful-demo
This is the sample Flask based REST APIs that communicates with Mysql db.


### Prerequisites:
- Python 3 is required
- Flask 
- Mysql


## Run the application
```
pip install -r requirements.txt
```

Environment variables are required

SERVE_PORT = 8080
MYSQL_SERVICE_HOST = localhost
DB_PW = 'my-secret-pw'

```
python app.py
```


## APIs

```
curl --location --request GET 'localhost:8080/getall' \
--header 'Host: api.bshukla.com' \
--header 'Content-Type: application/json' \
--data-raw '{
    "amount": 10000, "desc":"this is sample"
}'
```


Expected response
```
```
