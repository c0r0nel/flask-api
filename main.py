from flask import Flask, jsonify, request, abort
from prometheus_client import start_http_server, Counter, Gauge, generate_latest
import redis
import os
import time

# Take some values form the environment
API_KEY = os.getenv("API_KEY")  # Set API_KEY in environment variables
REDIS_HOST = os.getenv("REDIS_HOST")  # Set REDIS_HOST in environment variables

# Initialize Flask app and Redis client
app = Flask(__name__)
r = redis.StrictRedis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

# Queue name (you can change it to any other name)
QUEUE_NAME = 'message_queue'

# Create Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total number of HTTP requests', ['method', 'endpoint', 'status'])
QUEUE_LENGTH = Gauge('queue_length', 'Number of messages in the queue')

# Middleware to check for API key in each request
def require_api_key():
    api_key = request.headers.get('API-Key')
    if not api_key or api_key != API_KEY:
        abort(403, description="Forbidden: Invalid API Key")

# Add authentication check to each endpoint
@app.before_request
def before_request():
    require_api_key()

# Increment request count metric
def record_request(endpoint, method, status_code):
    REQUEST_COUNT.labels(endpoint=endpoint, method=method, status=status_code).inc()

# Endpoint to pop a message from the queue
@app.route('/api/queue/pop', methods=['POST'])
def pop_message():
    start_time = time.time()
    
    msg = r.lpop(QUEUE_NAME)  # Pop the leftmost item from the list (queue)
    if msg:
        status_code = 200
        response = jsonify({'status': 'ok', 'message': msg})
    else:
        status_code = 400
        response = jsonify({'status': 'error', 'message': 'Queue is empty'})

    # Record metrics
    record_request('/api/queue/pop', 'POST', status_code)
    QUEUE_LENGTH.set(r.llen(QUEUE_NAME))  # Update queue length
    response.headers['X-Request-Time'] = str(time.time() - start_time)  # Record request time
    
    return response, status_code

@app.route('/api/queue/push', methods=['POST'])
def push_message():
    start_time = time.time()

    data = request.get_json()
    msg = data.get('message')
    if msg:
        r.rpush(QUEUE_NAME, msg)
        status_code = 200
        response = jsonify({'status': 'ok'})
    else:
        status_code = 400
        response = jsonify({'status': 'error', 'message': 'No message provided'})

    # Record metrics
    record_request('/api/queue/push', 'POST', status_code)
    QUEUE_LENGTH.set(r.llen(QUEUE_NAME))
    response.headers['X-Request-Time'] = str(time.time() - start_time)
    
    return response, status_code

@app.route('/api/queue/count', methods=['GET'])
def count_messages():
    start_time = time.time()

    count = r.llen(QUEUE_NAME)
    status_code = 200
    response = jsonify({'status': 'ok', 'count': count})

    record_request('/api/queue/count', 'GET', status_code)
    QUEUE_LENGTH.set(count)
    response.headers['X-Request-Time'] = str(time.time() - start_time)
    
    return response, status_code

@app.route('/api/queue/health', methods=['GET'])
def health_check():
    start_time = time.time()

    try:
        if r.ping():
            status_code = 200
            response = jsonify({'status': 'ok', 'message': 'Redis server is healthy'})
        else:
            status_code = 500
            response = jsonify({'status': 'error', 'message': 'Redis server is not responding'})
    except redis.ConnectionError:
        status_code = 500
        response = jsonify({'status': 'error', 'message': 'Unable to connect to Redis server'})

    record_request('/api/queue/health', 'GET', status_code)
    response.headers['X-Request-Time'] = str(time.time() - start_time)
    
    return response, status_code

@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200

@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({'status': 'error', 'message': error.description}), 403

if __name__ == '__main__':
    start_http_server(8000)
    app.run(host="0.0.0.0")
