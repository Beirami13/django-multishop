from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from account.models import Address
from product.models import Product
from .cart_modules import Cart
from .forms import CheckoutForm
from .models import Discount, Order
from .services import (
    InvalidDiscount, OutOfStock, calculate_discount, cancel_order, create_order,
)
from .zarinpal import ZarinPal

pay = ZarinPal(
    merchant=settings.ZARINPAL_MERCHANT,
    call_back_url=settings.ZARINPAL_CALLBACK_URL,
)


def parse_quantity(value, default=1):
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return default


def get_applied_discount(request):
    name = request.session.get('discount_code')
    if not name:
        return None
    return Discount.objects.filter(name=name, quantity__gt=0).first()


def finish_cart(request):
    Cart(request).remove_cart()
    request.session.pop('discount_code', None)


class CartView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = Cart(request)
        subtotal = cart_items.total()
        discount_amount = calculate_discount(subtotal, get_applied_discount(request))

        return render(request, 'cart/cart.html', {
            'cart_items': cart_items,
            'discount_amount': discount_amount,
            'total_price': subtotal - discount_amount,
        })


class CartAddView(LoginRequiredMixin, View):
    def post(self, request):
        product = get_object_or_404(Product, id=request.POST.get('product_id'))
        Cart(request).add(
            product,
            parse_quantity(request.POST.get('quantity')),
            request.POST.get('color', ''),
            request.POST.get('size', ''),
        )
        return redirect('cart:cart')


class CartRemoveView(LoginRequiredMixin, View):
    def post(self, request, id):
        Cart(request).remove(id)
        return redirect('cart:cart')


class CartUpdateView(LoginRequiredMixin, View):
    def post(self, request):
        Cart(request).update(
            request.POST.get('unique_id'),
            parse_quantity(request.POST.get('quantity')),
        )
        return redirect('cart:cart')


class DiscountCheckView(LoginRequiredMixin, View):
    def post(self, request):
        name = request.POST.get('discount', '').strip()
        discount = Discount.objects.filter(name=name, quantity__gt=0).first()

        if discount:
            request.session['discount_code'] = discount.name
            messages.success(request, 'Discount code applied.')
        else:
            request.session.pop('discount_code', None)
            messages.error(request, 'Invalid or expired discount code.')

        return redirect('cart:cart')


def render_checkout(request, cart, form):
    shipping = settings.SHIPPING_COST
    subtotal = cart.total()
    discount_amount = calculate_discount(subtotal, get_applied_discount(request))

    return render(request, 'cart/order_detail.html', {
        'cart_items': cart,
        'addresses': Address.objects.filter(user=request.user),
        'form': form,
        'shipping': shipping,
        'discount_amount': discount_amount,
        'grand_total': subtotal - discount_amount + shipping,
    })


class OrderCreationView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        if not list(cart):
            return redirect('cart:cart')
        return render_checkout(request, cart, CheckoutForm(request.user))

    def post(self, request):
        cart = Cart(request)
        items = list(cart)
        if not items:
            return redirect('cart:cart')

        form = CheckoutForm(request.user, request.POST)
        if not form.is_valid():
            return render_checkout(request, cart, form)

        data = form.cleaned_data

        try:
            order = create_order(request.user, items, data, get_applied_discount(request))
        except OutOfStock as e:
            form.add_error(None, f'Not enough stock for: {e}')
            return render_checkout(request, cart, form)
        except InvalidDiscount:
            request.session.pop('discount_code', None)
            form.add_error(None, 'This discount code is no longer valid.')
            return render_checkout(request, cart, form)

        # Cash on delivery: the order is final, empty the cart.
        if data['payment_method'] == 'cash':
            finish_cart(request)
            messages.success(request, 'Your order has been placed successfully.')
            return redirect('cart:order-detail', id=order.id)

        # Online payment: the order exists but is unpaid until verify() runs.
        request.session['pending_order_id'] = order.id

        response = pay.send_request(
            amount=int(order.total_price),
            description=f'Order #{order.id}',
            email=data.get('email') or '',
            mobile=data['phone_number'],
        )

        if response.get('error_code') is None:
            return response

        cancel_order(order)
        request.session.pop('pending_order_id', None)
        form.add_error(None, f"Payment error: {response.get('message')}")
        return render_checkout(request, cart, form)


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, id):
        order = get_object_or_404(
            Order.objects.prefetch_related('orderitem_set__product'),
            id=id,
            user=request.user,
        )
        return render(request, 'cart/order_detail.html', {'order': order})


@login_required
def verify(request):
    order_id = request.session.get('pending_order_id')
    order = Order.objects.filter(pk=order_id, user=request.user).first() if order_id else None

    if order is None:
        return HttpResponse('No pending order found.')

    if order.is_paid:
        return redirect('cart:order-detail', id=order.id)

    response = pay.verify(request=request, amount=int(order.total_price))

    if response.get('transaction') and response.get('pay'):
        order.is_paid = True
        order.status = 'processing'
        order.save(update_fields=['is_paid', 'status'])

        request.session.pop('pending_order_id', None)
        finish_cart(request)
        messages.success(request, 'Your payment was successful and your order has been placed.')
        return redirect('cart:order-detail', id=order.id)

    cancel_order(order)
    request.session.pop('pending_order_id', None)
    return render(request, 'cart/order_failed.html', {
        'message': 'Your payment was cancelled or failed. Your order was not placed.'
    })