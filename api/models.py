# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import uuid

class Signal(models.Model):
    """ Model representing a signal """
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=1000,default='')
    text_extra = models.CharField(max_length=1000,default='',blank=True)
    coordinates = models.CharField(max_length=100,default='POINT (0.0 0.0)')
    datetime = models.DateTimeField(auto_now_add=True,null=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=17, blank=True) 
    source = models.CharField(max_length=15,default='api')
    main_category = models.CharField(max_length=50,default='',blank=True)
    sub_category = models.CharField(max_length=50,default='',blank=True)
    ml_cat = models.CharField(max_length=50,default='',blank=True)
    ml_prob = models.CharField(max_length=50,default='',blank=True)
    ml_cat_all = models.CharField(max_length=500,default='',blank=True)
    ml_cat_all_prob = models.CharField(max_length=500,default='',blank=True)
    ml_sub_cat = models.CharField(max_length=500,default='',blank=True)
    ml_sub_prob = models.CharField(max_length=500,default='',blank=True)
    ml_sub_all = models.CharField(max_length=500,default='',blank=True)
    ml_sub_all_prob = models.CharField(max_length=500,default='',blank=True)
    stadsdeel = models.CharField(max_length=500,default='',blank=True)
    afvalapi = models.CharField(max_length=5000,default='',blank=True)
    image = models.ImageField(upload_to = 'images/',null=True,blank=True )
    soorten = ((x,x) for x in (('Ja'),('Nee'),))
    waternet_soort_boot = models.CharField(max_length=50, choices=soorten,default=('Nee','Nee'))
    datetime_overlast = models.DateTimeField(auto_now_add=False,null=True)
    waternet_rederij = models.CharField(max_length=100,default='',blank=True)
    waternet_naam_boot = models.CharField(max_length=500,default='',blank=True)
    adres = models.CharField(max_length=500,default='')
    user = models.CharField(max_length=200,default='',null=True)
    last_status = models.CharField(max_length=1,default='m')

    @property
    def verantwoordelijk(self):
    	if self.sub_category != 'Geluid':
    		return 'Waternet'
    	if self.stadsdeel.lower() in ['centrum','west']:
    		return 'Waternet'
    	if self.stadsdeel.lower() in ['zuidoost','nieuw-west','noord','oost','zuid']:
    		return 'Stadsdeel '+ self.stadsdeel
    	return 'Waternet'
   
    class Meta:
        verbose_name_plural = "Signalen"
        get_latest_by = "datetime"
        ordering = ['datetime']

    def __str__(self):
        return self.text

class Status(models.Model):
    """	Model representing a signal	"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    signal= models.ForeignKey('Signal', on_delete=models.SET_NULL, null=True,related_name='Signal') 
    datetime = models.DateTimeField(auto_now_add=True,null=True)
    text = models.CharField(max_length=1000,default='')
    user = models.CharField(max_length=200,default='',null=True)
    STATUS = (
        ('m', 'Gemeld'),
        ('i', 'In afwachting van behandeling'),
        ('o', 'Afgehandeld')
    )
    status = models.CharField(max_length=1, choices=STATUS, blank=True, default='m', help_text='Melding status')
    extern = models.BooleanField(default=False,help_text='Wel of niet status extern weergeven')

    class Meta:
        verbose_name_plural = "Statussen"
        get_latest_by = "datetime"

    def __str__(self):
        return self.text

class Rederij(models.Model):
    ''' Model representing the waternetform rederijen '''
    naam = models.CharField(max_length=500)
    class Meta:
        verbose_name_plural = "Rederijen"

class Source(models.Model):
    ''' Model representing all possible sources '''
    naam = models.CharField(max_length=500)
    class Meta:
        verbose_name_plural = "Bronnen"