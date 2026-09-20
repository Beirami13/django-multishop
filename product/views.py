from django.views.generic import DetailView, ListView
from django.views.generic import ListView
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
            queryset = queryset.filter(
                category__slug=slug
            )

        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        if min_price:
            queryset = queryset.filter(
                price__gte=min_price
            )

        if max_price:
            queryset = queryset.filter(
                price__lte=max_price
            )

        return queryset.distinct()