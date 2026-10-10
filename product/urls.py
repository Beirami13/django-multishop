from django.urls import path
from .views import ProductDetailView, ProductListView, CommentAddView

app_name = 'product'

urlpatterns = [
    path('', ProductListView.as_view(), name='products'),
    path('category/<slug:slug>/', ProductListView.as_view(), name='category'),
    path('<int:pk>/', ProductDetailView.as_view(), name='detail'),
    path('<int:pk>/comment/',CommentAddView.as_view(),name='comment-add'),
]
