from django.db import models
from django.contrib.auth.models import User

# Bảng lưu trữ lịch sử chat của từng người dùng
class ChatMessage(models.Model):
    # Liên kết với tài khoản khách hàng. null=True, blank=True để khách chưa đăng nhập vẫn có thể chat (nhưng không lưu)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField(verbose_name="Nội dung tin nhắn")
    is_bot = models.BooleanField(default=False, verbose_name="Là tin nhắn của Bot?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # Tự động sắp xếp tin nhắn cũ trước, mới sau để hiển thị đúng thứ tự

    def __str__(self):
        nguoi_gui = "Bot" if self.is_bot else "Khách"
        user_name = self.user.username if self.user else "Khách vãng lai"
        return f"[{nguoi_gui}] - {user_name} - {self.message[:30]}..."