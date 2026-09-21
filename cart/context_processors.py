from .cart_modules import Cart


def cart_count(request):
    cart = Cart(request)
    return {'cart_count': cart.count()}