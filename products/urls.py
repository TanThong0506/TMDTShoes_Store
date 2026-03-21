from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('<int:id>/', views.product_detail, name='product_detail'),

    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('increase/<int:item_id>/', views.increase, name='increase'),
    path('decrease/<int:item_id>/', views.decrease, name='decrease'),

    path('remove/<int:item_id>/', views.remove_item, name='remove_item'),

    path('checkout/', views.checkout, name='checkout'),
]