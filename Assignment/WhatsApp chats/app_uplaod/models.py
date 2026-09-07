from django.db import models

# Create your models here.
class WhatsApp(models.Model):
    #name = models.CharField(max_length=50)
    upload_file = models.FileField(upload_to='media/')
