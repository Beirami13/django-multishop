from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .cart_modules import Cart

from product.models import Product


class CartView(View):
    def get(self,request):
        cart_items = Cart(request)
        return render(request, "cart/cart.html", {'cart_items': cart_items})

class CartAddView(View):
    def post(self,request):
        product = get_object_or_404(Product, id=request.POST['product_id'])
        size , color , quantity = request.POST['size'], request.POST['color'], request.POST['quantity']
        cart_items = Cart(request)
        cart_items.add(product, quantity, color , size)


        return redirect('cart:cart')


class CartRemoveView(View):
    def get(self,request, id):
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