from dotenv import load_dotenv
import os

load_dotenv()

RMQ_HOST = os.environ.get('RMQ_HOST')
RMQ_PORT = os.environ.get('RMQ_PORT')
RMQ_USER = os.environ.get('RMQ_USER')
RMQ_PASSWORD = os.environ.get('RMQ_PASSWORD')
RQM_VHOST = os.environ.get('RMQ_VHOST')
RMQ_URL = f'amqp://{RMQ_USER}:{RMQ_PASSWORD}@{RMQ_HOST}:{RMQ_PORT}/{RQM_VHOST}'

SERVER_ENDPOINT = os.environ.get('SERVER_ENDPOINT')
DEFAULT_NETWORK_PREFIX = os.environ.get('DEFAULT_NETWORK_PREFIX')
