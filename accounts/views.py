from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import F
from django.core.exceptions import PermissionDenied

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from orders.models import Order
from carts.models import Cart, CartItem
from carts.views import _cart_id

# Create your views here.
def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            gender = form.cleaned_data['gender']
            city = form.cleaned_data['city']
            country = form.cleaned_data['country']
            password = form.cleaned_data['password']
            username = email[:email.find('@')]
            # username = email.split("@")[0]

            user = Account.objects.create_user(first_name, last_name, username, email, password)
            user.phone_number = phone_number
            user.gender = gender
            user.city = city
            user.country = country
            user.save()
            messages.success(request, f"You are successfully registered, {first_name} {last_name}. Activate your account through the link sent to {email}.")

            current_site = get_current_site(request)
            mail_subject = 'Account activation link'
            mail_body = render_to_string('accounts/account_verification_email.html', {
                'user': user, 
                'domain': current_site, 
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), 
                'token': default_token_generator.make_token(user),
            })
            sent_emails = EmailMessage(mail_subject, mail_body, to=(email,))
            sent_emails.send()

            return redirect(reverse('store'))
    context = {'form': form}
    return render(request, 'accounts/register.html', context=context)

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=['is_active'])
        messages.success(request, "Your Account is activated successfully")
        return redirect('user_login')
    messages.error(request, "Account is not activated, wrong link!")
    return redirect(reverse('store'))

def forgot_password(request):
    if request.method == 'POST' and 'email' in request.POST:
        email = request.POST.get('email')
        account = Account.objects.filter(email__iexact=email)
        if account.exists() and account.count() == 1:
            user = account[0]
            current_site = get_current_site(request)
            mail_subject = 'Password reset link'
            mail_body = render_to_string('accounts/password_reset_email.html', {
                'user': user, 
                'domain': current_site, 
                'uid': urlsafe_base64_encode(force_bytes(user.pk)), 
                'token': default_token_generator.make_token(user),
            })
            sent_emails = EmailMessage(mail_subject, mail_body, to=(user.email,))
            sent_emails.send()
            messages.info(request, "You will receive an email to reset your password")
            return redirect(reverse('store'))
        else:
            messages.error(request, f'No account with such email "{email}"')

    return render(request, 'accounts/forgot_password.html')

def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and user.is_active and default_token_generator.check_token(user, token):
        request.session['uid'] = uidb64
        messages.success(request, "You can now reset your password")
        return redirect('user_login')
    else:
        messages.error(request, "This link has expired")
    return render(request, 'accounts/forgot_password.html')


@login_required
def dashboard(request):
    order_count = Order.objects.filter(user_id=request.user.id, is_ordered=True).count()
    try:
        userprofile = request.user.userprofile
    except: 
        userprofile = None
    return render(request, 'accounts/dashboard.html', {
        'order_count': order_count, 
        'userprofile': userprofile
    })

@login_required
def orders(request):
    return render(request, 'accounts/orders.html', {
        'orders': Order.objects.filter(user_id=request.user.id, is_ordered=True).order_by('-created_at'),
    })

@login_required
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, account=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    return render(request, 'accounts/edit-profile.html', {
        'user_form': user_form, 
        'profile_form': profile_form, 
        'userprofile': userprofile, 
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        current = request.POST.get('current_password')
        changed = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')

        user = Account.objects.get(username__exact=request.user.username)
        if user.check_password(current) and changed == confirm:
            user.set_password(changed)
            user.save()
            # logout(request) is called here by default
            messages.success(request, 'Your password is changed')
            return redirect(dashboard)
        elif changed != confirm:
            messages.error(request, 'Your new password does not match with confirmation password')
        else:
            messages.error(request, 'Your password is wrong')
    return render(request, 'accounts/change-password.html')

def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number__exact=order_number)
    if order.user != request.user:
        raise PermissionDenied
    return render(request, 'accounts/order-detail.html', {'order': order})

# development only
def user_reset(request):
    user = Account.objects.get(pk=4)
    if user is not None:
        user.is_active = False
        user.save(update_fields=['is_active'])
    return render(request, 'accounts/signin.html')

# development only
def noregister(request):
    user = Account.objects.get(pk=4)
    if user is not None:
        messages.success(request, f"You are successfully registered. Activate your account")
        current_site = get_current_site(request)
        mail_subject = 'Account activation link'
        mail_body = render_to_string('accounts/account_verification_email.html', {
            'user': user, 
            'domain': current_site, 
            'uid': urlsafe_base64_encode(force_bytes(user.pk)), 
            'token': default_token_generator.make_token(user),
        })
        sent_emails = EmailMessage(mail_subject, mail_body, to=(user.email,))
        sent_emails.send()
        return redirect(reverse('store'))
    context = {'form': RegistrationForm()}
    return render(request, 'accounts/register.html', context=context)

def user_login(request):
    if request.user.is_authenticated:
        return redirect('index')
    elif request.method == 'POST':
        email = request.POST["email"]
        password = request.POST["password"]

        if request.session.has_key('uid'):
            try:
                uid = urlsafe_base64_decode(request.session.get('uid')).decode()
                a_user = Account._default_manager.get(pk=uid, email=email)
            except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
                a_user = None
            del request.session['uid']
            if a_user is not None and a_user.is_active:
                a_user.set_password(password)
                a_user.save()
                messages.success(request, "Your password is reset")
            else:
                messages.error(request, "Try again to reset password")
                return render(request, 'accounts/signin.html')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
            except Cart.DoesNotExist:
                pass
            else:
                cart_items = cart.cartitem_set.filter(is_active=True)
                if cart_items.exists():
                    repeated_items = CartItem.objects.filter(buyer=user, product__in=cart_items.values_list('product_id', flat=True).distinct(), is_active=True)
                    cart.cartitem_set.update(buyer=user)
                    if repeated_items.exists():
                        for item in cart_items:
                            user_items = repeated_items.filter(product=item.product)
                            for user_item in user_items:
                                if set(item.variations.values_list('id', flat=True)) == set(user_item.variations.values_list('id', flat=True)):
                                    user_item.quantity = F("quantity") + item.quantity
                                    item.quantity = 0
                                    item.is_active=False
                                    user_item.save()
                                    item.save()
                                    break

            login(request, user)
            messages.success(request, f"You are successfully logged in {user.get_username()}.")
            
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return redirect(dashboard)
        else:
            messages.warning(request, f"Wrong login credentials.")
    return render(request, 'accounts/signin.html')

def user_logout(request):
    logout(request)
    messages.info(request, "You are logged out.")
    return redirect(reverse('store'))
