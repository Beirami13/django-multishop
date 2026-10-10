from django.conf import settings
from django.db import transaction
from django.db.models import F

from product.models import Product
from .models import Discount, Order, OrderItem


class OutOfStock(Exception):
    pass


class InvalidDiscount(Exception):
    pass


def calculate_discount(subtotal, discount):
    """discount.discount is a percentage."""
    if not discount:
        return 0
    return subtotal * discount.discount // 100


def create_order(user, items, data, discount=None):
    """items: list(cart). data: cleaned_data of CheckoutForm."""
    with transaction.atomic():
        locked = {
            p.id: p
            for p in Product.objects.select_for_update().filter(id__in=[i['id'] for i in items])
        }
        for i in items:
            if locked[i['id']].stock < i['quantity']:
                raise OutOfStock(locked[i['id']].name)

        subtotal = sum(i['total'] for i in items)

        discount_amount = 0
        if discount:
            valid = Discount.objects.select_for_update().filter(
                pk=discount.pk, quantity__gt=0,
            ).first()
            if valid is None:
                raise InvalidDiscount()
            discount_amount = calculate_discount(subtotal, valid)
            Discount.objects.filter(pk=valid.pk).update(quantity=F('quantity') - 1)

        address = data['address']

        order = Order.objects.create(
            user=user,
            address=address,
            shipping_address=f"{address.city} - {address.address} - {address.zip_code}",
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data['phone_number'],
            email=data.get('email') or None,
            payment_method=data['payment_method'],
            subtotal=subtotal,
            discount_amount=discount_amount,
            total_price=subtotal - discount_amount + settings.SHIPPING_COST,
        )

        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=i['product'],
                quantity=i['quantity'],
                price=i['product'].price,
                size=i['size'],
                color=i['color'],
            )
            for i in items
        ])

        for i in items:
            Product.objects.filter(pk=i['id']).update(stock=F('stock') - i['quantity'])

    return order


def cancel_order(order):
    """Cancel an unpaid order and give the stock back."""
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        if order.is_paid or order.status == 'cancelled':
            return
        for item in order.orderitem_set.all():
            Product.objects.filter(pk=item.product_id).update(
                stock=F('stock') + item.quantity
            )
        order.status = 'cancelled'
        order.save(update_fields=['status'])