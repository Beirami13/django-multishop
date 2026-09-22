from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from home.models import Contact
from product.models import Product


class HomeView(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['featured_products'] = Product.objects.all()[:8]
        context['recent_products'] = Product.objects.order_by('-created_at')[:8]

        return context

class ContactView(View):
    def get(self, request):
        return render(request, 'home/contact.html', {})
    def post(self, request):
        name = request.POST['name']
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        Contact.objects.create(name=name, email=email, subject=subject, message=message)

        return render(request, 'home/contact.html', {})