from rest_framework import viewsets, serializers
from .models import Brand, Category, Size, Product, ProductImage, Review, StorePolicy
from .serializers import (
    BrandSerializer, CategorySerializer, SizeSerializer,
    ProductSerializer, ProductImageSerializer, ReviewSerializer,
    )


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class StorePolicyViewSet(viewsets.ModelViewSet):
    queryset = StorePolicy.objects.all()
    # Reuse a simple serializer
    class SimpleStorePolicySerializer(serializers.ModelSerializer):
        class Meta:
            model = StorePolicy
            fields = ['id', 'title', 'payment_policy', 'return_policy']

    serializer_class = SimpleStorePolicySerializer
