import datetime
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from carts.models import CartItem

# Create your views here.
@login_required
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    payment = Payment.objects.create(
        user = request.user, 
        payment_id = body['transID'], 
        payment_method = body['payment_method'], 
        status = body['status'], 
        amount_paid = order.order_total
    )
    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(buyer=request.user, is_active=True)
    for item in cart_items:
        order_product = OrderProduct.objects.create(
            order_id = order.id, 
            payment = payment, 
            user_id = request.user.id, 
            product_id = item.product_id, 
            quantity = item.quantity, 
            price = item.product.price, 
            ordered = True
        )
        order_product.variations.set(item.variations.all())
        item.product.stock -= order_product.quantity
        item.product.save()
    cart_items.delete()

    mail_subject = 'Thank you for your order'
    mail_body = render_to_string('orders/order_recieved_email.html', {
        'user': request.user, 
        'order': order, 
        })
    send_emails = EmailMessage(mail_subject, mail_body, to=(request.user.email,))
    send_emails.send()

    data = {'order_number': order.order_number, 'transID': payment.payment_id}
    return JsonResponse(data)


@login_required
def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(buyer=current_user, is_active=True)
    if not cart_items.exists():
        messages.info(request, "To place an order, buy something.")
        return redirect(reverse('store'))
    total = 0
    quantity = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            current_date = datetime.date.today().strftime('%Y%m%d')
            data.order_number = order_number = current_date + str(data.id)
            data.save()
            
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            return render(request, 'orders/payments.html', context={
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            })

    return render(request, "orders/place-order.html", context={'form': form})


@login_required
def order_complete(request):
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('transID')
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
    except (Order.DoesNotExist, OrderProduct.DoesNotExist, Payment.DoesNotExist):
        return redirect('index')
    subtotal = 0
    for i in ordered_products:
        subtotal += i.price * i.quantity
    return render(request, "orders/order_complete.html", context={
        'order': order, 
        'ordered_products': ordered_products, 
        'subtotal': subtotal, 
    })
