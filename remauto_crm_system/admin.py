from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from . import models
from django.utils.html import format_html






class CustomAccountAdmin(UserAdmin):
    model = models.Account

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<id>/password/',
                self.admin_site.admin_view(self.password_change_view),
                name='account_password_change',
            ),
        ]
        return custom_urls + urls

    def password_change_view(self, request, id):
        user = get_object_or_404(self.model, pk=id)

        if request.method == 'POST':
            form = AdminPasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                self.message_user(request, "Password was successfully changed.")
                return HttpResponseRedirect(f'../')
        else:
            form = AdminPasswordChangeForm(user)

        context = {
            'form': form,
            'title': f'Изменить пароль: {user.username}',
            'opts': self.model._meta,
            'original': user,
            'app_label': self.model._meta.app_label,
        }

        return render(request, 'admin/auth/user/change_password.html', context)



class AccountToClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_username', 'client_full_name', 'create_dt')
    search_fields = ('client__name', 'client__surname', 'client__email', 'client__phone_number')  
    list_filter = ('create_dt', 'account__username')
    ordering = ('-create_dt',)

    
    autocomplete_fields = ('client',)

    
    readonly_fields = ('client_details', 'create_dt')

    
    fieldsets = (
        ('Информация об аккаунте', {
            'fields': ('account',),
        }),
        ('Информация о клиенте', {
            'fields': ('client', 'client_details'),
        }),
        ('Дата создания', {
            'fields': ('create_dt',),
        }),
    )

    
    def account_username(self, obj):
        return f" {obj.account.username}" 
    account_username.short_description = 'Account Username'

    
    def client_full_name(self, obj):
        return f"{obj.client.name} {obj.client.surname}"
    client_full_name.short_description = 'Client Full Name'

    
    def client_details(self, obj):
        client = obj.client

        
        orders = models.Order.objects.filter(client=client)
        if orders.exists():
            
            active_services = "".join(
                f"<li><span style='margin-left: 0rem; font-weight: bold; font-size: 14px'> • {order.service.name}</span></li>"
                for order in orders
            )
            
            active_services = f"<ul style='margin-left: 0rem; padding-left: 0rem'>{active_services}</ul>"
        else:
            
            active_services = "<b><span style='color: #ff4d4f; margin-left: .5rem;'>The client has no orders yet</span></b>"

        return format_html(
            "<div style='padding: .5rem'><strong style='; color: #78acc4'>Client ID:</strong> <span style='margin-left: .5rem; font-weight: bold'>{}</span><br></div>"
            "<div style='padding: .5rem'><strong style='; color: #78acc4'>First Name:</strong> <span style='margin-left: .5rem; font-weight: bold'>{}</span><br></div>"
            "<div style='padding: .5rem'><strong style='; color: #78acc4'>Last Name:</strong> <span style='margin-left: .5rem; font-weight: bold'>{}</span><br></div>"
            "<div style='padding: .5rem'><strong style='; color: #78acc4'>Email:</strong> <span style='margin-left: .5rem; font-weight: bold'>{}</span><br></div>"
            "<div style='padding: .5rem'><strong style='; color: #78acc4'>Phone:</strong> <span style='margin-left: .5rem; font-weight: bold'>{}</span><br></div>"
            "<div style='padding: .5rem'><strong style='; color: #78acc4'>Address:</strong> <span style='margin-left: .5rem; font-weight: bold'>{}</span><br></div>"
            "<div style='padding: .5rem'><strong style='; color: #78acc4'>Date of Birth:</strong> <span style='margin-left: .5rem; font-weight: bold'>{}</span><br></div>"
            "<div style='padding: .5rem'><strong style='; color: #78acc4'>Client Status:</strong> <span style='margin-left: .5rem; font-weight: bold'>{}</span><br></div>"
            "<div style='padding: .5rem'><strong style='; color: #78acc4'>Active Services:</strong>{}</div>",
            client.id,
            client.name,
            client.surname,
            client.email or "—",
            client.phone_number or "—",
            client.address or "—",
            client.date_of_birth or "—",
            client.get_status_display(),
            format_html(active_services),
        )
    client_details.short_description = "Additional information about the client"



@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'surname', 'email', 'phone_number', 'status')
    search_fields = ('id', 'name', 'surname')
    


    def get_search_results(self, request, queryset, search_term):
        
        if search_term.isdigit():
            queryset = queryset.filter(id=search_term)
            return queryset, False
        
        return super().get_search_results(request, queryset, search_term)



@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'client', 'account', 'create_dt', 'vehicle_info')
    search_fields = ('id', 'service__name', 'client__name', 'client__surname', 'account__username')

    def get_search_results(self, request, queryset, search_term):
        """
        Настройка поиска для автозаполнения.
        """
        if search_term.isdigit():
            queryset = queryset.filter(id=search_term)  
            return queryset, False
        return super().get_search_results(request, queryset, search_term)


@admin.register(models.OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'status_display', 'is_reopened_display', 'order_service', 'order_id_link', 'client_name_link', 'account_id_display', 'vehicle_info_display', 'create_dt')
    
    list_filter = ('status', 'is_reopened', 'account')
    
    search_fields = ('order__id', 'order__client__name', 'order__client__surname', 'order__service__name', 'order__vehicle_info')
    
    ordering = ('-create_dt',)
    
    autocomplete_fields = ['order']
    
    def account_id_display(self, obj):
        if obj.order.account:
            url = reverse('admin:remauto_crm_system_account_change', args=[obj.order.account.id])
            return format_html('<a href="{}"> {} ( {} ) </a>', url, obj.order.account.username, obj.order.account.id)
        return "No account linked"
    account_id_display.short_description = 'Account ( ID )'
    
    def order_service(self, obj):
        return obj.order.service.name
    order_service.short_description = 'Service'
    
    def order_id_link(self, obj):
        url = reverse('admin:remauto_crm_system_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.id)
    order_id_link.short_description = 'Order ID'
    
    def is_reopened_display(self, obj):
        if obj.is_reopened:
            return format_html('<span style="color: green; font-weight: bold;">Reopened</span>')
        return format_html('<span style="color: gray;">No</span>')
    is_reopened_display.short_description = 'Reopened'
    
    def status_display(self, obj):
        status_color = {
            models.OrderStatus.Status.CREATED: "blue",
            models.OrderStatus.Status.ACTIVE: "green",
            models.OrderStatus.Status.COMPLETED: "gray",
            models.OrderStatus.Status.CANCELLED: "red",
            models.OrderStatus.Status.DELETED: "black",
        }
        color = status_color.get(obj.status, "black")
        return format_html('<span style="color: {};">{}</span>', color, obj.get_status_display())
    status_display.short_description = 'Status'
    
    def client_name_link(self, obj):
        client = obj.order.client
        url = reverse('admin:remauto_crm_system_client_change', args=[client.id])
        return format_html('<a href="{}">{}</a>', url, f"{client.name} {client.surname} (ID: {client.id})")
    client_name_link.short_description = 'Client ( ID )'

    def vehicle_info_display(self, obj):
        return obj.order.vehicle_info or "Not specified"
    vehicle_info_display.short_description = 'Vehicle Info'
    
    actions = ['mark_active']

    def mark_active(self, request, queryset):
        updated_count = queryset.update(status=models.OrderStatus.Status.ACTIVE)
        self.message_user(request, f"{updated_count} orders marked as ACTIVE.")
    mark_active.short_description = 'Mark selected orders as ACTIVE'





admin.site.register(models.Account, CustomAccountAdmin)
admin.site.register(models.Service)

admin.site.register(models.AccountToClient, AccountToClientAdmin)
