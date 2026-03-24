from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.contrib.auth.models import User

class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True) 
    description = models.TextField(blank=True, null=True) 

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Loại sản phẩm" 
        
    def __str__(self):
        return self.name

class Size(models.Model):
    value = models.CharField(max_length=10, unique=True) 
    
    def __str__(self):
        return self.value

class Product(models.Model):
    name = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Chọn được nhiều Loại sản phẩm cùng lúc
    category = models.ManyToManyField(Category, blank=True, verbose_name="Loại sản phẩm")
    sizes = models.ManyToManyField(Size) 
    
    # Giá tiền nhập bằng phím tự do
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
    
    # Cho phép chọn nhiều định dạng ảnh khác nhau
    image = models.ImageField(
        upload_to='product_images/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'svg', 'gif'])],
        verbose_name="Ảnh đại diện"
    )
    
    stock = models.PositiveIntegerField(default=0, verbose_name="Số lượng tồn kho")
    is_active = models.BooleanField(default=True, verbose_name="Đang kinh doanh")
    
    # Giữ lại trong Model để không lỗi DB nhưng ẩn ở Admin
    payment_policy = models.TextField(blank=True, verbose_name="Chính sách thanh toán")
    return_policy = models.TextField(blank=True, verbose_name="Chính sách đổi trả")

    stock_status = models.BooleanField(default=True) 

    # Hàm tiện ích kiểm tra giảm giá
    @property
    def is_on_sale(self):
        return bool(self.old_price and self.old_price > self.price)

    # --- HÀM TÍNH % ĐÃ ĐƯỢC BỔ SUNG VÀO ĐÂY ---
    def get_sale_percent(self):
        if self.old_price and self.old_price > self.price:
            percent = ((self.old_price - self.price) / self.old_price) * 100
            return int(percent)
        return 0

    def __str__(self):
        return self.name

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
    
# ================== CART ==================


# ================== ORDER ==================
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    total = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = (
        ('pending', 'Đang xử lý'),
        ('shipping', 'Đang giao'),
        ('done', 'Đã giao'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField()
    price = models.IntegerField()  # giá lưu khi checkout