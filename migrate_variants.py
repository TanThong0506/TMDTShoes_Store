import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoestore.settings')
django.setup()

from products.models import Product, ProductVariant

def migrate_stock_to_variants():
    print("Starting stock migration to variants...")
    products = Product.objects.all()
    created_variants = 0
    
    for product in products:
        if product.variants.count() == 0:
            sizes = product.sizes.all()
            if sizes.exists():
                total_stock = product.stock
                num_sizes = sizes.count()
                stock_per_size = total_stock // num_sizes if num_sizes > 0 else 0
                remainder = total_stock % num_sizes if num_sizes > 0 else 0
                
                for i, size in enumerate(sizes):
                    stock = stock_per_size + (remainder if i == 0 else 0)
                    ProductVariant.objects.create(
                        product=product,
                        size=size,
                        stock=stock
                    )
                    created_variants += 1
                    
    print(f"Done! Created {created_variants} variants.")

if __name__ == '__main__':
    migrate_stock_to_variants()
