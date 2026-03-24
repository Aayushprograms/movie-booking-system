import razorpay
from django.conf import settings

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

def create_payment_order(amount, receipt_id):
    order = client.order.create({
        "amount": amount * 100,
        "currency": "INR",
        "receipt": receipt_id,
        "payment_capture": 1
    })
    return order