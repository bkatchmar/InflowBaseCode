from __future__ import unicode_literals
from django.db import models

class Currency(models.Model):
    IdCurrency = models.AutoField(primary_key=True,verbose_name="IdCurrency",default=1)
    Country = models.CharField(max_length=100,verbose_name="Country",default="United States")
    Name = models.CharField(max_length=100,verbose_name="Name",default="Dollar")
    Code = models.CharField(max_length=100,verbose_name="Code",default="USD")
    
    def __str__(self):
        return self.Code
    
    def FullName(self):
        return ("%s %s" % (self.Country, self.Name))
    
    class Meta:
       db_table = 'Currency'
       
class Country(models.Model):
    IdCountry = models.AutoField(primary_key=True,verbose_name="IdCountry",default=1)
    Name = models.CharField(max_length=100,verbose_name="Name",default="United States")
    Code = models.CharField(max_length=5,verbose_name="Code",default="US")
    PrimaryCurrency = models.ForeignKey(Currency,unique=False,verbose_name="PrimaryCurrency")
    
    def __str__(self):
        return self.Name
    
    class Meta:
        db_table = 'Country'