from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import TestResult, User  # Sizning oddiy User modelingiz
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError # username unique bo'lgani uchun
from question.models import Question
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Avg, Count

# Create your views here.


def welcome_view(request):
    """
    Landing page (Xush kelibsiz) sahifasini ko'rsatish.
    """
    # Agar foydalanuvchi allaqachon tizimda bo'lsa, to'g'ridan-to'g'ri Home sahifasiga yo'naltirish
    if request.user.is_authenticated:
        return redirect('home')
        
    return render(request, 'welcome.html')

def home(request):
    if 'user_id' not in request.session:
        messages.error(request, "Iltimos, avval tizimga kiring.")
        return redirect('login')
        
    user = request.session.get('username')
    return render(request, 'home.html', {'user': user})

# ==================================
# === O'ZGARTIRILGAN FUNKSIYA (MODUL) ===
# ==================================
def modules(request):
    if 'user_id' not in request.session:
        messages.error(request, "Iltimos, avval tizimga kiring.")
        return redirect('login')
    
    # 1. Bazadan barcha noyob modullarni olamiz
    modules_qs = Question.objects.values_list('Modul', flat=True).distinct()
    
    # 2. Python yordamida ularni matn emas, SON sifatida tartiblaymiz
    try:
        # key=int ularni '1', '2', '10' deb to'g'ri tartiblaydi
        modules_sorted = sorted(list(modules_qs), key=int)
    except ValueError:
        # Agar orasida "Maxsus" kabi son bo'lmagan nom bo'lsa,
        # oddiy alfavit bo'yicha tartiblaymiz
        modules_sorted = sorted(list(modules_qs))

    return render(request, 'modules.html', {'modules': modules_sorted})

# ===================================
# === O'ZGARTIRILGAN FUNKSIYA (MAVZU) ===
# ===================================
def themes(request,modul_id):
    if 'user_id' not in request.session:
        messages.error(request, "Iltimos, avval tizimga kiring.")
        return redirect('login')
    
    # 1. Bazadan barcha noyob mavzularni olamiz
    # Eslatma: Bu (values) bizga lug'atlar ro'yxatini qaytaradi:
    # [{'lMavzu': '1'}, {'lMavzu': '10'}, {'lMavzu': '2'}]
    themes_qs = Question.objects.filter(
            Modul=modul_id
        ).values('lMavzu').distinct()

    # 2. Python yordamida sonli tartiblaymiz
    try:
        # Har bir lug'atdan 'lMavzu' qiymatini olib, 'int' ga o'girib tartiblaymiz
        themes_sorted = sorted(list(themes_qs), key=lambda item: int(item['lMavzu']))
    except ValueError:
        # Agar son bo'lmagan nomlar bo'lsa, alfavit bo'yicha tartiblaymiz
        themes_sorted = sorted(list(themes_qs), key=lambda item: item['lMavzu'])
    
    print(themes_sorted)

    return render(request, "themes.html",{"themes": themes_sorted,"modul_id":modul_id})

def do_test(request, modul_id, mavzu_id): 
    """
    Berilgan Modul va Mavzu bo'yicha savollarni tanlaydi va ularni 
    bir sahifada (do_test.html) FORM ko'rinishida yuboradi.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Iltimos, avval tizimga kiring.")
        return redirect('login')
    request.session['mavzu_id'] = mavzu_id
    try:
        # 1. Savollarni bazadan filtrlash
        # BU YERDA HAM MODUL VA MAVZUNI STRING QILIB SOLISHTIRGAN MA'QUL
        all_questions_qs = Question.objects.filter(
            Modul=str(modul_id), 
            lMavzu=str(mavzu_id)
        )
        
        NUM_QUESTIONS_TO_SELECT = 25
        
        # QuerySet'ni ro'yxatga o'tkazish
        questions_list = list(all_questions_qs)
        
        if not questions_list:
            messages.error(request, "Bu Modul va Mavzu uchun savollar topilmadi.")
            # Qaytish uchun to'g'ri URL nomini ishlatamiz (agar sizda 'modules' URL bo'lmasa, uni to'g'rilang)
            return redirect('home') # 'home' ga qaytarish eng xavfsiz
        
        # 2. Savollarni tanlash va aralashtirish
        num_to_sample = min(len(questions_list), NUM_QUESTIONS_TO_SELECT)
        
        # Savollarni tanlab, aralashtiramiz
        random_questions = random.sample(questions_list, num_to_sample)
        total_question = len(random_questions)

        # 3. Savollarni FORM ko'rinishida shablonga yuborish
        context = {
            'modul': modul_id,
            'mavzu': mavzu_id, # Natijani hisoblash uchun kerak bo'lishi mumkin
            'questions': random_questions,
            'total_question': total_question
        }
        
        # Endi 'do_test.html' bu savollarni FORM ichida ko'rsatishi kerak
        return render(request, 'do_test.html', context)
        
    except Exception as e:
        messages.error(request, f"Testni boshlashda kutilmagan xato yuz berdi: {e}")
        return redirect('home')
    

def do_real_test(request):
    if 'user_id' not in request.session:
        messages.error(request, "Iltimos, avval tizimga kiring.")
        return redirect('login')
        
    questions = Question.objects.all()  
    questions = list(questions)  # Convert queryset to list
    random_questions = random.sample(questions, min(len(questions), 25))
    total_question = len(random_questions)
    request.session['total_question'] = total_question
    return render(request, 'do_real_test.html', {'questions': random_questions,'total_question':total_question})


def finish_real_exam_view(request):
    """
    Haqiqiy imtihon javoblarini qabul qiladi, natijani hisoblaydi va TestResultga saqlaydi.
    (Mantiqiy xato tuzatildi va samaradorlik oshirildi)
    """
    if 'user_id' not in request.session:
        messages.error(request, "Iltimos, avval tizimga kiring.")
        return redirect('login')
        
    user_id = request.session['user_id']
    current_user = get_object_or_404(User, id=user_id) 

    if request.method != 'POST':
        return redirect('home')

    try:
        total_questions = request.session.get('total_question', 0)
        
        if total_questions == 0:
            messages.error(request, "Savollar topilmadi. Natija hisoblanmadi.")
            return redirect('home')
        
        # Foydalanuvchi javoblarini POST dan ajratib olish
        user_answers = {} # {question_id: user_answer_value}
        
        for key, value in request.POST.items():
            if key.startswith('q_'):
                try:
                    question_id = int(key.split('_')[1])
                    user_answers[question_id] = value
                except (IndexError, ValueError):
                    continue
        
        score = 0
        
        if user_answers:
            question_ids = list(user_answers.keys())
            
            # To'g'ri javoblarni bazadan Bitta so'rov bilan olish
            questions_from_db = Question.objects.filter(
                Savol_ID__in=question_ids
            )
            
            correct_answers_map = {q.Savol_ID: q.To_g_ri_Javob for q in questions_from_db}

            # Ballni hisoblash
            for q_id, user_ans in user_answers.items():
                if q_id in correct_answers_map and user_ans == correct_answers_map[q_id]:
                    score += 1
        
        # Natijani TestResult modeliga saqlash
        new_result = TestResult.objects.create( 
            user=current_user,
            modul='Real Exam', 
            score=score,
            total_questions=total_questions
        )
        
        # Sessiyani tozalash
        if 'total_question' in request.session:
            del request.session['total_question']
            
        messages.success(request, f"Haqiqiy imtihon yakunlandi. Siz {score} / {total_questions} ball to'pladingiz.")
        
        # Natijalar sahifasiga yo'naltirish
        return redirect('result') 
            
    except Exception as e:
        messages.error(request, f"Natijani saqlashda kutilmagan xato yuz berdi: {e}")
        return redirect('home')

# ====================================================================
# 1. RO'YXATDAN O'TISH FUNKSIYASI (REGISTER)
# ====================================================================
def register_view(request):
    
    """
    Yangi foydalanuvchini ro'yxatdan o'tkazish funksiyasi (Qo'lda boshqariladi).
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 1. Parollar mos kelishini tekshirish
        if password != confirm_password:
            messages.error(request, "Parollar mos kelmadi!")
            return render(request, 'register.html')
        
        # 2. Xavfsizlik: Parolni hashlash
        hashed_password = make_password(password)

        # 3. Yangi foydalanuvchini yaratish va saqlash
        try:
            user = User.objects.create(
                username=username, 
                password=hashed_password # Hashlangan parolni saqlash
            )
            user.save()
            
            messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz. Tizimga kiring.")
            return redirect('login')  # Kirish sahifasiga yo'naltirish
        
        except IntegrityError:
            # username unique bo'lgani uchun
            messages.error(request, "Bu foydalanuvchi nomi allaqachon band.")
            return render(request, 'register.html')
        except Exception as e:
            messages.error(request, f"Ro'yxatdan o'tishda kutilmagan xato: {e}")
            return render(request, 'register.html')
            
    return render(request, 'register.html')

# 2. TIZIMGA KIRISH FUNKSIYASI (LOGIN)

def login_view(request):
    """
    Foydalanuvchini qo'lda tekshirish va sessiyani yaratish funksiyasi.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # 1. Foydalanuvchini username orqali bazadan topish
            user = User.objects.get(username=username)
            
            # 2. Xavfsizlik: Kiritilgan parolni bazadagi hash bilan solishtirish
            if check_password(password, user.password):
                
                # ✅ Muvaffaqiyatli: Sessiyani qo'lda yaratish (Django'ning login funksiyasi o'rniga)
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                
                messages.success(request, f"Xush kelibsiz, {username}!")
                return redirect('home')  # Asosiy sahifaga yo'naltirish
            else:
                # Parol noto'g'ri
                messages.error(request, "Noto'g'ri parol.")
                
        except User.DoesNotExist:
            # Foydalanuvchi topilmasa
            messages.error(request, "Bunday foydalanuvchi nomi mavjud emas.")
            
    return render(request, 'login.html')



# 3. TIZIMDAN CHIQISH FUNKSIYASI (LOGOUT)
def logout_view(request):
    """
    Foydalanuvchining sessiyasini o'chirish.
    """
    # Sessiya ma'lumotlarini o'chirish
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'username' in request.session:
        del request.session['username']
        
    messages.info(request, "Siz tizimdan chiqdingiz.")
    return redirect('login')


def finish_exam_view(request):
    """
    Imtihon javoblarini qabul qiladi, natijani hisoblaydi va TestResultga saqlaydi.
    (Ma'lumotlar turi mos kelmasligi xatosi tuzatildi)
    """
    if 'user_id' not in request.session:
        messages.error(request, "Iltimos, avval tizimga kiring.")
        return redirect('login')
        
    user_id = request.session['user_id']
    current_user = get_object_or_404(User, id=user_id) 

    if request.method != 'POST':
        return redirect('home')
        
    try:
        # 1. Modul ID'sini POST ma'lumotidan olish
        modul_id = request.POST.get('modul_id') # Bu string (masalan, "1")
        
        # 2. Mavzu ID'sini sessiyadan olish
        mavzu_id_int = request.session.get('mavzu_id') # Bu int (masalan, 1)

        if not modul_id:
             messages.error(request, "Modul identifikatori (ID) aniqlanmadi.")
             return redirect('home')
        
        if not mavzu_id_int:
             messages.error(request, "Mavzu identifikatori (ID) topilmadi. Sessiya muddati tugagan bo'lishi mumkin.")
             return redirect('home')

        # === XATO TUZATILDI ===
        # Sessiyadan olingan 'int' ni bazadagi 'CharField' bilan solishtirish uchun 'str' ga o'tkazamiz
        mavzu_id_str = str(mavzu_id_int) 
        
        total_questions = int(request.POST.get('total_question', 0))
        
        if total_questions == 0:
            messages.error(request, "Bu modul uchun savollar topilmadi.")
            return redirect('home')
        
        # 3. Foydalanuvchi javoblarini POST dan ajratib olish
        user_answers = {} # {question_id: user_answer_value}
        
        for key, value in request.POST.items():
            if key.startswith('q_'):
                try:
                    question_id = int(key.split('_')[1])
                    user_answers[question_id] = value
                except (IndexError, ValueError):
                    continue
        
        score = 0
        
        if user_answers:
            question_ids = list(user_answers.keys())
            
            # 4. To'g'ri javoblarni bazadan Bitta so'rov bilan olish
            questions_from_db = Question.objects.filter(
                Savol_ID__in=question_ids,
                Modul=modul_id,          # Bu 'str' (POST dan)
                lMavzu=mavzu_id_str      # Bu ham 'str' (qo'lda o'tkazildi)
            )
            
            correct_answers_map = {q.Savol_ID: q.To_g_ri_Javob for q in questions_from_db}

            # 5. Ballni hisoblash
            for q_id, user_ans in user_answers.items():
                if q_id in correct_answers_map and user_ans == correct_answers_map[q_id]:
                    score += 1
        
        modul_nomi = f"{modul_id}-Modul, {mavzu_id_str}-Mavzu"
        
        # 6. Natijani TestResult modeliga saqlash
        new_result = TestResult.objects.create( 
            user=current_user,
            modul=modul_nomi,
            score=score,
            total_questions=total_questions
        )
        
        # 7. Session dan mavzu_id ni tozalash
        if 'mavzu_id' in request.session:
            del request.session['mavzu_id']
        
        messages.success(request, f"Imtihon yakunlandi. Siz {score} / {total_questions} ball to'pladingiz.")
        
        # 8. Natijalar sahifasiga yo'naltirish
        return redirect('result') 
            
    except Exception as e:
        messages.error(request, f"Natijani saqlashda xato: {e}")
        return redirect('home')


# ====================================================================
# === 1. YANGI MAXSUS TEST UCHUN FUNKSIYA (START) ===
# === (LOGIN TEKSHIRUVI OLIB TASHLANDI) ===
# ====================================================================
def start_special_quiz_view(request):
    """
    Faqat 'Modul=0', 'lMavzu=1' uchun maxsus testni boshlaydi.
    Login shart emas.
    """
    try:
        # Modul va Mavzuni QAT'IY belgilaymiz
        HARDCODED_MODUL = '0'
        HARDCODED_MAVZU = '1'
        
        all_questions_qs = Question.objects.filter(
            Modul=HARDCODED_MODUL, 
            lMavzu=HARDCODED_MAVZU
        )
        
        questions_list = list(all_questions_qs)
        
        if not questions_list:
            messages.error(request, "Maxsus test uchun savollar topilmadi (Modul: 0, Mavzu: 1).")
            # Bosh sahifaga (welcome) qaytaramiz
            return redirect('welcome')
        
        # Bu test uchun 10 ta savol tanlaymiz (yoki hamma topilgan savolni)
        NUM_QUESTIONS_TO_SELECT = 10
        num_to_sample = min(len(questions_list), NUM_QUESTIONS_TO_SELECT)
        
        random_questions = random.sample(questions_list, num_to_sample)
        total_question = len(random_questions)

        context = {
            'questions': random_questions,
            'total_question': total_question
        }
        
        # Yangi shablonga (template) yuboramiz
        return render(request, 'special_quiz.html', context)
        
    except Exception as e:
        messages.error(request, f"Maxsus testni boshlashda kutilmagan xato: {e}")
        return redirect('welcome')

# ====================================================================
# (Qolgan funksiyalar)
# ====================================================================

def stats_dashboard_view(request):
    """
    Foydalanuvchining umumiy statistikasini hisoblaydi va ko'rsatadi.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Iltimos, avval tizimga kiring.")
        return redirect('login')
        
    user_id = request.session['user_id']
    
    # 1. Barcha natijalarni olish
    all_results = TestResult.objects.filter(user_id=user_id).order_by('-date_taken')
    
    # 2. Umumiy Haqiqiy Imtihonlar Statistikasi 
    real_tests = all_results.filter(modul='Real Exam') 
    
    avg_score_percent = 0
    total_real_tests = real_tests.count()
    
    if total_real_tests > 0:
        total_percent = sum((r.score / r.total_questions) * 100 for r in real_tests if r.total_questions > 0)
        avg_score_percent = round(total_percent / total_real_tests)

    # 3. Modullar bo'yicha Statistika (har bir modul uchun o'rtacha ball)
    module_stats = all_results.exclude(modul='Real Exam') \
                              .values('modul') \
                              .annotate(
                                  count=Count('modul'),
                                  avg_score=Avg('score') 
                              ).order_by('modul')

    context = {
        'avg_score_percent': avg_score_percent,
        'total_real_tests': total_real_tests,
        'module_stats': module_stats,
        'all_results_history': all_results[:10], # Oxirgi 10 ta natija tarixi
        'has_results': all_results.exists(),
    }
    
    return render(request, 'stats_dashboard.html', context)