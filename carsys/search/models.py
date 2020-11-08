"""
python manage.py inspectdb > search/models.py
"""
from django.db import models


class Car(models.Model):
    no = models.AutoField(primary_key=True)
    carno = models.CharField(unique=True, max_length=10)
    owner = models.CharField(max_length=20)
    brand = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'tb_car'


class Record(models.Model):
    no = models.AutoField(primary_key=True)
    reason = models.CharField(max_length=200)
    punish = models.CharField(max_length=200)
    makedate = models.DateField()
    dealt = models.BooleanField(blank=True, default=False)
    # car_id
    car = models.ForeignKey(to=Car, on_delete=models.DO_NOTHING)
    is_deleted = models.BooleanField(default=False)
    deleted_time = models.DateTimeField(blank=True, null=True)
    updated_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tb_record'
