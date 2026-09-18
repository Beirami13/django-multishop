from django.db import models

class Size(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()
    discount = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to="products")
    size = models.ManyToManyField(Size)
    color = models.ManyToManyField(Color)

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
        return {self.product.name}

class information(models.Model):
    text= models.TextField()
    product = models.ForeignKey(Product, null=True,  on_delete=models.CASCADE)

    def __str__(self):
        return self.text
