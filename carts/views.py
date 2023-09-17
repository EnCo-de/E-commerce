from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.db.models import F
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = None
        try:
            # get the cart id using the session_key
            cart = Cart.objects.get(cart_id=_cart_id(request)) 
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                user = current_user, 
                cart_id = _cart_id(request)
            )

    if request.method == 'POST':
        n = int(request.POST.get('quantity', 1))
        product_variation = set()
        for e in request.POST:
            if e not in ('csrfmiddlewaretoken', 'quantity'):
                variation = Variation.objects.get( 
                    product=product, 
                    variation_category__iexact=e[6], 
                    variation_value__iexact=request.POST.get(e)
                    )
                product_variation.add(variation)
        if current_user is not None:
            cart_items = CartItem.objects.filter(product=product, buyer=current_user).distinct()
            if product_variation:
                cart_items = cart_items.filter(variations__in=product_variation).distinct()
        else:
            cart_items = CartItem.objects.filter(product=product, cart=cart, variations__in=product_variation).distinct()
        for cart_item in cart_items:
            if set(cart_item.variations.distinct()) == product_variation:
                cart_item.quantity = F("quantity") + n
                cart_item.save()
                return redirect('cart')
        if current_user is not None:
            cart_item = CartItem.objects.create(
                product=product, 
                buyer=current_user, 
                quantity=n
                )
        else:
            cart_item = CartItem.objects.create(
                product=product, 
                cart=cart, 
                quantity=n
                )
        cart_item.variations.set(product_variation)
    else:
        pk = request.GET.get('pk')
        if pk:
            try:
                cart_item = CartItem.objects.get(pk=pk, product=product)
            except CartItem.DoesNotExist:
                messages.error(request, "You don't have that product in your shopping cart.")
                return redirect(reverse('store'))
            cart_item.quantity = F("quantity") + 1
            cart_item.save()
        else:
            if current_user is not None:
                cart_item = CartItem.objects.create(
                    product=product, 
                    buyer=current_user, 
                    quantity=1
                    )
            else:
                cart_item = CartItem.objects.create(
                    product=product, 
                    cart=cart, 
                    quantity=1
                    )
            cart_item.variations.set((Variation.objects.colors().first(), Variation.objects.sizes().first()))            
    return redirect('cart')


def remove_cart(request, product_id):
    if request.user.is_authenticated:
        current_user = request.user
    else:
        current_user = None
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            messages.error(request, "You don't have a shopping cart.")
            return redirect(reverse('store'))
    product = get_object_or_404(Product, id=product_id)
    if current_user is not None:
        cart_items = CartItem.objects.filter(product=product, buyer=current_user)
    else:
        cart_items = CartItem.objects.filter(product=product, cart=cart)
    if cart_items and request.GET.get('remove') == 'All':
        cart_items.delete()
    else:
        try:
            cart_item = cart_items.get(pk=request.GET.get('pk'))
        except CartItem.DoesNotExist:
            messages.error(request, "You don't have that product in your shopping cart.")
            return redirect(reverse('store'))
        else:
            if request.GET.get('remove') == 'True' or cart_item.quantity <= 1:
                cart_item.delete()
            else:
                cart_item.quantity = F("quantity") - 1
                cart_item.save()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(buyer=request.user, is_active=True)
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        except Cart.DoesNotExist:
            messages.error(request, "You don't have a shopping cart.")
            return redirect(reverse('store'))
    context = {'cart': []}
    if not cart_items:
        messages.info(request, "Your shopping cart is empty.")
        return redirect(reverse('store'))
    for cart_item in cart_items:
        total += cart_item.sub_total()
        quantity += cart_item.quantity
    tax = 0.10
    context={
        'cart': cart_items, 
        'category_slug': cart_items.last().product.category.slug,
        'quantity': quantity,
        'total': total, 
        'tax': total * tax, 
        'Total': total * (1+tax), 
        }
    if request.path == reverse('checkout'):
        return context
    return render(request, "carts/cart.html", context=context)

@login_required(login_url='user_login')
def checkout(request):
    context = cart(request)
    return render(request, "carts/checkout.html", context=context)
