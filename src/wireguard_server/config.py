from dotenv import load_dotenv
import os

load_dotenv()

rmq_host = os.environ.get('RMQ_HOST')
rmq_port = os.environ.get('RMQ_PORT')
rmq_user = os.environ.get('RMQ_USER')
rmq_password = os.environ.get('RMQ_PASSWORD')
rmq_vhost = os.environ.get('RMQ_VHOST')
rmq_url = f'amqp://{rmq_user}:{rmq_password}@{rmq_host}:{rmq_port}/{rmq_vhost}'