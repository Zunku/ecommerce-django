from django.conf import settings
# post_save receive a signal from a model when an object is saved
from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import Customer

# Signal Receivers/Handlers
# This decorator is for connect receivers to signals. Allow us to choose the signal and the model who sended it
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_for_new_user(sender, **kwargs):
    if kwargs['created']:
        Customer.objects.create(user=kwargs['instance'])