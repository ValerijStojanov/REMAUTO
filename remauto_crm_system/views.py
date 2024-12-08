from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .forms import AccountCreationForm, ClientForm, AddServiceForm
from .models import Order, Client, AccountToClient, OrderStatus


def hello_world(request):
    return HttpResponse("Hello, World!")

class CustomLoginView(LoginView):
    template_name = 'remauto_crm_system/login.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard')

@login_required
def create_order_with_status(request, service, client, account, status=OrderStatus.Status.CREATED):
    """
    Вспомогательная функция для создания заказа с начальным статусом.
    """
    order = Order.objects.create(service=service, client=client, account=account)
    OrderStatus.objects.create(order=order, status=status, account=account)
    return order


@login_required
def dashboard(request):
    user = request.user  

    
    form = ClientForm()
    service_form = AddServiceForm()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')  

        if form_type == 'add_client':
            
            form = ClientForm(request.POST)
            if form.is_valid():
                
                client = form.save()
                AccountToClient.objects.create(account=user, client=client)
                services = form.cleaned_data.get('services', [])
                
                for service in services:
                    Order.objects.create(service=service, client=client, account=user)
                return redirect('dashboard')

        elif form_type == 'add_service':
            
            client_id = request.POST.get('client_id')
            client = get_object_or_404(Client, id=client_id)

            
            if not AccountToClient.objects.filter(account=user, client=client).exists():
                return redirect('dashboard')  

            service_form = AddServiceForm(request.POST)
            if service_form.is_valid():
                service = service_form.cleaned_data['service']
                
                Order.objects.create(service=service, client=client, account=user)
                return redirect('dashboard')

    
    clients = Client.objects.filter(client_accounts=user).prefetch_related(
        'order_set__orderstatus_set'
    )

    
    clients_with_orders = []
    for client in clients:
        orders_with_statuses = []
        for order in client.order_set.filter(account=user):
            orders_with_statuses.append({
                'order': order,
                'statuses': order.orderstatus_set.all()
            })
        clients_with_orders.append({
            'client': client,
            'orders': orders_with_statuses
        })

    return render(request, 'remauto_crm_system/dashboard.html', {
        'user': user,
        'clients_with_orders': clients_with_orders,
        'form': form,  
        'service_form': service_form,  
    })


    
    clients = Client.objects.filter(client_accounts=user).prefetch_related(
        'order_set__orderstatus_set'
    )

    
    clients_with_orders = []
    for client in clients:
        orders_with_statuses = []
        for order in client.order_set.filter(account=user):
            orders_with_statuses.append({
                'order': order,
                'statuses': order.orderstatus_set.all()
            })
        clients_with_orders.append({
            'client': client,
            'orders': orders_with_statuses
        })

    return render(request, 'remauto_crm_system/dashboard.html', {
        'user': user,
        'clients_with_orders': clients_with_orders,
        'form': form,  
        'service_form': service_form,  
    })

def register(request):
    if request.method == 'POST':
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = AccountCreationForm()
    return render(request, 'remauto_crm_system/register.html', {'form': form})


def authorization(request):
    return render(request, 'remauto_crm_system/authorization.html')