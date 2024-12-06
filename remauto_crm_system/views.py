from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .forms import AccountCreationForm





def hello_world(request):
    return HttpResponse("Hello, World!")

class CustomLoginView(LoginView):
    template_name = 'remauto_crm_system/login.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard')

@login_required
def dashboard(request):
    user = request.user
    return render(request, 'remauto_crm_system/dashboard.html', {'user': user})


def register(request):
    if request.method == 'POST':
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Логиним пользователя после успешной регистрации
            login(request, user)
            return redirect('dashboard')
    else:
        form = AccountCreationForm()
    return render(request, 'remauto_crm_system/register.html', {'form': form})

