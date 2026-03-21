from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True) 
    description = models.TextField(blank=True, null=True) 

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = "Categories" # Chữa lỗi "Categorys" trong Admin
    def __str__(self):
        return self.name

class Size(models.Model):
    value = models.CharField(max_length=10, unique=True) # Ví dụ: 35, 36, 37...
    
    def __str__(self):
        return self.value

class Product(models.Model):
    name = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    sizes = models.ManyToManyField(Size) # Một đôi giày có nhiều size
    price = models.IntegerField(
        validators=[MinValueValidator(1000)], # Chặn nhập dưới 1000
        verbose_name="Giá hiện tại"
    )
    old_price = models.IntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(1000)], # Chặn nhập dưới 1000
        verbose_name="Giá cũ"
    )
    description = models.TextField(blank=True) # Mô tả chi tiết
    image = models.ImageField(upload_to='product_images/')
    stock_status = models.BooleanField(default=True) # True: Còn hàng, False: Hết hàng

    def __str__(self):
        return self.name
class ProductImage(models.Model):
    # Liên kết ảnh này với sản phẩm cụ thể
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    # Trường lưu ảnh phụ, ảnh sẽ được upload vào thư mục product_images/extra/
    image = models.ImageField(upload_to='product_images/extra/')
    alt_text = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)