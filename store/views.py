from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id

# Create your views here.
def index(request):
    return render(request, 'home.html', {
        'products': Product.objects.all().filter(is_available=True)[:8]
        })

def search(request):
    keyword = request.GET.get('keyword')
    if keyword:
        products = Product.objects.filter(Q(product_name__icontains=keyword) | Q(description__icontains=keyword))
        paginator = Paginator(products, 2)
        page = request.GET.get('page')
        context = {
            'products': paginator.get_page(page), 
            'product_count': products.count(), 
            'keyword': keyword, 
            }
    else:
        context = {'product_count': 0}
    context['category_name'] = 'Search results'
    return render(request, 'store/store.html', context=context)
        

def store(request, category_slug=None):
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        cat = category.category_name
        products = Product.objects.filter(category=category, is_available=True)
    else:
        cat = ''
        products = Product.objects.filter(is_available=True)
    paginator = Paginator(products, 2)
    page = request.GET.get('page')

    return render(request, 'store/store.html', {
        'category_name': cat, 
        'products': paginator.get_page(page), 
        'product_count': products.count()
        })

def product_detail(request, category, product):
    return render(request, 'store/product-detail.html', {
        'product': get_object_or_404(Product, category__slug=category, slug=product, is_available=True), 
        'in_cart': CartItem.objects.filter(cart__cart_id__exact=_cart_id(request), product__slug=product).exists(),
        })
