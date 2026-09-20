from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from account.models import Address
from product.models import Product

from .cart_modules import Cart
from .models import Order, OrderItem, Discount
from .zarinpal import ZarinPal


class CartView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = Cart(request)

        discount_amount = request.session.get('discount_amount', 0)

        total_price = request.session.get(
            'total_price',
            cart_items.total()
        )

        return render(
            request,
            "cart/cart.html",
            {
                'cart_items': cart_items,
                'discount_amount': discount_amount,
                'total_price': total_price,
            }
        )


class CartAddView(LoginRequiredMixin, View):
    def post(self, request):
        product = get_object_or_404(
            Product,
            id=request.POST['product_id']
        )

        size = request.POST['size']
        color = request.POST['color']
        quantity = request.POST['quantity']

        cart_items = Cart(request)
        cart_items.add(product, quantity, color, size)

        return redirect('cart:cart')


class CartRemoveView(LoginRequiredMixin, View):
    def get(self, request, id):
        cart = Cart(request)
        cart.remove(id)

        return redirect('cart:cart')


class CartUpdateView(LoginRequiredMixin, View):
    def post(self, request):
        unique_id = request.POST['unique_id']
        quantity = request.POST['quantity']

        cart = Cart(request)
        cart.update(unique_id, quantity)

        return redirect('cart:cart')


class OrderCreationView(LoginRequiredMixin, View):

    def get(self, request):
        cart = Cart(request)
        addresses = Address.objects.filter(user=request.user)

        return render(
            request,
            'cart/order_detail.html',
            {
                'cart_items': cart,
                'addresses': addresses
            }
        )

    def post(self, request):

        cart = Cart(request)

        address = get_object_or_404(
            Address,
            id=request.POST['address'],
            user=request.user
        )

        subtotal = cart.total()

        discount_amount = request.session.get(
            'discount_amount',
            0
        )

        total_price = subtotal - discount_amount

        payment_method = request.POST['payment_method']


        # -------------------------
        # Cash Payment
        # -------------------------

        if payment_method == 'cash':

            order = Order.objects.create(
                user=request.user,
                address=address,
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                phone_number=request.POST['phone_number'],
                email=request.POST.get('email', ''),
                payment_method='cash',
                subtotal=subtotal,
                discount_amount=discount_amount,
                total_price=total_price,
                is_paid=False,
            )

            for item in cart:

                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['product'].price,
                    color=item['color'],
                    quantity=item['quantity'],
                    size=item['size'],
                )

            cart.remove_cart()

            return render(
                request,
                'cart/order_success.html',
                {
                    'message': 'Your order has been placed successfully.'
                }
            )


        # -------------------------
        # Online Payment
        # -------------------------

        if payment_method == 'online':

            # اطلاعات سفارش را موقتاً در session نگه می‌داریم
            request.session['pending_order'] = {
                'address': address.id,
                'first_name': request.POST['first_name'],
                'last_name': request.POST['last_name'],
                'phone_number': request.POST['phone_number'],
                'email': request.POST.get('email', ''),
                'subtotal': float(subtotal),
                'discount_amount': float(discount_amount),
                'total_price': float(total_price),
            }

            request.session.modified = True


            response = pay.send_request(
                amount=int(total_price),
                description='Online payment for order',
                email=request.POST.get('email', ''),
                mobile=request.POST['phone_number']
            )

            if response.get('error_code') is None:

                return response

            else:

                return HttpResponse(
                    f"Payment error: {response.get('message')}"
                )


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, id):

        order = get_object_or_404(
            Order,
            id=id,
            user=request.user
        )

        return render(
            request,
            'cart/order_detail.html',
            {
                'order': order
            }
        )


class DiscountCheckView(LoginRequiredMixin, View):
    def post(self, request):

        cart = Cart(request)

        discount_name = request.POST['discount']

        discount_code = get_object_or_404(
            Discount,
            name=discount_name
        )

        if discount_code.quantity == 0:
            return redirect('cart:cart')

        subtotal = cart.total()

        discount_amount = (
            subtotal * discount_code.discount / 100
        )

        total_price = subtotal - discount_amount

        request.session['discount_amount'] = float(
            discount_amount
        )

        request.session['total_price'] = float(
            total_price
        )

        request.session['discount_name'] = (
            discount_code.name
        )

        request.session.modified = True

        return redirect('cart:cart')


# -------------------------
# ZarinPal
# -------------------------

pay = ZarinPal(
    merchant='xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
    call_back_url='http://localhost:8000/verify/'
)


def send_request(request):

    response = pay.send_request(
        amount='1000',
        description='Payment description',
        email='Example@test.com',
        mobile='09123456789'
    )

    if response.get('error_code') is None:

        return response

    else:

        return HttpResponse(
            f"Error code: {response.get('error_code')}, "
            f"Error Message: {response.get('message')}"
        )


def verify(request):

    pending_order = request.session.get('pending_order')

    if not pending_order:
        return HttpResponse(
            'No pending order found.'
        )


    response = pay.verify(
        request=request,
        amount=int(pending_order['total_price'])
    )


    # -------------------------
    # Payment Successful
    # -------------------------

    if response.get('transaction') and response.get('pay'):

        address = get_object_or_404(
            Address,
            id=pending_order['address'],
            user=request.user
        )

        order = Order.objects.create(
            user=request.user,
            address=address,
            first_name=pending_order['first_name'],
            last_name=pending_order['last_name'],
            phone_number=pending_order['phone_number'],
            email=pending_order['email'],
            payment_method='online',
            subtotal=pending_order['subtotal'],
            discount_amount=pending_order['discount_amount'],
            total_price=pending_order['total_price'],
            is_paid=True,
        )


        # ساختن OrderItem ها
        cart = Cart(request)

        for item in cart:

            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['product'].price,
                color=item['color'],
                quantity=item['quantity'],
                size=item['size'],
            )


        # پاک کردن Cart
        cart.remove_cart()


        # پاک کردن اطلاعات موقت سفارش
        request.session.pop('pending_order', None)
        request.session.pop('discount_amount', None)
        request.session.pop('total_price', None)
        request.session.pop('discount_name', None)


        return render(
            request,
            'cart/order_success.html',
            {
                'message': 'Your payment was successful and your order has been placed.'
            }
        )


    # -------------------------
    # Payment Failed / Cancelled
    # -------------------------

    else:

        request.session.pop('pending_order', None)

        return render(
            request,
            'cart/order_failed.html',
            {
                'message': 'Your payment was cancelled or failed. Your order was not placed.'
            }
        )