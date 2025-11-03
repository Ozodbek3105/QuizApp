from django.urls import include, path

from question.view_for_excel import upload_excel_view
from question.views import (
    do_real_test, do_test, finish_exam_view, 
    finish_real_exam_view, home, login_view, logout_view, 
    modules, register_view, stats_dashboard_view, themes, 
    welcome_view,
    
    # === IMPORT O'ZGARDI ===
    start_special_quiz_view 
)

urlpatterns = [
    path('', welcome_view, name='welcome'),
    path('home/',home, name='home'),
    path('modules/',modules, name='modules'),
    path('modules/<int:modul_id>/themes/',themes,name='themes'),
    path('modules/<int:modul_id>/themes/do_test/<int:mavzu_id>/',do_test, name='do_test'),
    path('do_real_test/',do_real_test,name='do_real_test'),
    path('register/',register_view,name='register'), 
    path('login/',login_view,name='login'),
    path('logout/',logout_view,name="logout"),
    path('exam_finish/', finish_exam_view, name='finish_exam'),
    path('real_exam_finish/', finish_real_exam_view, name='finish_real_exam'),
    
    # === PATH O'ZGARDI ===
    path('special-quiz/', start_special_quiz_view, name='start_special_quiz'),
    # 'finish_special_quiz' URL endi kerak emas
    
    path('result/', stats_dashboard_view, name='result'),
    # path('check-answer/', check_answer_view, name='check_answer'),
    path('upload/', upload_excel_view, name='upload_page'),
]