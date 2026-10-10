from django.contrib import admin
from .models import Product, Category, Comment, information
from . import models


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

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created']
    list_filter = ['created']
    search_fields = ['user__phone_number', 'product__name', 'text']
