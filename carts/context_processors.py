from .models import Cart, CartItem
from .views import _cart_id
from store.models import Product


def counter(request):
    if "admin/" in request.path:
        return {}
    elif request.user.is_authenticated:
        cart_items = CartItem.objects.filter(buyer=request.user, is_active=True)
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = cart.cartitem_set.all()
        except Cart.DoesNotExist:
            return {"cart_count": 0}
    added_products = cart_items.values_list('product_id', flat=True).distinct()
    return {"cart_count": cart_items.count(), "added_products": added_products}
