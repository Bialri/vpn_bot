import pika
import time
from wireguard_manager import WGManager
from pathlib import Path
from schemas import ChangeStateMessage
from wireguard_server.src.config import DEFAULT_NETWORK_PREFIX

CONFIG_DIR = Path('/etc/wireguard/')
manager = WGManager(DEFAULT_NETWORK_PREFIX, CONFIG_DIR)


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
            match message.status:
                case 'stopped':
                    interface.stop_interface()
                case 'absent':
                    manager.delete_interface(interface)


def main():
    parametrs = pika.URLParameters('amqp://ID:egor0123@172.26.96.1:5672/')
    connection = pika.BlockingConnection(parametrs)
    while(1):
        try:
            channel = connection.channel()
            print('Connection established')
            break
        except RuntimeError as e:
            print('Connection not established, trying in 5 seconds...')
            time.sleep(5)

    channel.basic_consume('demo', on_message)
    try:
        print('Waiting for messages.')
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()
        print('Connection closed')


if __name__ == '__main__':
    main()