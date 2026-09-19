from django.contrib import admin
from . import models
from .models import Discount


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address', 'is_paid')
    inlines = (OrderItemInline,)
    list_filter = ('is_paid',)

@admin.register(models.Discount)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'discount')

