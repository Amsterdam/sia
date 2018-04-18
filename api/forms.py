# -*- coding: utf-8 -*-

from django import forms
from .models import *
from datetimewidget.widgets import DateTimeWidget
from django.http import HttpResponseRedirect
from formtools.wizard.views import SessionWizardView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import datetime

class CategoryForm(forms.ModelForm):
    ''' Form for changing category of signal '''
    class Meta: 
        model = Signal
        fields = ('sub_category',)

class StatusForm(forms.ModelForm):
    ''' Form for adding new status to signal '''
    class Meta:
        model = Status
        fields = ('text','status','extern')
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

class Form1(forms.Form):
    ''' First form of making a citizen report, asking for text and location '''
    text = forms.CharField(max_length=1000,widget=forms.Textarea(attrs={'style':'width:100%','max_length':1000}),label='Omschrijf de overlast op het water')
    coordinates = forms.CharField(max_length=400)
    adres = forms.CharField(max_length=200,label='Geef de locatie aan met een adres of door op de kaart te slepen.')

class Form1Intern(forms.Form):
    ''' First form of making a internal report, asking for text and location and source, used by 14020 '''
    OPTIONS = ((x.naam,x.naam) for x in Source.objects.all())
    source=  forms.ChoiceField(choices=OPTIONS,label='Hoe komt de melding binnen?',required=False)
    text = forms.CharField(max_length=1000,widget=forms.Textarea(attrs={'max_length':1000}),label='Omschrijf de overlast op het water')
    coordinates = forms.CharField(max_length=400)
    adres = forms.CharField(max_length=200,label='Geef de locatie aan met een adres of door op de kaart te slepen.')
    
dateTimeOptions = {
'format': 'dd/mm/yyyy HH:ii P',
'autoclose': True,
'showMeridian' : False,
'pickerPosition' : 'bottom-left',
#'endDate' : str(datetime.date.today() + datetime.timedelta(days=1)),
}

from django.core.exceptions import ValidationError

def file_size(value): # add this to some file where you can import it from
    limit = 50 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Het bestand is groter dan toegestaan, afbeeldingen mogen niet groter dan 50 MB zijn.')

class Form2(forms.Form):
    ''' Second form of making a report, asking for time, image and extra text '''
    datetime_overlast = forms.DateTimeField(label='Wanneer deed het probleem zich voor? (niet verplicht)',required=False,widget=DateTimeWidget(attrs={'id':"yourdatetimeid",'type':'datetime'}, usel10n = True, bootstrap_version=3,options = dateTimeOptions))
    image = forms.ImageField(required=False,label='Afbeelding (niet verplicht)',validators=[file_size])
    text_extra = forms.CharField(required=False,label='Heeft u nog extra informatie? (niet verplicht)',max_length=1000,widget=forms.Textarea(attrs={'rows': 3,'style':'width:100%','max_length':1000}))

class FormWaternet(forms.Form):
    ''' Form that is added when citizen report is about 'Geluid','Snelheid' or 'Nautisch toezicht' of 'Overlast op het water '''
    OPTIONS = (
            ("j", "Ja"),
            ("n", "Nee"),
            )    
    waternet_soort_boot =  forms.ChoiceField(choices=OPTIONS,initial='n',label='Gaat de melding over een rondvaartboot?',required=False, widget=forms.Select(attrs={'class':'waternet_soort_boot select-picker'}))
    OPTIONS = ['Onbekend'] + [x.naam for x in Rederij.objects.all()]
    OPTIONS = ((x,x) for x in OPTIONS)
    waternet_rederij =  forms.ChoiceField(choices=OPTIONS,label='Rederij',required=False, widget=forms.Select(attrs={'class':'waternet_rederij select-picker','data-live-search':'true'}))
    waternet_naam_boot = forms.CharField(max_length=400, required=False,widget=forms.Textarea(attrs={'rows': 1,'class':'waternet_naam_boot','style':'width:100%'}),label='Naam van de boot (niet verplicht)')

class Form3(forms.Form):
    ''' Last form, asking for contact information '''
    email = forms.EmailField(max_length=100, required=False,label='Uw e-mailadres (niet verplicht)',widget=forms.Textarea(attrs={'rows': 1,'class':'waternet_naam_boot'}))
    phone_number = forms.CharField(max_length=15, required=False,label='(Mobiel) telefoonnummer (niet verplicht)',widget=forms.Textarea(attrs={'rows': 1,'class':'waternet_naam_boot'}))

from django.contrib.auth import authenticate  

class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True,label='Gebruikersnaam')
    password = forms.CharField(widget=forms.PasswordInput, required=True,label='Wachtwoord')

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("De combinatie van gebruikersnaam en wachtwoord is niet correct.")
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user