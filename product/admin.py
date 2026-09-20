from django.contrib import admin

from . import models
from .models import information, Product


class InformationAdmin(admin.StackedInline):
    model = information

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    inlines = [InformationAdmin]

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(models.Size)
admin.site.register(models.Color)
