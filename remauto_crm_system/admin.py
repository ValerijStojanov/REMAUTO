from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.urls import path
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from . import models


# Кастомный UserAdmin для модели Account
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


# Кастомный Admin для модели AccountToClient
class AccountToClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_username', 'client_full_name', 'create_dt')
    search_fields = ('client__name', 'client__surname', 'client__email', 'client__phone_number')  # Для автозаполнения
    list_filter = ('create_dt', 'account__username')
    ordering = ('-create_dt',)

    # Используем автозаполнение для клиента
    autocomplete_fields = ('client',)

    # Поля только для чтения
    readonly_fields = ('client_details', 'create_dt')

    # Группировка полей в секции
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

    # Кастомное отображение имени пользователя аккаунта
    def account_username(self, obj):
        return obj.account.username
    account_username.short_description = 'Account Username'

    # Кастомное отображение полного имени клиента
    def client_full_name(self, obj):
        return f"{obj.client.name} {obj.client.surname}"
    client_full_name.short_description = 'Client Full Name'

    # Полная информация о клиенте
    def client_details(self, obj):
        client = obj.client

        # Получаем все заказы клиента и извлекаем услуги
        orders = models.Order.objects.filter(client=client)
        if orders.exists():
            # Формируем список <li> с услугами
            active_services = "".join(
                f"<li><span style='margin-left: 0rem; font-weight: bold; font-size: 14px'> • {order.service.name}</span></li>"
                for order in orders
            )
            # Оборачиваем в <ul>
            active_services = f"<ul style='margin-left: 0rem; padding-left: 0rem'>{active_services}</ul>"
        else:
            # Если услуг нет
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






# Регистрация модели Client с поиском для автозаполнения
@admin.register(models.Client)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'surname', 'email', 'phone_number', 'status')
    search_fields = ('id', 'name', 'surname')
    


    def get_search_results(self, request, queryset, search_term):
        # Проверяем, если запрос состоит только из цифр, ищем по ID
        if search_term.isdigit():
            queryset = queryset.filter(id=search_term)
            return queryset, False
        # В остальных случаях ищем по стандартным полям
        return super().get_search_results(request, queryset, search_term)


# Регистрация остальных моделей
admin.site.register(models.Account, CustomAccountAdmin)
admin.site.register(models.Service)
admin.site.register(models.Order)
admin.site.register(models.OrderStatus)
admin.site.register(models.AccountToClient, AccountToClientAdmin)
