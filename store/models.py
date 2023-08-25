from django.db import models
from django.db.models import Avg, Count
from django.urls import reverse

from accounts.models import Account
from category.models import Category

# Create your models here.

class Product(models.Model):
    product_name    = models.CharField(max_length=200, unique=True)
    slug            = models.SlugField(max_length=200, unique=True)
    description     = models.TextField(max_length=500, blank=True)
    price           = models.FloatField()
    images          = models.ImageField(upload_to='photos/products')
    stock           = models.IntegerField()
    is_available    = models.BooleanField(default=True)
    category        = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-modified_date',)

    def __str__(self):
        return self.product_name
    
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])



class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='c', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='s', is_active=True)


VARIATION_CATEGORIES = (
    ('c', 'color'), 
    ('s', 'size'), 
)


class Variation(models.Model):
    product      = models.ForeignKey(Product, related_name='variations', on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=1, choices=VARIATION_CATEGORIES)
    variation_value = models.CharField(max_length=60)
    is_active       = models.BooleanField(default=True)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)
    
    objects = VariationManager()

    def __str__(self) -> str:
        return f'{self.variation_value}'
