from django.test import TestCase

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from products.models import Product, Size, Brand, Category
from .models import Cart, CartItem


class CartModelTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='alice', password='pass')
		brand = Brand.objects.create(name='B')
		cat = Category.objects.create(name='C')
		size = Size.objects.create(value='42')
		img = SimpleUploadedFile('p.jpg', b'img', content_type='image/jpeg')
		self.product = Product.objects.create(name='P', price=100, image=img, stock=5)
		self.product.sizes.add(size)

	def test_cart_and_items(self):
		cart = Cart.objects.create(user=self.user)
		item = CartItem.objects.create(cart=cart, product=self.product, quantity=2, size='42')
		self.assertEqual(str(cart).startswith('Cart'), True)
		self.assertEqual(str(item), '2 x P')
		self.assertEqual(cart.items.count(), 1)
