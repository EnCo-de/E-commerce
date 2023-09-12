from django.contrib import admin
from .models import Cart, CartItem

# Register your models here.
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')
    inlines = (CartItemInline, )


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'buyer', 'cart', 'is_active')
    filter_horizontal = ('variations',)


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
