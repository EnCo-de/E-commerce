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


    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        return ReviewRating.objects.filter(product=self, status=True).count()


from django.db.models.signals import pre_save
def price_rounder(sender, instance, **kwargs):
    instance.price = float(round(instance.price), 2)

# pre_save.connect(price_rounder, sender=Product)


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
        return self.variation_value


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
    
    class Meta:
        ordering = ('-updated_at',)


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to='store/products/', max_length=255)

    def __str__(self) -> str:
        return self.product.product_name

    class Meta:
        verbose_name_plural = 'product gallery'
