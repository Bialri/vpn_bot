import pika
from wireguard_manager.manager import WGManager
from pathlib import Path
from schemas import ChangeStateMessage

CONFIG_DIR = Path('/etc/wireguard/')
manager = WGManager(CONFIG_DIR)


def on_message(channel, method_frame, header_frame, body):
    payload = body.decode('utf-8')
    print("Message!")
    try:
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        message = ChangeStateMessage.model_validate_json(payload)
    except ValueError:
        print('error')
        return
    interfaces = manager.interfaces
    for interface in interfaces:
        if interface.name == message.interface:
            if message.status == 'stopped':
                interface.stop_interface()


def main():
    parametrs = pika.URLParameters('amqp://ID:egor0123@172.26.96.1:5672/')
    connection = pika.BlockingConnection(parametrs)
    chanel = connection.channel()
    chanel.basic_consume('demo', on_message)
    try:
        chanel.start_consuming()
    except KeyboardInterrupt:
        chanel.stop_consuming()
        connection.close()
        print('Connection closed')


if __name__ == '__main__':
    main()