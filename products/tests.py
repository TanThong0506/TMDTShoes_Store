from django.shortcuts import redirect
from django.contrib import messages
from .forms import ProductForm

# ==========================================
# QUẢN LÝ SẢN PHẨM (THÊM, SỬA, XÓA)
# ==========================================
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm sản phẩm mới thành công!')
            return redirect('products:product_list')
    else:
        form = ProductForm()
    
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Thêm Sản Phẩm Mới'})

def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật {product.name} thành công!')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
        
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Cập Nhật Sản Phẩm', 'product': product})

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Đã xóa sản phẩm {product_name}.')
        return redirect('products:product_list')
        
    return render(request, 'products/product_confirm_delete.html', {'product': product})