from django.db import models


class User(models.Model):
    
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username
    
# myapp/models.py 



class Question(models.Model):
    # E'tibor bering: Bu nomlar KATTA-KICHIK HARFLARGA sezgir
    Modul = models.CharField(max_length=100)  # <-- Katta 'M'
    lMavzu = models.CharField(max_length=150) # <-- Kichik 'l'
    Savol_ID = models.IntegerField()
    Savol_Matni = models.TextField()
    Variant_A = models.CharField(max_length=255)
    Variant_B = models.CharField(max_length=255)
    Variant_C = models.CharField(max_length=255)
    Variant_D = models.CharField(max_length=255)
    

    To_g_ri_Javob = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.Savol_ID} - {self.Savol_Matni[:30]}"
    

class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    modul = models.CharField(max_length=100)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user} - {self.modul} - Score: {self.score}/{self.total_questions}"