from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.urls import path
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from . import models


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
    


admin.site.register(models.Account, CustomAccountAdmin)

# Остальные модели
admin.site.register([
    models.Client,
    models.AccountToClient,
    models.Service,
    models.Order,
    models.OrderStatus,
])