from flask import Flask
from redis import Redis


app = Flask(__name__)


@app.route("/get-hello")
def hello():
    try:
        redis_instance = Redis(host='redis', port=6379, decode_responses=True)
        return redis_instance.get('testing_key')
    except Exception as e:
        return str(e)


@app.route("/ping")
def ping():
    return "pong"

if __name__ == "__main__":
    app.run('0.0.0.0', port=8000)
