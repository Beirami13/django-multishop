from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView, ListView

from product.models import Product, Category, Comment
from wishlist.models import Wishlist


class ProductDetailView(DetailView):
    template_name = 'product/product.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.select_related('user')
        if self.request.user.is_authenticated:
            context['wishlist_ids'] = list(
                Wishlist.objects.filter(user=self.request.user).values_list('product_id', flat=True)
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

        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset.distinct()


@method_decorator(login_required, name='dispatch')
class CommentAddView(View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        text = request.POST.get('text', '').strip()

        if text and len(text) <= 1000:
            Comment.objects.create(user=request.user, product=product, text=text)

        return redirect(reverse('product:detail', args=[pk]) + '#reviews')