from django.db import models
from django.contrib.auth.models import AbstractUser


class Account(AbstractUser):
    clients = models.ManyToManyField(
        'Client', blank=True,
        through='AccountToClient',
        through_fields=('account', 'client'),
        related_name='client_accounts'
    )


class Client(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField("email address", blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    class ClientStatus(models.TextChoices):
        NEW = 'NEW', 'New'
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        PROBLEM = 'PROBLEM', 'Problem'

    status = models.CharField(
        max_length=10,
        choices=ClientStatus.choices,
        default=ClientStatus.NEW
    )

    

    def __str__(self):
        return f"{self.name} {self.surname}"


class AccountToClient(models.Model):
    account = models.ForeignKey('Account', on_delete=models.PROTECT)
    client = models.ForeignKey('Client', on_delete=models.PROTECT)
    create_dt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return  f'{self.account} - {self.client}'


class Service(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Order(models.Model):
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    create_dt = models.DateTimeField(auto_now_add=True)
    vehicle_info = models.CharField(max_length=255, blank=True, null=True)  # Новое текстовое поле


    def __str__(self):
        vehicle_info_display = f" | Vehicle: {self.vehicle_info}" if self.vehicle_info else ""
        return f'Order #{self.id} | {self.service.name} | {self.client.name} {self.client.surname}{vehicle_info_display}'



class OrderStatus(models.Model):
    class Status(models.IntegerChoices):
        CREATED = 0, 'Created'
        ACTIVE = 10, 'Active'
        COMPLETED = 20, 'Completed'
        CANCELLED = 30, 'Cancelled'
        DELETED = 90, 'Deleted'

    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    status = models.SmallIntegerField(choices=Status.choices, default=Status.CREATED)  
    account = models.ForeignKey(Account, on_delete=models.PROTECT, null=True, blank=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    note_reason = models.TextField(blank=True, null=True)  
    is_reopened = models.BooleanField(default=False)  

    def __str__(self):
        reopened_label = " (Reopened)" if self.is_reopened else ""
        return f'{self.order} - {self.get_status_display()}{reopened_label}'