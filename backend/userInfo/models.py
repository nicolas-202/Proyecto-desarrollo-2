from django.db import models

# Create your models here.
class DocumentType(models.Model):
    document_type_name = models.CharField(max_length=50, unique=True)
    document_type_code = models.CharField(max_length=4, unique=True)
    document_type_description= models.TextField(blank=True, null=True)
    document_type_is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.document_type_name
    
class Gender(models.Model):
    gender_name = models.CharField(max_length=50, unique=True)
    gender_code = models.CharField(max_length=4, unique=True)
    gender_description= models.TextField(blank=True, null=True)
    gender_is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.gender_name

class PaymentMethodType(models.Model):
    payment_method_type_name = models.CharField(max_length=50, unique=True)
    payment_method_type_code = models.CharField(max_length=4, unique=True)
    payment_method_type_description= models.TextField(blank=True, null=True)
    payment_method_type_is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.payment_method_type_name