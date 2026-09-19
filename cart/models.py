from django.db import models

from account.models import User
from product.models import Product


class Order(models.Model):
    PAYMENT_CHOICES = [('cash', 'Cash on Delivery'),('online', 'Online Payment'),]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey('account.Address',on_delete=models.PROTECT)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    payment_method = models.CharField(max_length=20,choices=PAYMENT_CHOICES,default='cash')
    subtotal = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    discount_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    total_price = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    created = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return self.user.phone_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.product.name


class Discount(models.Model):
    name = models.CharField(max_length=100, unique=True)
    discount = models.SmallIntegerField()
    quantity = models.IntegerField()

    def __str__(self):
        return self.name
