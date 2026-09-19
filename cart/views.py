from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from account.models import Address
from .cart_modules import Cart

from product.models import Product
from .models import Order, OrderItem, Discount


class CartView(View):
    def get(self, request):
        cart_items = Cart(request)

        discount_amount = request.session.get('discount_amount', 0)
        total_price = request.session.get('total_price', cart_items.total())

        return render(request, "cart/cart.html",
            {'cart_items': cart_items,'discount_amount': discount_amount,'total_price': total_price,})


class CartAddView(View):
    def post(self, request):
        product = get_object_or_404(Product, id=request.POST['product_id'])
        size, color, quantity = request.POST['size'], request.POST['color'], request.POST['quantity']
        cart_items = Cart(request)
        cart_items.add(product, quantity, color, size)

        return redirect('cart:cart')


class CartRemoveView(View):
    def get(self, request, id):
        cart = Cart(request)
        cart.remove(id)
        return redirect('cart:cart')


class CartUpdateView(View):
    def post(self, request):
        unique_id = request.POST['unique_id']
        quantity = request.POST['quantity']

        cart = Cart(request)
        cart.update(unique_id, quantity)

        return redirect('cart:cart')


from account.models import Address


class OrderCreationView(View):
    def get(self, request):
        cart = Cart(request)
        addresses = Address.objects.filter(user=request.user)

        return render(
            request,
            'cart/order_detail.html',
            {'cart_items': cart, 'addresses': addresses}
        )

    def post(self, request):
        cart = Cart(request)
        address = get_object_or_404(Address, id=request.POST['address'], user=request.user)

        order = Order.objects.create(
            user=request.user,
            address=address,
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            phone_number=request.POST['phone_number'],
            email=request.POST.get('email', ''),
            payment_method=request.POST['payment_method'],
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

        return redirect('cart:order-detail', id=order.id)


class OrderDetailView(View):
    def get(self, request, id):
        order = get_object_or_404(Order, id=id)

        return render(request, 'cart/order_detail.html', {'order': order})


from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from account.models import Address
from .cart_modules import Cart
from product.models import Product
from .models import Order, OrderItem, Discount


class CartView(View):
    def get(self, request):
        cart_items = Cart(request)

        return render(
            request,
            "cart/cart.html",
            {'cart_items': cart_items}
        )


class CartAddView(View):
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


class CartRemoveView(View):
    def get(self, request, id):
        cart = Cart(request)
        cart.remove(id)

        return redirect('cart:cart')


class CartUpdateView(View):
    def post(self, request):
        unique_id = request.POST['unique_id']
        quantity = request.POST['quantity']

        cart = Cart(request)
        cart.update(unique_id, quantity)

        return redirect('cart:cart')


class OrderCreationView(View):
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

        order = Order.objects.create(
            user=request.user,
            address=address,
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            phone_number=request.POST['phone_number'],
            email=request.POST.get('email', ''),
            payment_method=request.POST['payment_method'],
            subtotal=subtotal,
            total_price=subtotal,
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

        return redirect(
            'cart:order-detail',
            id=order.id
        )


class OrderDetailView(View):
    def get(self, request, id):
        order = get_object_or_404(
            Order,
            id=id,
            user=request.user
        )

        return render(
            request,
            'cart/order_detail.html',
            {'order': order}
        )


class DiscountCheckView(View):
    def post(self, request):
        cart = Cart(request)

        discount_name = request.POST['discount']
        discount_code = get_object_or_404(Discount, name=discount_name)

        if discount_code.quantity == 0:
            return redirect('cart:cart')

        subtotal = cart.total()

        discount_amount = subtotal * discount_code.discount / 100
        total_price = subtotal - discount_amount

        request.session['discount_amount'] = float(discount_amount)
        request.session['total_price'] = float(total_price)
        request.session['discount_name'] = discount_code.name

        request.session.modified = True

        return redirect('cart:cart')
