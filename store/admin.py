from django.contrib import admin
from .models import Product, Variation

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    list_editable = ('price', 'stock',)
    links = ('category',)
    prepopulated_fields = {'slug': ('product_name',)}


class VariationAdmin(admin.ModelAdmin):
    list_display = ('variation_value', 'product', 'variation_category', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category')


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
