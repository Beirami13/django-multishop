from cart.views import OrderDetailView, OrderCreationView, DiscountCheckView
from cart.views import CartView, CartAddView, CartRemoveView, CartUpdateView
from django.urls import path
from .views import verify, send_request

app_name = 'cart'
urlpatterns = [
    path('detail/', CartView.as_view(), name='cart'),
    path('add/', CartAddView.as_view(), name='cart-add'),
    path('remove/<str:id>/', CartRemoveView.as_view(), name='cart-remove'),
    path('update/', CartUpdateView.as_view(), name='cart-update'),

    path('checkout/', OrderCreationView.as_view(), name='order-creation'),
    path('order/<int:id>/', OrderDetailView.as_view(), name='order-detail'),
    path('Applydiscount/', DiscountCheckView.as_view(), name='apply-discount'),
    path('request', send_request, name='request'),
    path('verify', verify, name='verify')
]
