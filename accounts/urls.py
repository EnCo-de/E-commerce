from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.orders, name='orders'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('order-detail/<int:order_number>/', views.order_detail, name='order_detail'),

    path('activate/<uidb64>/<str:token>/', views.activate, name='activate'),
    path('reset-password-validate/<uidb64>/<str:token>/', views.reset_password, name='reset_password'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    
    # development only
    path('noregister/', views.noregister, name='noregister'),
    path('reset/', views.user_reset, name='reset'),
    
]
