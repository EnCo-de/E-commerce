from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .models import Product


@receiver(pre_save, sender=Product)
def price_handler(sender, instance, **kwargs):
    try:
        value = float(round(instance.price, 2))
    except:
        raise ValueError(
            _('%(value)s is not an integer or a float  number'),
            params={'value': value},
        )
    else:
        instance.price = value
