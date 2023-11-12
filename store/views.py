from django.db.models import Q, Avg, Value
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from .forms import ReviewForm
from .models import Product, ReviewRating, ProductGallery
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from orders.models import OrderProduct

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


def show_stars(value):
    star = [
        '<i class="fa-regular fa-star"></i>', 
        '<i class="fa-solid fa-star-half-stroke"></i>', 
        '<i class="fa-solid fa-star"></i>'
    ]
    halves = int(value*2) if value else 0
    stars = halves//2 * star[2] + halves%2 * star[1] + (10 - halves)//2 * star[0]  
    return stars


def product_detail(request, category, product):
    product = get_object_or_404(Product, category__slug=category, slug=product, is_available=True)
    product_gallery = ProductGallery.objects.filter(product=product)
    context = {
        'product': product, 
        'product_gallery': product_gallery, 
        'in_cart': CartItem.objects.filter(cart__cart_id__exact=_cart_id(request), product=product).exists(), 
        }
    reviews = ReviewRating.objects.filter(product=product, status=True)
    average = show_stars(reviews.aggregate(Avg('rating', default=0))['rating__avg'])
    context['average'] = average
    reviews = reviews.annotate(stars=Value(''))
    for e in reviews: 
        e.stars = show_stars(e.rating)
    context['reviews'] = reviews

    if request.user.is_authenticated:
        context['user_cart'] = CartItem.objects.filter(buyer=request.user, product=product).exists()
        context['orderproduct'] = OrderProduct.objects.filter(user=request.user, product=product, ordered=True).exists()
        try:
            review = reviews.get(user=request.user)
            form = ReviewForm(initial={'subject': review.subject, 'review': review.review, 'rating': review.rating})
        except (TypeError, ReviewRating.DoesNotExist):
            form = ReviewForm()
        else:
            stars = show_stars(review.rating)
            context['stars'] = stars

        context['form'] = form
    return render(request, 'store/product-detail.html', context=context)

@login_required
def submit_review(request, product_pk):
    user = request.user
    referer_url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(user=user, product__pk=product_pk)
            form = ReviewForm(request.POST, instance=review)
            form.save()
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = ReviewRating()
                review.subject = form.cleaned_data['subject']
                review.review = form.cleaned_data['review']
                review.rating = form.cleaned_data['rating']
                review.ip = request.META.get('REMOTE_ADDR')
                review.product_id = product_pk
                review.user = user
                review.save()
        return redirect(referer_url)
    return redirect(index)
