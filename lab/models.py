from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Lab(BaseModel):
    name = models.CharField(max_length=120)
    address = models.CharField(max_length=500)
    pincode = models.CharField(max_length=6)
    email = models.EmailField()


class LabUser(BaseModel):
    is_admin = models.BooleanField(default=False)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class LabPatient(BaseModel):
    GENDER_MAPPING = (
        ('Male', 'MALE'),
        ('Female', 'FEMALE'),
        ('Others', 'OTHERS'),
    )
    first_name = models.CharField(max_length=120)
    email = models.EmailField()
    contact = models.CharField(max_length=13)
    gender = models.CharField(choices=GENDER_MAPPING, max_length=20)
    dob = models.DateField()
    address = models.TextField()
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    lab_user = models.ForeignKey(LabUser, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)


class Bills(BaseModel):
    PAYMENT_MODES = (
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('debit card', 'Debit Card'),
        ('credit card', 'Credit Card'),
        ('cheque', 'Cheque'),
        ('others', 'Others')
    )
    PAYMENT_STATUS = (
        ('due', 'Due'),
        ('paid', 'Paid')
    )
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    total_amount = models.FloatField()
    due = models.FloatField()
    advance = models.FloatField(max_length=50)
    patient = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    lab_user = models.ForeignKey(LabUser, on_delete=models.DO_NOTHING)
    lab = models.ForeignKey(Lab, on_delete=models.DO_NOTHING)


class Tests(BaseModel):
    TESTS_NAME_MAPPING = (
        ('cbc', 'CBC'),
        ('liver function', 'Liver Function'),
        ('cholesterol profile', 'Cholesterol Profile'),
        ('urinalysis', 'Urinalysis')
    )
    TESTS_STATUS = (
        ('pending', 'Pending'),
        ('competed', 'Competed'),
    )
    name = models.CharField(max_length=120, choices=TESTS_NAME_MAPPING)
    price = models.FloatField()
    tests_status = models.CharField(max_length=50, choices=TESTS_STATUS, default='pending')
    bill = models.ForeignKey(Bills, on_delete=models.DO_NOTHING)
    lab = models.ForeignKey(Lab, on_delete=models.DO_NOTHING)
    patient = models.ForeignKey(User, on_delete=models.DO_NOTHING)


class CBCTest(BaseModel):
    hemoglobin = models.DecimalField(max_digits=5, decimal_places=2)
    wbc_count = models.DecimalField(max_digits=7, decimal_places=2)
    rbc_count = models.DecimalField(max_digits=7, decimal_places=2)
    platelet_count = models.PositiveIntegerField()
    test = models.ForeignKey(Tests, on_delete=models.DO_NOTHING)


class UrinalysisTest(BaseModel):
    color = models.CharField(max_length=20)
    appearance = models.CharField(max_length=50)
    ph = models.DecimalField(max_digits=4, decimal_places=2)
    test = models.ForeignKey(Tests, on_delete=models.DO_NOTHING)


class CholesterolProfileTest(BaseModel):
    total_cholesterol = models.DecimalField(max_digits=5, decimal_places=2)
    hdl_cholesterol = models.DecimalField(max_digits=5, decimal_places=2)
    ldl_cholesterol = models.DecimalField(max_digits=5, decimal_places=2)
    triglycerides = models.DecimalField(max_digits=5, decimal_places=2)
    test = models.ForeignKey(Tests, on_delete=models.DO_NOTHING)


class LiverFunctionTest(BaseModel):
    alt = models.DecimalField(max_digits=5, decimal_places=2)
    ast = models.DecimalField(max_digits=5, decimal_places=2)
    total_bilirubin = models.DecimalField(max_digits=5, decimal_places=2)
    direct_bilirubin = models.DecimalField(max_digits=5, decimal_places=2)
    test = models.ForeignKey(Tests, on_delete=models.DO_NOTHING)
