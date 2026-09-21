from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from product.models import Product
from .models import Wishlist


@method_decorator(login_required, name='dispatch')
class WishlistAddView(View):
    def post(self, request):
        product = get_object_or_404(Product, id=request.POST['product_id'])

        existing = Wishlist.objects.filter(user=request.user, product=product).first()

        if existing:
            existing.delete()
        else:
            Wishlist.objects.create(user=request.user, product=product)

        return redirect(request.META.get('HTTP_REFERER', '/'))


@method_decorator(login_required, name='dispatch')
class WishlistView(View):
    def get(self, request):
        wishlist_items = Wishlist.objects.filter(user=request.user)
        return render(request, 'wishlist/wishlist.html', {'wishlist_items': wishlist_items})


@method_decorator(login_required, name='dispatch')
class WishlistRemoveView(View):
    def get(self, request, id):
        Wishlist.objects.filter(user=request.user, product_id=id).delete()
        return redirect('wish:wishlist')