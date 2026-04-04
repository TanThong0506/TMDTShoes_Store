from rest_framework import routers
from django.urls import path, include

from products.api import (
    BrandViewSet, CategoryViewSet, SizeViewSet, ProductViewSet, ProductImageViewSet, ReviewViewSet, StorePolicyViewSet
)
from orders.api import OrderViewSet, OrderItemViewSet
from cart.api import CartViewSet, CartItemViewSet
from users.api import ChatMessageViewSet

router = routers.DefaultRouter()
router.register(r'brands', BrandViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'sizes', SizeViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-images', ProductImageViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'store-policies', StorePolicyViewSet)

router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)

router.register(r'carts', CartViewSet)
router.register(r'cart-items', CartItemViewSet)

router.register(r'chat-messages', ChatMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
