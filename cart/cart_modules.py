import product
from product.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')

        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart

    def __iter__(self):
        cart = self.cart.copy()

        for item in cart.values():
            item['product'] = Product.objects.get(id=int(item['id']))
            item['total'] = int(item['product'].price) * int(item['quantity'])
            item['unique_id'] = self.unique_id_generator(item['id'], item['color'], item['size'])
            yield item

    def unique_id_generator(self, product_id, color, size):
        result = f"{product_id}-{color}-{size}"
        return result

    def add(self, product, quantity, color, size):
        quantity = int(quantity)
        unique = self.unique_id_generator(product.id, color, size)

        if unique not in self.cart:
            self.cart[unique] = {
                'quantity': quantity,
                'size': size,
                'color': color,
                'id': product.id,
            }
        else:
            self.cart[unique]['quantity'] += quantity

        self.session.modified = True

    def save(self):
        self.session.modified = True

    def total(self):
        total = 0
        for item in self:
            total += item['total']
        return total

    def remove(self, id):
        if id in self.cart:
            del self.cart[id]
            self.save()

    def count(self):
        return sum(item['quantity'] for item in self.cart.values())

    def update(self, unique_id, quantity):
        if unique_id in self.cart:
            self.cart[unique_id]['quantity'] = int(quantity)

        self.session.modified = True

    def remove_cart(self):
        del self.session['cart']