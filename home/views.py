from django.views.generic import TemplateView
from product.models import Category


from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home/index.html'