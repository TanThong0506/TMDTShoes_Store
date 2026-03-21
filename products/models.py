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
        verbose_name_plural = "Categories" 
    def __str__(self):
        return self.name

class Size(models.Model):
    value = models.CharField(max_length=10, unique=True) 
    
    def __str__(self):
        return self.value

class Product(models.Model):
    name = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    sizes = models.ManyToManyField(Size) 
    price = models.IntegerField(
        validators=[MinValueValidator(1000)], 
        verbose_name="Giá hiện tại"
    )
    old_price = models.IntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(1000)], 
        verbose_name="Giá cũ"
    )
    description = models.TextField(blank=True) 
    image = models.ImageField(upload_to='product_images/')
    
    stock = models.PositiveIntegerField(default=0, verbose_name="Số lượng tồn kho")
    is_active = models.BooleanField(default=True, verbose_name="Đang kinh doanh")
    
    # Giữ lại trong Model để không lỗi DB nhưng sẽ ẩn ở Admin
    payment_policy = models.TextField(blank=True, verbose_name="Chính sách thanh toán")
    return_policy = models.TextField(blank=True, verbose_name="Chính sách đổi trả")

    stock_status = models.BooleanField(default=True) 

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/extra/')
    alt_text = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# --- MODEL QUẢN LÝ CHÍNH SÁCH RIÊNG ---
class StorePolicy(models.Model):
    title = models.CharField(max_length=100, default="Cấu hình chính sách chung", verbose_name="Tên cấu hình")
    payment_policy = models.TextField(verbose_name="Nội dung Chính sách thanh toán")
    return_policy = models.TextField(verbose_name="Nội dung Chính sách đổi trả")

    class Meta:
        verbose_name = "Chính sách cửa hàng"
        verbose_name_plural = "Chính sách cửa hàng"

    def __str__(self):
        return self.title