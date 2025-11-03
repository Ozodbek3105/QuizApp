import pandas as pd
from django.db import transaction
from django.db.utils import IntegrityError, DataError
from .models import Question

def handle_excel_upload(excel_file, sheet_name):
    """
    Excel faylni oladi, qayta ishlaydi va natijalarni lug'at (dict) sifatida qaytaradi.
    Bu funksiya 'request' yoki 'messages' haqida bilmaydi.
    """
    created_count = 0
    skipped_count = 0
    total_rows = 0
    errors = [] # Xatoliklarni yig'ish uchun ro'yxat

    try:
        # 1. Excel faylni o'qish
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        df.columns = df.columns.str.strip()
        total_rows = len(df)

    except Exception as e:
        errors.append(f"Excel faylni o'qishda xatolik: {e}")
        return {
            'created_count': 0, 
            'skipped_count': total_rows, 
            'errors': errors
        }

    # 2. Ma'lumotlarni bazaga yuklash (Sizning kodingizdagi mantiq)
    for index, row in df.iterrows():
        try:
            with transaction.atomic():
                Question.objects.create(
                    # Siz bergan koddan aynan ko'chirildi
                    Modul = row['Modul'], 
                    lMavzu = row['Mavzu'], # Eslatma: Bu 'lMavzu' bo'lishi kerak emasmi?
                    Savol_ID = int(row['Savol_ID']), 
                    Savol_Matni = row['Savol_Matni'],
                    Variant_A = row['Variant_A'],
                    Variant_B = row['Variant_B'],
                    Variant_C = row['Variant_C'],
                    Variant_D = row['Variant_D'],
                    To_g_ri_Javob = row['Tugri_Javob'], 
                )
                created_count += 1
        
        except KeyError as e:
            errors.append(f"JIDDIY XATO (Qator {index+2}): Excel ustuni topilmadi: {e}. Yuklash to'xtatildi.")
            skipped_count = total_rows - created_count
            break # Birinchi jiddiy xatoda to'xtaymiz
                
        except (IntegrityError, DataError, ValueError) as e:
            errors.append(f"Qator {index+2} (Excelda) yuklanmadi. ASOSIY XATO: {e}. Savol_ID: {row.get('Savol_ID', 'Nomalum')}")
            skipped_count += 1
                
        except Exception as e:
            errors.append(f"KUTILMAGAN XATO (Qator {index+2}): {e}. Yuklash to'xtatildi.")
            skipped_count = total_rows - created_count
            break

    # Natijalarni view'ga qaytarish
    return {
        'created_count': created_count,
        'skipped_count': skipped_count,
        'errors': errors
    }
