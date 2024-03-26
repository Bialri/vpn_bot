import sqlalchemy
import dotenv
import os
import pika
import json

dotenv.load_dotenv()

if __name__ == '__main__':
    engine = sqlalchemy.create_engine(os.getenv('DB_URI'))
    pika_parameters = pika.URLParameters(os.environ.get("RMQ_URL"))
    connection = pika.BlockingConnection(pika_parameters)
    channel = connection.channel()

    with engine.connect() as conn:
        cur = conn.exec_driver_sql('''SELECT interface.interface_name, servers.address from vpn_interfaces as interface
         join "user" as u on u.id = interface.owner_id
         join vpn_servers as servers on servers.id = interface.server_id
         WHERE u.subscription_till < CURRENT_DATE''')

        rows = cur.fetchall()
        for row in rows:
            interface_name = row[0]
            address = row[1]
            query = {
                'interface': f'{interface_name}',
                'status': "stopped"
            }
            channel.basic_publish(exchange='route',
                                  routing_key=address,
                                  body=json.dumps(query))

        сur = conn.exec_driver_sql('''SELECT interface.interface_name, servers.address from vpn_interfaces as interface
         join "user" as u on u.id = interface.owner_id
         join vpn_servers as servers on servers.id = interface.server_id
         WHERE u.subscription_till < CURRENT_DATE - INTERVAL '3' MONTH''')

        rows = cur.fetchall()
        for row in rows:
            interface_name = row[0]
            address = row[1]
            query = {
                'interface': f'{interface_name}',
                'status': "absent"
            }
            channel.basic_publish(exchange='route',
                                  routing_key=address,
                                  body=json.dumps(query))