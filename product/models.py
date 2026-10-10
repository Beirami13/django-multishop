from django.db import models
from django.conf import settings

class Size(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=10)
    slug = models.SlugField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ManyToManyField(Category, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()
    discount = models.IntegerField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=10)
    image = models.ImageField(upload_to="products")
    size = models.ManyToManyField(Size)
    color = models.ManyToManyField(Color)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def discounted_price(self):
        if self.discount:
            return int(self.price - (self.price * self.discount / 100))

        return self.price

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/gallery")

    def __str__(self):
        return self.product.name

class information(models.Model):
    text= models.TextField()
    product = models.ForeignKey(Product, null=True,  on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.user} - {self.product.name}"