from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order, OrderStatus

@receiver(post_save, sender=Order)
def create_order_status(sender, instance, created, **kwargs):
    
    if created:  
        OrderStatus.objects.create(
            order=instance,
            status=OrderStatus.Status.CREATED,  
            account=instance.account
        )

@receiver(pre_save, sender=OrderStatus)
def set_account_from_order(sender, instance, **kwargs):

    if not instance.account:  
        instance.account = instance.order.account
