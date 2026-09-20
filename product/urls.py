from django.urls import path

from product.admin import CategoryAdmin
from product.views import ProductDetailView, ProductListView

app_name = 'product'
urlpatterns = [
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:slug>/',ProductListView.as_view(),name='category'),
]