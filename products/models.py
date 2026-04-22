from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator

# --- BRANDS ---
class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True) 
    description = models.TextField(blank=True, null=True) 

    def __str__(self):
        return self.name

# --- CATEGORIES ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Loại sản phẩm" 
        
    def __str__(self):
        return self.name

# --- SIZES ---
class Size(models.Model):
    value = models.CharField(max_length=10, unique=True) 
    
    def __str__(self):
        return self.value

# --- PRODUCT ---
class Product(models.Model):
    name = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ManyToManyField(Category, blank=True, verbose_name="Loại sản phẩm")
    sizes = models.ManyToManyField(Size) 
    
    price = models.IntegerField(
        validators=[MinValueValidator(0)], 
        verbose_name="Giá hiện tại"
    )
    old_price = models.IntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(0)], 
        verbose_name="Giá cũ (Để trống nếu không giảm giá)"
    )
    
    description = models.TextField(blank=True) 
    image = models.ImageField(
        upload_to='product_images/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'svg', 'gif'])],
        verbose_name="Ảnh đại diện"
    )
    
    stock = models.PositiveIntegerField(default=0, verbose_name="Số lượng tồn kho")
    is_active = models.BooleanField(default=True, verbose_name="Đang kinh doanh")
    stock_status = models.BooleanField(default=True) 

    discount_percent = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Phần trăm giảm giá"
    )

    @property
    def is_on_sale(self):
        return bool(self.old_price and self.old_price > self.price)

    def get_sale_percent(self):
        if self.discount_percent:
            return int(self.discount_percent)
        if self.old_price and self.old_price > self.price:
            percent = ((self.old_price - self.price) / self.old_price) * 100
            return int(percent)
        return 0

    def get_discounted_price(self):
        percent = self.get_sale_percent()
        if percent and percent > 0:
            base = self.old_price if self.old_price else self.price
            discounted = int(base * (100 - percent) / 100)
            return max(discounted, 0)
        return self.price

    def __str__(self):
        return self.name

# --- PRODUCT IMAGES (EXTRA) ---
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='product_images/extra/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'svg', 'gif'])],
        verbose_name="Ảnh phụ"
    )
    alt_text = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"

# --- REVIEWS ---
class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 sao'),
        (2, '2 sao'),
        (3, '3 sao'),
        (4, '4 sao'),
        (5, '5 sao'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES, default=5, verbose_name="Số sao")
    comment = models.TextField(verbose_name="Nội dung đánh giá")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Đánh giá"
        verbose_name_plural = "Đánh giá"

    def __str__(self):
        return f"{self.user.username} đánh giá {self.product.name} - {self.rating} sao"

# --- POLICIES ---
class StorePolicy(models.Model):
    title = models.CharField(max_length=100, default="Cấu hình chính sách chung", verbose_name="Tên cấu hình")
    payment_policy = models.TextField(verbose_name="Nội dung Chính sách thanh toán")
    return_policy = models.TextField(verbose_name="Nội dung Chính sách đổi trả")

    class Meta:
        verbose_name = "Chính sách cửa hàng"
        verbose_name_plural = "Chính sách cửa hàng"

    def __str__(self):
        return self.title

# --- SALES/PROMOTIONS ---
class Sale(models.Model):
    title = models.CharField(max_length=120, default='Flash Sale', verbose_name='Tiêu đề chương trình')
    products = models.ManyToManyField(Product, blank=True, related_name='sales', verbose_name='Sản phẩm tham gia')
    start_date = models.DateTimeField(verbose_name='Bắt đầu')
    end_date = models.DateTimeField(verbose_name='Kết thúc')
    active = models.BooleanField(default=True, verbose_name='Kích hoạt')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Chương trình khuyến mãi'
        verbose_name_plural = 'Chương trình khuyến mãi'

    def __str__(self):
        return f"{self.title} ({self.start_date.date()} - {self.end_date.date()})"