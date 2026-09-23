from django.views.generic import DetailView, ListView
from product.models import Product
from wishlist.models import Wishlist


class ProductDetailView(DetailView):
    template_name = 'product/product.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['wishlist_ids'] = list(
                Wishlist.objects
                .filter(user=self.request.user)
                .values_list('product_id', flat=True)
            )
        else:
            context['wishlist_ids'] = []

        return context


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

        min_discount = self.request.GET.get('min_discount')
        max_discount = self.request.GET.get('max_discount')

        if min_discount:
            queryset = queryset.filter(discount__gte=min_discount)

        if max_discount:
            queryset = queryset.filter(discount__lte=max_discount)

        if min_discount or max_discount:
            queryset = queryset.exclude(discount__isnull=True)

        return queryset