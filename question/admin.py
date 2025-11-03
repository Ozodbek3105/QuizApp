from django.contrib import admin

# Register your models here.

admin.site.site_header = "Savol-Javob Admin"
admin.site.site_title = "Savol-Javob Sayti Admin Paneli"
admin.site.index_title = "Savol-Javob Saytining Boshqaruv Paneli"
from .models import User, Question, TestResult
admin.site.register(User)
admin.site.register(Question)
admin.site.register(TestResult)
