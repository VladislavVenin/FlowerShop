import json
import uuid

from django.conf import settings
from yookassa import Configuration, Payment
from yookassa.domain.exceptions import ApiError, BadRequestError

from .models import Order

Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def create_payment(order: Order, return_url: str = None) -> str:
    '''Создание платежа для сервиса юкасса вернет url'''

    if not return_url:
        return_url = settings.YOOKASSA_RETURN_URL

    idempotence_key = str(uuid.uuid4())
    amount = float(order.bouquet.price) if order.bouquet else 0.0
    description = f"Оплата заказанного букета №{order.id}"

    payment_data = {
        "amount": {"value": f"{amount:.2f}", "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": return_url},
        "capture": True,
        "description": description,
        "metadata": {"order_id": order.id}
    }

    try:
        payment = Payment.create(payment_data, idempotence_key)
        order.yookassa_transaction_id = payment.id
        order.save(update_fields=['yookassa_transaction_id'])
        return payment.confirmation.confirmation_url
    except (BadRequestError, ApiError):
        raise


def yookassa_webhook(request_body: bytes) -> None:
    '''Вебхук для получаения статуса платежа'''

    try:
        event_data = json.loads(request_body)

        if event_data.get('event') == 'payment.succeeded':
            payment_id = event_data.get('object', {}).get('id')
            if payment_id:
                try:
                    order = Order.objects.get(yookassa_transaction_id=payment_id)
                    order.payment_status = 'paid'
                    order.save(update_fields=['payment_status'])
                except Order.DoesNotExist:
                    pass

        elif event_data.get('event') == 'payment.canceled':
            payment_id = event_data.get('object', {}).get('id')
            if payment_id:
                try:
                    order = Order.objects.get(yookassa_transaction_id=payment_id)
                    order.payment_status = 'failed'
                    order.save(update_fields=['payment_status'])
                except Order.DoesNotExist:
                    pass

    except json.JSONDecodeError:
        pass
    except Exception:
        raise
