from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData, guestOrder
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from django.core.mail import send_mail
from django.conf import settings


def home(request):
    return render(request, 'home.html', {})


def about(request):
    return render(request, 'about.html', {})


@csrf_exempt
def shop(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'shop.html', context)


@csrf_exempt
def contact(request):
    if request.method == 'POST':
        contact = Contact()
        email = request.POST.get('email')
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        comment = request.POST.get('comment')
        contact.name = name
        contact.email = email
        contact.subject = subject
        contact.comment = comment
        contact.save()
    return render(request, 'contact.html', {})


@csrf_exempt
def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'cart.html', context)


def blog(request):
    return render(request, 'blog.html', {})


@csrf_exempt
def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}

    return render(request, 'checkout.html', context)


@csrf_exempt
def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    print('action: ', action)
    print('product_id: ', product_id)

    customer = request.user.customer
    product = Product.objects.get(id=product_id)

    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderitem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderitem.quantity += 1
    elif action == 'remove':
        orderitem.quantity -= 1

    orderitem.save()

    if orderitem.quantity <= 0:
        orderitem.delete()

    return JsonResponse('Item was added.', safe=False)


@csrf_exempt
def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)
