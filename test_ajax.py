from django.test import Client
import json
import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Shoes_Store.settings')
django.setup()

from products.models import Product, Size, ProductVariant

# Get the first product and size
p = Product.objects.first()
v = ProductVariant.objects.filter(product=p).first()

if not v:
    print("No product variant found")
    sys.exit()

s = v.size
print(f"Testing with Product {p.id}, Size {s.value}, Stock {v.stock}")

c = Client()
# We don't need login since add_to_cart is not login_required? Wait, it IS login_required!
# Let's create a user
from django.contrib.auth.models import User
u, _ = User.objects.get_or_create(username='test_user', email='test@test.com')
u.set_password('test_pass')
u.save()

c.login(username='test_user', password='test_pass')

# Add to cart
res = c.post(f'/cart/add/{p.id}/', {'quantity': v.stock, 'size': s.value})
print('Add to cart status:', res.status_code)

# Update cart to exceed stock
res = c.get(f'/cart/update/?item_key={p.id}_{s.value}&action=increase')
print('Update cart status:', res.status_code)
print('Update cart content type:', res.headers.get('Content-Type'))
print('Update cart response:', res.content.decode('utf-8'))
