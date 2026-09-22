from django.contrib import admin

from product.admin import InformationAdmin
from . import models


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name","email", "message")
    list_filter = ['created_at']