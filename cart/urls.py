from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_page, name='cart_page'),
    path('items/', views.cart_items, name='cart_items'),
    path('items/add/', views.add_to_cart, name='add_to_cart'),
    path('items/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('items/<int:item_id>/delete/', views.delete_cart_item, name='delete_cart_item'),
    path('clear/', views.clear_cart, name='clear_cart'),
]