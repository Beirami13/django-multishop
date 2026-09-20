from django.shortcuts import render
from django.views.generic import DetailView, TemplateView, ListView

from product.models import Product, Category


class ProductDetailView(DetailView):
    template_name = 'product/product.html'
    model = Product


class ProductListView(ListView):
    model = Product
    template_name = 'product/products_list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        queryset = Product.objects.all()

        slug = self.kwargs.get('slug')

        if slug:
            queryset = queryset.filter(category__slug=slug)

        return queryset