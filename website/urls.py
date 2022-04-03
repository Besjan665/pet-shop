from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('about.html', views.about, name="about"),
    path('shop.html', views.shop, name="shop"),
    path('contact.html', views.contact, name="contact"),
    path('cart.html', views.cart, name="cart"),
    path('blog.html', views.blog, name="blog"),
    path('checkout.html', views.checkout, name="checkout"),
    path('update_item/', views.update_item, name="update_item"),
    path('process_order/', views.process_order, name="process_order"),
]
