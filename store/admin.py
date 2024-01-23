from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Variation, ReviewRating, ProductGallery

# Register your models here.
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    
    def preview(self, object):
        return format_html('<img src="{}" style="width: 150px; border-radius: 5%;">', object.image.url)
    preview.short_description = 'image preview'
    readonly_fields = ['preview']


class ProductGalleryAdmin(admin.ModelAdmin):
    def preview(self, object):
            return format_html('<img src="{}" style="width: 150px; border-radius: 5%;">', object.image.url)
    preview.short_description = 'Product Gallery picture'
    list_display = ['preview', 'image', ]
    readonly_fields = ['preview']


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    list_editable = ('price', 'stock',)
    links = ('category',)
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]


class VariationAdmin(admin.ModelAdmin):
    list_display = ('variation_value', 'product', 'variation_category', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category')


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery, ProductGalleryAdmin)
