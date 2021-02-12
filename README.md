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


### APIs

### Start transaction 
POST - /starttransaction

example
```
curl --location --request POST 'localhost:8080/starttransaction' \
--header 'Host: api.bshukla.com' \
--header 'Content-Type: application/json' \
--data-raw '{
    "amount": 1, "desc":"this is sample"
}'
```


Expected response
```
{
    "message": "<Message from the server>",
    "transaction_id": <transaction_id>
}
```


GET - /getall

example
```
curl --location --request GET 'localhost:8080/getall'
```


Expected response - Example
```
[
    {
        "ID": 1,
        "amount": 400,
        "desc": "it's all about test",
        "status": 1,
        "ts": "Thu, 11 Feb 2021 03:44:38 GMT"
    },
    {
        "ID": 2,
        "amount": 200,
        "desc": "it's all about test",
        "status": 1,
        "ts": "Thu, 11 Feb 2021 03:44:42 GMT"
    },
    {
        "ID": 3,
        "amount": 300,
        "desc": "it's all about test",
        "status": 1,
        "ts": "Thu, 11 Feb 2021 03:44:46 GMT"
    },
    {
        "ID": 4,
        "amount": 300,
        "desc": "it's all about test",
        "status": 1,
        "ts": "Thu, 11 Feb 2021 17:18:42 GMT"
    }
]
```

### Complete the transaction (Only marks the transaction complete if the ID is available)

POST - /complete

```curl --location --request POST 'localhost:8080/complete' \
--header 'Host: api.bshukla.com' \
--header 'Content-Type: application/json' \
--data-raw '{
    "ID": 37
}'
```

Sample response
```
{
    "message": "Transaction marked as completed."
}
```

### Fetch the maximum transaction amount in the current session. 
On restart of the application it will reset to 0. This is to demonstrate the statefulness of the application.

GET  - /maxtrans

```
curl --location --request GET 'localhost:8080/maxtrans'
```

Sample response
```
{
    "amount": 1,
    "message": "Maximum transaction amount in this session. This will get reset to 0 on application restart."
}
```

