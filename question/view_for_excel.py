from django.shortcuts import render, redirect
from django.contrib import messages # Foydalanuvchiga xabar berish uchun
from .forms import ExcelUploadForm
from .excel_importer import handle_excel_upload # Ajratilgan logikani import qilamiz

def upload_excel_view(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            sheet_name = form.cleaned_data['sheet_name']
            
            # 2. Butun logikani chaqiramiz
            result = handle_excel_upload(excel_file, sheet_name)

            # 3. Natijalarni foydalanuvchiga 'messages' orqali ko'rsatamiz
            
            # Avval xatoliklarni ko'rsatamiz
            for error_msg in result['errors']:
                messages.warning(request, error_msg) # Xatolarni ogohlantirish sifatida

            # Keyin yakuniy natijani ko'rsatamiz
            messages.success(
                request, 
                f"✅ Yuklash tugallandi: {result['created_count']} tasi yaratildi. "
                f"({result['skipped_count']} tasi xatolik bilan o'tkazib yuborildi)"
            )
            
            return redirect('upload_page') # Sahifani yangilaymiz

    else:
        form = ExcelUploadForm() # Agar GET so'rovi bo'lsa, bo'sh forma

    # HTML'ni ko'rsatish
    return render(request, 'upload_excel.html', {'form': form})

