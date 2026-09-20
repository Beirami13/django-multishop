from django.views.generic import TemplateView
from product.models import Product


class HomeView(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['featured_products'] = Product.objects.all()[:8]
        context['recent_products'] = Product.objects.order_by('-created_at')[:8]

        return context