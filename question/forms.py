from django import forms

class ExcelUploadForm(forms.Form):
    # Fayl qabul qilish maydoni
    excel_file = forms.FileField(
        label="Excel faylni tanlang (.xlsx)",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    # Varoq nomini kiritish maydoni
    sheet_name = forms.CharField(
        label="Varoq (Sheet) nomi", 
        initial="questions", # Ko'pincha 'questions' ishlatganingiz uchun
        help_text="Masalan: 'questions' yoki 0",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
