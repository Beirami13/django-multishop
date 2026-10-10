from product.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get('cart', {})

    def __iter__(self):
        products = Product.objects.in_bulk([int(i['id']) for i in self.cart.values()])
        for item in self.cart.values():
            product = products.get(int(item['id']))
            if product is None:
                continue
            quantity = int(item['quantity'])
            yield {
                **item,
                'quantity': quantity,
                'product': product,
                'total': product.price * quantity,
                'unique_id': self.unique_id_generator(item['id'], item['color'], item['size']),
            }

    def __len__(self):
        return len(self.cart)

    def unique_id_generator(self, product_id, color, size):
        return f"{product_id}-{color}-{size}"

    def add(self, product, quantity, color, size):
        unique = self.unique_id_generator(product.id, color, size)
        if unique in self.cart:
            self.cart[unique]['quantity'] += quantity
        else:
            self.cart[unique] = {
                'quantity': quantity,
                'size': size,
                'color': color,
                'id': product.id,
            }
        self.save()

    def update(self, unique_id, quantity):
        if unique_id in self.cart:
            self.cart[unique_id]['quantity'] = quantity
            self.save()

    def remove(self, unique_id):
        if unique_id in self.cart:
            del self.cart[unique_id]
            self.save()

    def clear(self):
        self.session.pop('cart', None)
        self.cart = {}
        self.session.modified = True

    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True

    def total(self):
        return sum(item['total'] for item in self)

    def count(self):
        return sum(int(i['quantity']) for i in self.cart.values())