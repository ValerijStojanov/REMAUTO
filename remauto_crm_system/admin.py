from django.contrib import admin
from remauto_crm_system import models



# Register your models here.

admin.site.register([
	models.Account,
	models.Client,
	models.AccountToClient,
	models.Service,
	models.Order,
	models.OrderStatus,
])