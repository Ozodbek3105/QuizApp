import pandas as pd
from django.core.management.base import BaseCommand
# Sizning app nomingiz 'question' deb faraz qilindi
from question.models import Question 
from django.db import transaction
from django.db.utils import IntegrityError, DataError

class Command(BaseCommand):
    help = 'Excel fayldagi savollarni ma\'lumotlar bazasiga yuklaydi (Modul, lMavzu va b.)'

    def add_arguments(self, parser):
        # Fayl yo'lini qabul qilish uchun argument qo'shamiz
        parser.add_argument('excel_file', type=str, help='Excel faylining to\'liq yo\'li (masalan, questions.xlsx)')
        parser.add_argument('--sheet', type=str, default=0, help='Excel varog\'ining nomi yoki indeksi (default: 0 - birinchi varoq)')


    def handle(self, *args, **options):
        file_path = options['excel_file']
        sheet_name = options['sheet']

        try:
            # 1. Excel faylni o'qish
            self.stdout.write(self.style.NOTICE(f'"{file_path}" fayli, "{sheet_name}" varog\'i o\'qilmoqda...'))
            
            # sheet_name int yoki str bo'lishi mumkin
            if isinstance(sheet_name, str) and sheet_name.isdigit():
                 sheet_name = int(sheet_name)
                 
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Ustun nomlarida bo'lishi mumkin bo'lgan bo'shliqlarni olib tashlash
            df.columns = df.columns.str.strip()

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Xatolik: Fayl topilmadi: {file_path}'))
            return
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'Xatolik: Excel faylni o\'qishda muammo yuz berdi. Varog\' nomi/indeksi to\'g\'rimi? Xato: {e}'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Noma\'lum xatolik: {e}'))
            return

        total_rows = len(df)
        created_count = 0
        skipped_count = 0
        
        # 2. Ma'lumotlarni bazaga yuklash
        self.stdout.write(self.style.NOTICE(f'{total_rows} ta qator topildi. Ma\'lumotlar bazaga yuklanmoqda...'))

        # Tranzaksiya ichida ishlash
        # Bu safar har bir qator uchun alohida tranzaksiya ochamiz, shunda bitta xato boshqasiga ta'sir qilmaydi
        # va biz asosiy xato matnini olishimiz mumkin.
        
        for index, row in df.iterrows():
            # Har bir qator uchun alohida atomic blok (bu performance'ga salbiy ta'sir qiladi, 
            # lekin debug qilish uchun zarur)
            try:
                with transaction.atomic():
                    Question.objects.create(
                        # !!! MAYDON NOMINI TEKSHIRING: Excelda 'Modu' ekanligini taxmin qildik, chunki oldin shunga xato bergandi.
                        # Agar Modelda 'Modul' bo'lsa va Excelda ham 'Modul' bo'lsa, uni 'Modul' deb qoldiring.
                        # Hozircha Model maydoni 'Modul' va Excel ustuni 'Modul' deb faraz qildik
                        Modul = row['Modul'], 
                        
                        # !!! MAYDON NOMINI TEKSHIRING: Excelda 'lMavzu' ekanligini taxmin qildik.
                        lMavzu = row['Mavzu'], 
                        
                        Savol_ID = int(row['Savol_ID']), 
                        Savol_Matni = row['Savol_Matni'],
                        Variant_A = row['Variant_A'],
                        Variant_B = row['Variant_B'],
                        Variant_C = row['Variant_C'],
                        Variant_D = row['Variant_D'],
                        
                        # !!! MAYDON NOMINI TEKSHIRING: Sizning Excelingizda to'g'ri javob ustuni nomi qanday?
                        # Agar u 'Tugri_Javob' bo'lsa, pastdagi kod shunday bo'lishi kerak.
                        To_g_ri_Javob = row['Tugri_Javob'], 
                    )
                    created_count += 1
            
            except KeyError as e:
                # Agar Excel ustuni noto'g'ri yozilgan bo'lsa
                self.stdout.write(self.style.ERROR(f"\n!!! JIDDIY XATO (Qator {index+2}) !!!"))
                self.stdout.write(self.style.ERROR(f"Excel ustuni topilmadi: {e}. Excel ustun nomlarini tekshiring."))
                self.stdout.write(self.style.ERROR(f"Mavjud ustunlar: {list(df.columns)}"))
                skipped_count += 1
                break # Agar ustun topilmasa, keyingilarini yuklash ma'nosiz
                
            except (IntegrityError, DataError, ValueError) as e:
                # Agar ma'lumotlar bazasining cheklovlari buzilgan bo'lsa (masalan, takroriy ID yoki matn juda uzun)
                self.stdout.write(self.style.WARNING(f"Qator {index+2} (Excelda) yuklanmadi. ASOSIY XATO: {e}. Savol_ID: {row.get('Savol_ID', 'Nomalum')}"))
                skipped_count += 1
                
            except Exception as e:
                # Boshqa kutilmagan xatolar uchun
                self.stdout.write(self.style.ERROR(f"\n!!! KUTILMAGAN XATO (Qator {index+2}) !!!"))
                self.stdout.write(self.style.ERROR(f"Xato turi: {type(e).__name__} | Xato: {e}"))
                skipped_count += 1
                # Birinchi kutilmagan xatoda to'xtash.
                if created_count + skipped_count == 1:
                    raise e

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Yuklash tugallandi: **{created_count}** tasi yaratildi. ({skipped_count} tasi xatolik bilan o\'tkazib yuborildi)"
        ))
