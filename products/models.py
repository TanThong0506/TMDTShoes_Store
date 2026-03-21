from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên thương hiệu")
    
    class Meta:
        verbose_name = "Thương hiệu"
        verbose_name_plural = "Thương hiệu"

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Tên danh mục")
    
    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"

    def __str__(self):
        return self.name

class Size(models.Model):
    value = models.CharField(max_length=10, unique=True, verbose_name="Kích thước")
    
    class Meta:
        verbose_name = "Kích cỡ"
        verbose_name_plural = "Kích cỡ"

    def __str__(self):
        return self.value

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Thương hiệu")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Danh mục")
    sizes = models.ManyToManyField(Size, blank=True, verbose_name="Kích cỡ hiện có") 
    
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Giá gốc")
    discount_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name="Giá khuyến mãi")
    
    image = models.ImageField(upload_to='products/', verbose_name="Hình ảnh")
    is_featured = models.BooleanField(default=False, verbose_name="Sản phẩm nổi bật")

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"

    def __str__(self):
        return self.name

    def get_sale_percent(self):
        if self.discount_price and self.price > 0:
            percent = 100 - (self.discount_price / self.price * 100)
            return int(percent)
        return 0