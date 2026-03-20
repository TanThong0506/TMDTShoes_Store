from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
<<<<<<< HEAD
=======
    # Bạn có thể thêm logo hãng ở đây nếu muốn
    
>>>>>>> main
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
<<<<<<< HEAD
    def __str__(self):
        return self.name

class Size(models.Model):
    value = models.CharField(max_length=10, unique=True) # Ví dụ: 35, 36, 37...
    def __str__(self):
        return self.value

class Product(models.Model):
    name = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    # Thêm trường Size ở đây (Quan hệ Nhiều-Nhiều)
    sizes = models.ManyToManyField(Size, blank=True) 
    
    price = models.DecimalField(max_digits=12, decimal_places=0)
    # Thêm trường giá khuyến mãi nếu bạn muốn dùng như đã nói ở trên
    discount_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    
=======

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    # Kết nối với bảng Brand và Category
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=0)
>>>>>>> main
    image = models.ImageField(upload_to='products/')
    is_featured = models.BooleanField(default=False)

    def __str__(self):
<<<<<<< HEAD
        return self.name

    # Hàm hỗ trợ tính % giảm giá (nếu có)
    def get_sale_percent(self):
        if self.discount_price and self.price > 0:
            percent = 100 - (self.discount_price / self.price * 100)
            return int(percent)
        return 0
=======
        return self.name
>>>>>>> main
