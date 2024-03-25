import uuid

import yookassa
import asyncio

yookassa.Configuration.account_id = 347553
yookassa.Configuration.secret_key = 'test_UPurEZyrtQ77_YCHz8gn7XrQiyzrHtKwvrWKoQgvaX4'


def create_payment_subscription(title, amount):
    subscription = yookassa.Payment.create({
        'amount': {
            'value': amount,
            'currency': 'RUB'
        },
        'confirmation': {
            'type': 'redirect',
            'return_url': 'https://t.me/DhoineBot'
        },
        'description': title,
        'capture': False
    })
    return subscription.confirmation.confirmation_url, subscription


async def check_payment_subscription(payment_id):
    payment = yookassa.Payment.find_one(payment_id)

    while payment.status == 'pending':
        await asyncio.sleep(4)
        payment = yookassa.Payment.find_one(payment_id)
    return payment.status == "waiting_for_capture"


def refund_payment(payment_id):
    uid = str(uuid.uuid4())
    yookassa.Payment.cancel(payment_id, uid)


def capture_payment(payment_id):
    yookassa.Payment.capture(payment_id)
