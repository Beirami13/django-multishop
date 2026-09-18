from django.urls import path

from cart.views import OrderDetailView, OrderCreationView
from cart.views import CartView, CartAddView, CartRemoveView, CartUpdateView

app_name = 'cart'
urlpatterns = [
    path('detail/', CartView.as_view(), name='cart'),
    path('add/', CartAddView.as_view(), name='cart-add'),
    path('remove/<str:id>/', CartRemoveView.as_view(), name='cart-remove'),
    path('update/', CartUpdateView.as_view(), name='cart-update'),

    path('checkout/', OrderCreationView.as_view(), name='order-creation'),
    path('order/<int:id>/', OrderDetailView.as_view(), name='order-detail'),
]
