from django.urls import path
from wishlist.views import WishlistView, WishlistAddView, WishlistRemoveView

app_name = 'wishlist'

urlpatterns = [
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/', WishlistAddView.as_view(), name='wishlist-add'),
    path('wishlist/remove/<int:id>/', WishlistRemoveView.as_view(), name='wishlist-remove'),
]