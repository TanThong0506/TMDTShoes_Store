from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),

    path('search/', views.search_products, name='search'),

    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    path('<int:id>/', views.product_detail, name='product_detail'),

    # Cart
    
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('increase/<int:item_id>/', views.increase, name='increase'),
    path('decrease/<int:item_id>/', views.decrease, name='decrease'),
    path('remove/<int:item_id>/', views.remove_item, name='remove_item'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),
]