import os
import json
import logging
import re
import traceback
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

# SỬ DỤNG THƯ VIỆN GROQ (SIÊU NHANH & MIỄN PHÍ)
from groq import Groq

from users.models import ChatMessage
from products.models import Product, Category, Brand 

logger = logging.getLogger(__name__)
load_dotenv() 

# Khởi tạo Groq Client
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)
else:
    client = None
    print("⚠️ LỖI: Chưa lấy được GROQ_API_KEY từ file .env")

# ==========================================
# 1. CÁC TRANG CƠ BẢN
# ==========================================

def home(request):
    sale_products = Product.objects.filter(old_price__gt=0).order_by('?')[:10]
    all_brands = Brand.objects.all()
    latest_products = Product.objects.all().order_by('-id')[:8]
    context = {
        'sale_products': sale_products, 
        'brands': all_brands, 
        'latest_products': latest_products
    }
    return render(request, 'home.html', context)

def help_page(request):
    return render(request, 'help.html')

def sale_page(request):
    sale_items = Product.objects.filter(old_price__gt=0).order_by('-id')
    return render(request, 'sale.html', {'sale_items': sale_items})

def chatbot_index(request):
    return render(request, 'chatbot.html')


# ==========================================
# 2. TIỆN ÍCH & BẢO VỆ DATABASE
# ==========================================

def clean_text_for_db(text):
    """Xóa các emoji để tránh lỗi MySQL 1366 khi lưu vào Database."""
    if not text:
        return ""
    return re.sub(r'[^\x00-\xFFFF]', '', text)


# ==========================================
# 3. XỬ LÝ CHATBOT AI VỚI GROQ (LLAMA 3)
# ==========================================

@csrf_exempt
def get_response(request):
    if request.method == 'POST':
        if not client:
            return JsonResponse({'error': 'Chưa cấu hình Groq API Key.'}, status=503)
        
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message:
                return JsonResponse({'error': 'Tin nhắn trống.'}, status=400)

            # Lưu tin nhắn khách hàng (đã lọc emoji)
            user = request.user if request.user.is_authenticated else None
            if user:
                ChatMessage.objects.create(
                    user=user, 
                    message=clean_text_for_db(user_message), 
                    is_bot=False
                )

            # Lấy dữ liệu sản phẩm CÓ BAO GỒM LINK ẢNH
            products = Product.objects.filter(is_active=True)
            products_context = ""
            for p in products:
                sizes = ", ".join([s.value for s in p.sizes.all()]) if p.sizes.exists() else "Đủ size"
                brand = p.brand.name if p.brand else "Store"
                cate = p.category.name if p.category else "Giày"
                img_url = p.image.url if getattr(p, 'image', None) else ""
                
                products_context += f"- Mã SP: {p.id}. Tên: {p.name}. Loại: {cate}. Hãng: {brand}. Giá: {p.price} VNĐ. Size hiện có: {sizes}. Hình ảnh: {img_url}. Mô tả: {p.description}\n"

            # ==========================================
            # DẠY AI: CHUYÊN VIÊN TƯ VẤN CAO CẤP
            # ==========================================
            system_prompt = f"""
            Bạn là chuyên viên tư vấn bán hàng cao cấp của Shoe Store - "Nâng bước thành công".
            
            🌟 THÔNG TIN CỬA HÀNG:
            - Địa chỉ: Quận Hải Châu, TP. Đà Nẵng | Hotline: 0905.123.456
            - Chính sách: Freeship đơn trên 1 triệu VNĐ. Giao hỏa tốc Đà Nẵng 2h. Hỗ trợ đổi size/mẫu trong 7 ngày.

            🎯 KỸ NĂNG TƯ VẤN & BÁN HÀNG:
            1. GIỚI THIỆU TRUYỀN CẢM HỨNG: Khi khách yêu cầu giới thiệu về một phân loại giày (Running, Bóng rổ, Lifestyle...), hãy viết 1 đoạn giới thiệu bay bổng về đặc tính nổi bật của dòng đó. Trình bày: In đậm tên sản phẩm, dùng gạch đầu dòng, chèn emoji hợp lý (👟, 🔥, ✨).
            2. HIỂN THỊ HÌNH ẢNH SẢN PHẨM: Khi khách yêu cầu "xem chi tiết", "xem hình", "hình ảnh của" một sản phẩm, bạn BẮT BUỘC chèn đoạn mã sau vào câu trả lời để hiển thị ảnh: [SHOW_IMAGE: Đường_Dẫn_Hình_Ảnh_Trong_Dữ_Liệu]
               - Ví dụ: "Dạ đây là hình ảnh đôi giày bạn quan tâm ạ: [SHOW_IMAGE: /media/product_images/giay.png]"
            3. KHI NÀO HỎI SIZE?: **CHỈ KHI** khách nói rõ ý định MUA một SẢN PHẨM CỤ THỂ ("thêm vào giỏ", "mua đôi này", "lấy mã X"), bạn MỚI ĐƯỢC phản hồi kèm mã: [CHOOSE_SIZE: Mã SP: Size1, Size2]
               - Tuyệt đối không gắn mã này nếu khách chỉ đang hỏi thông tin.
            4. HOÀN TẤT GIỎ HÀNG: Khi khách chat đúng cú pháp "Xác nhận đặt mua mã X size Y", hãy báo thành công và chèn mã: [ADD_CART: X: Y] ở cuối.
            5. Giao tiếp: Xưng "mình", gọi "bạn". Nhiệt tình, lịch sự.

            --- DỮ LIỆU SẢN PHẨM ---
            {products_context}
            --- END DỮ LIỆU ---
            """

            # Gọi Groq API
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.75, 
            )
            ai_reply = completion.choices[0].message.content

            # --- XỬ LÝ MẬT LỆNH GIỎ HÀNG THỰC TẾ TRONG SESSION ---
            cart_match = re.search(r'\[ADD_CART:\s*(\d+)\s*:\s*([^\]]+)\]', ai_reply)
            cart = request.session.get('cart', {})
            if not isinstance(cart, dict): cart = {}

            if cart_match:
                p_id = cart_match.group(1)
                size = cart_match.group(2).strip()
                try:
                    product = Product.objects.get(id=p_id)
                    key = f"{p_id}_{size}"
                    if key in cart:
                        cart[key]['quantity'] += 1
                    else:
                        cart[key] = {
                            'product_id': p_id,
                            'name': product.name, 
                            'price': str(product.price), 
                            'quantity': 1, 
                            'size': size
                        }
                    request.session['cart'] = cart
                    request.session.modified = True
                    ai_reply = re.sub(r'\[ADD_CART:.*?\]', f'\n\n[Hệ thống: Đã thêm {product.name} size {size} vào giỏ! 🛍️]', ai_reply)
                except Exception:
                    pass

            cart_count = sum(item.get('quantity', 0) for item in cart.values() if isinstance(item, dict))
            request.session['cart_count'] = cart_count

            # Lưu DB
            if user:
                ChatMessage.objects.create(
                    user=user, 
                    message=clean_text_for_db(ai_reply), 
                    is_bot=True
                )

            return JsonResponse({'response': ai_reply, 'cart_count': cart_count})

        except Exception as e:
            logger.error(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def get_chat_history(request):
    """Lấy 50 tin nhắn lịch sử gần nhất để chat không bị trôi lên quá xa"""
    if request.user.is_authenticated:
        # Sắp xếp giảm dần theo thời gian và chỉ lấy 50 cái mới nhất
        recent_history = ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:50]
        # Đảo ngược lại danh sách để tin nhắn hiển thị đúng thứ tự từ trên xuống dưới
        history = list(recent_history)[::-1]
        
        return JsonResponse({
            'history': [{'message': h.message, 'is_bot': h.is_bot} for h in history]
        })
    return JsonResponse({'history': []})