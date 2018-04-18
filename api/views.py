# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import *
from .models import *
from .forms import *
from django.shortcuts import redirect
import requests
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from django_filters import Filter
from django_filters.fields import Lookup


class ListFilter(Filter):
    ''' filter that allows filtering on a list usng , as separator '''
    def filter(self, qs, value):
        value_list = value.split(u',')
        return super(ListFilter, self).filter(qs, Lookup(value_list, 'in'))


class SignalFilter(django_filters.FilterSet):
    ''' filter for signals '''
    email = django_filters.CharFilter(name="email", lookup_expr=("icontains"))
    phone_number = django_filters.CharFilter(name="phone_number", lookup_expr=("icontains"))
    id = django_filters.CharFilter(name="id", lookup_expr=("icontains"))
    datetime = django_filters.CharFilter(name="datetime", lookup_expr=("icontains"))
    adres = django_filters.CharFilter(name="adres", lookup_expr=("icontains"))
    stadsdeel = ListFilter(name='stadsdeel')
    sub_category = ListFilter(name='sub_category')
    last_status = ListFilter(name='last_status')
    
    class Meta:
        model = Signal
        fields = ['email','phone_number','id','datetime']

class SignalViewSet(viewsets.ModelViewSet):
    """ API endpoint to view signals """
    permission_classes = (IsAfhandelaar,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = SignalFilter
    queryset = Signal.objects.all().order_by('-datetime')
    serializer_class = SignalSerializer

class StatusViewSet(viewsets.ModelViewSet):
    """ API endpoint to view status """
    permission_classes = (IsAfhandelaar,)
    queryset = Status.objects.all()
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('signal',)
    serializer_class = StatusSerializer

def afhandel(request):
    ''' View for status table screen '''
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Afhandelaar').count() > 0:
            return render(request,'afhandel.html')

    return render(request,'no_auth.html') # change to redirect

def afhandel_kaart(request):
    ''' View for status map screen '''
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Afhandelaar').count() > 0:
            return render(request,'afhandel_kaart.html')

    return render(request,'no_auth.html') # change to redirect




def afhandel_detail(request,pk):
    ''' view for signal detail view '''
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Afhandelaar').count() > 0:


            if 'sub_category' in request.POST and request.method == "POST":


                form = CategoryForm(request.POST)

                if form.is_valid():
                    new = form.save(commit=False)
                    signal = Signal.objects.get(pk=pk)


                    if new.sub_category !=signal.sub_category:
                        status = Status(signal=signal,status='i',text='Subrubriek gewijzigd naar '+ new.sub_category + '.',extern=False,user='system')
                        signal.last_status = 'i'

                        signal.save()
                        status.save()

                    signal.main_category = new.main_category
                    signal.sub_category = new.sub_category

                    signal.save()
                    return redirect('/melding/'+str(pk)) # redirect toevoegen

            if request.method == "POST":
                form = StatusForm(request.POST)
                if form.is_valid():
                    status = form.save(commit=False)
                    status.signal=Signal.objects.get(pk=pk)
                    status.extern = False
                    status.user = request.user.username

                    signal = status.signal
                    signal.last_status  = status.status

                    signal.save()
                    status.save()
                    

                    return redirect('/melding/'+str(pk)) # redirect toevoegen

            return render(request,'afhandel_detail.html' ,{'pk':pk,'StatusForm':StatusForm,'CategoryForm':CategoryForm})
    return render(request,'no_auth.html') # change to redirect


def getafvalapi(coords):
    ''' Function that attempts to retrieve 'afval api' data based on coordinates POINT(0.0 0.0) '''
    try:
        lat = coords.split(' ')[2].replace(')','')
        lon = coords.split(' ')[1].replace('(','')
        r = requests.get('https://api.data.amsterdam.nl/afvalophaalgebieden/search/?lat='+lat+'&lon='+lon)

        return r.json()['result']
    except:
        return 'Fout ophalen stadsdeel'

def getafvalapi_stadsdeel(afvalapi):
    ''' Function that retrieves stadsdeel from afval api '''
    a = afvalapi
    if a == 'Fout ophalen stadsdeel':
        return 'Geen stadsdeel'
    try:
        return afvalapi['features'][0]['properties']['stadsdeel_naam']
    except:
        return 'Geen stadsdeel'
    return 'Geen stadsdeel'


from formtools.wizard.views import SessionWizardView

def get_ml_classification(text):
    ''' function that makes a call to flask api running on /predict to classifiy text '''
    text = text.replace('\r',' ').replace('\n',' ')
    r = requests.post('https://formulier-watermelding.amsterdam/predict', data = {'text':text})

    return r.json()


def condition_waternet(wizard):
    """ Return True if additional waternet form should be shown """
    cleaned_data = wizard.get_cleaned_data_for_step('form1') or 'skip'

    if cleaned_data == 'skip':
        return True


    ml_all = get_ml_classification(cleaned_data['text'])

    ml_main_cat = ml_all['hoofdrubriek'][0][0]
    ml_main_prob =  ml_all['hoofdrubriek'][1][0]

    ml_sub_cat = ml_all['subrubriek'][0][0]
    ml_sub_prob =  ml_all['subrubriek'][1][0]

    if float(ml_sub_prob) > 0.5 and  ml_main_cat!='melding openbare ruimte':
        if ml_sub_cat in ['Snel varen','Geluid','Scheepvaart nautisch toezicht']:
            return True
    return False


class MeldWizard(SessionWizardView):
    ''' The main external form wizard '''
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'images'))
    condition_dict= {'formWaternet': condition_waternet}

    def get_template_names(self):
       
        return 'melden.html'

    def get_context_data(self, form, **kwargs):
        context = super(MeldWizard, self).get_context_data(form=form, **kwargs)
        alldata = self.get_all_cleaned_data()

        context[str('wizard')].update({'alldata':alldata})

        if alldata == {}:
            return context


        ml_all = get_ml_classification(alldata['text'])

        text = ''
        if ml_all['subrubriek'][1][0] > 0.7:

            text = ''
            if ml_all['subrubriek'][0][0] in ['Snel varen','Geluid','Scheepvaart nautisch toezicht']:
                text = 'Bijvoorbeeld: de kleur(en) van de boot, het aantal passagiers, de vaarrichting, Y of Vignet nummer etc.'

            if ml_all['subrubriek'][0][0] in ['Gezonken boot']:
                text = 'Bijvoorbeeld: lekt er zichtbaar olie of levert de situatie gevaar op voor andere boten.'

        context[str('wizard')].update({'hint_text':text})

        context[str('wizard')].update({'rondvaart':ml_all['rondvaart'][0][0][0].lower()})
        
        return context

    def done(self, form_list, **kwargs):
        data = {k: v for form in form_list for k, v in form.cleaned_data.items()}

        instance = Signal.objects.create(**data)

        status = Status(signal=instance,text='Melding is aangemaakt',status='m',extern=False,user='system')
        status.save()

        signal = instance
        signal.last_status = 'm'
        signal.source = 'Webformulier'

        ml_all = get_ml_classification(signal.text)

        signal.ml_cat = ml_all['hoofdrubriek'][0][0]
        signal.ml_prob =  ml_all['hoofdrubriek'][1][0]

        if signal.ml_cat == 'melding openbare ruimte' and signal.ml_prob>0.8:
            signal.waternet_soort_boot = 'Nee'
            signal.waternet_rederij = 'Onbekend'
            signal.waternet_naam_boot = ''
        signal.save()
        signal.ml_prob =  ml_all['hoofdrubriek'][1][0]

        signal.ml_cat_all = '|'.join(ml_all['hoofdrubriek'][0])

        signal.ml_cat_all_prob = '|'.join([str(x) for x in ml_all['hoofdrubriek'][1]])

        signal.ml_sub_cat =   ml_all['subrubriek'][0][0]

        signal.ml_sub_prob =  ml_all['subrubriek'][1][0]

        signal.ml_sub_all =  '|'.join(ml_all['subrubriek'][0])

        signal.ml_sub_all_prob = '|'.join([str(x) for x in ml_all['subrubriek'][1]])

        signal.coordinates = signal.coordinates.replace(',','')
        
        signal.afvalapi = getafvalapi(signal.coordinates)

        signal.stadsdeel = getafvalapi_stadsdeel(signal.afvalapi)
        if float(signal.ml_sub_prob)>0.7:
            signal.sub_category = signal.ml_sub_cat
            status = Status(signal=signal,status='i',text='Subrubriek automatisch herkent als '+ str(signal.sub_category) + '.',extern=False,user='system')
            signal.last_status = 'i'
            status.save()


        signal.save()

        text =  '<p>We geven uw melding door aan onze handhavers. Door uw melding weten wij waar en wanneer u overlast ervaart.</p>'
        text += '<p>Blijf overlast aan ons melden. Ook als we niet altijd direct iets voor u kunnen doen. We gebruiken alle meldingen om overlast in de toekomst te kunnen beperken.</p>'
        if signal.sub_category in ['Snel varen','Geluid']:
            text = '<p>We geven uw melding door aan de handhavers. Als dat mogelijk is ondernemen zij direct actie, maar zij kunnen niet altijd snel genoeg aanwezig zijn. </p>'
            text +=  '<p>Blijf overlast aan ons melden. Ook als we niet altijd direct iets voor u kunnen doen. We gebruiken alle meldingen om overlast in de toekomst te kunnen beperken.</p>'

        if signal.sub_category in ['Gezonken boot']:
            text = '<p>We geven uw melding door aan onze handhavers. Zij beoordelen of het nodig is direct actie te ondernemen. Bijvoorbeeld omdat er olie lekt of omdat de situatie gevaar oplevert voor andere boten.</p>'
            text += '<p>Als er geen directe actie nodig is, dan pakken we uw melding op buiten het vaarseizoen (september - maart).</p>'
            text += '<p>Bekijk <a href="https://www.waternet.nl/actueel/kennisgevingen/" style="color:red;text-decoration:underline">in welke situaties we een wrak weghalen</a>. Boten die vol met water staan, maar nog wél drijven, mogen we bijvoorbeeld niet weghalen.</p>'



        return render(self.request, 'melden_confirm_extern.html', {'signal': signal,'bedankttekst':text})

def condition_waternet_intern(wizard):
    """ Return True if additional waternet form should be shown """
    cleaned_data = wizard.get_cleaned_data_for_step('form1Intern') or 'skip'

    if cleaned_data == 'skip':
        return True

    ml_all = get_ml_classification(cleaned_data['text'])

    ml_main_cat = ml_all['hoofdrubriek'][0][0]
    ml_main_prob =  ml_all['hoofdrubriek'][1][0]

    ml_sub_cat = ml_all['subrubriek'][0][0]
    ml_sub_prob =  ml_all['subrubriek'][1][0]

    if float(ml_sub_prob) > 0.5 and  ml_main_cat!='melding openbare ruimte':
        if ml_sub_cat in ['Snel varen','Geluid','Scheepvaart nautisch toezicht']:
            return True
    return False

class MeldInternWizard(SessionWizardView):
    ''' The main internal form wizard '''
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'images'))
    condition_dict= {'formWaternet': condition_waternet_intern}

    def get_template_names(self):
       
        return 'melden_intern.html'

    def get_context_data(self, form, **kwargs):
        context = super(MeldInternWizard, self).get_context_data(form=form, **kwargs)
        alldata = self.get_all_cleaned_data()

        context[str('wizard')].update({'alldata':alldata})

        if alldata == {}:
            return context


        ml_all = get_ml_classification(alldata['text'])

        text = ''
        if ml_all['subrubriek'][1][0] > 0.7:

            text = ''
            if ml_all['subrubriek'][0][0] in ['Snel varen','Geluid','Scheepvaart nautisch toezicht']:
                text = 'Bijvoorbeeld: de kleur(en) van de boot, het aantal passagiers, de vaarrichting, Y of Vignet nummer etc.'

            if ml_all['subrubriek'][0][0] in ['Gezonken boot']:
                text = 'Bijvoorbeeld: lekt er zichtbaar olie of levert de situatie gevaar op voor andere boten.'

        context[str('wizard')].update({'hint_text':text})

        context[str('wizard')].update({'rondvaart':ml_all['rondvaart'][0][0][0].lower()})
        
        return context

    def done(self, form_list, **kwargs):
        data = {k: v for form in form_list for k, v in form.cleaned_data.items()}

        instance = Signal.objects.create(**data)

        status = Status(signal=instance,text='Melding is aangemaakt',status='m',extern=False,user='system')
        status.save()

        signal = instance
        signal.last_status = 'm'
        

        ml_all = get_ml_classification(signal.text)

        signal.ml_cat = ml_all['hoofdrubriek'][0][0]
        signal.ml_prob =  ml_all['hoofdrubriek'][1][0]

        if signal.ml_cat == 'melding openbare ruimte' and float(signal.ml_prob)>0.7:
            signal.waternet_soort_boot = 'Nee'
            signal.waternet_rederij = 'Onbekend'
            signal.waternet_naam_boot = ''
        signal.save()
        signal.ml_prob =  ml_all['hoofdrubriek'][1][0]

        signal.ml_cat_all = '|'.join(ml_all['hoofdrubriek'][0])

        signal.ml_cat_all_prob = '|'.join([str(x) for x in ml_all['hoofdrubriek'][1]])

        signal.ml_sub_cat =   ml_all['subrubriek'][0][0]

        signal.ml_sub_prob =  ml_all['subrubriek'][1][0]

        signal.ml_sub_all =  '|'.join(ml_all['subrubriek'][0])

        signal.ml_sub_all_prob = '|'.join([str(x) for x in ml_all['subrubriek'][1]])

        signal.coordinates = signal.coordinates.replace(',','')
        signal.afvalapi = getafvalapi(signal.coordinates)

        signal.stadsdeel = getafvalapi_stadsdeel(signal.afvalapi)
        if float(signal.ml_sub_prob)>0.7:
            signal.sub_category = signal.ml_sub_cat
            status = Status(signal=signal,status='i',text='Subrubriek automatisch herkent als '+ str(signal.sub_category) + '.',extern=False,user='system')
            signal.last_status = 'i'
            status.save()


        signal.save()

        text =  '<p>We geven uw melding door aan de handhavers. Door uw melding weten wij waar en wanneer er overlast wordt ervaren. We bekijken alle meldingen om de handhaving te verbeteren en overlast in de toekomst te beperken.</p>'
        if signal.sub_category in ['Snel varen','Geluid']:
            text = '<P>We geven uw melding door aan de handhavers. Als dat mogelijk is ondernemen zij direct actie, maar zij kunnen niet altijd snel genoeg aanwezig zijn. </p>'
            text +=  '<p>We bekijken alle meldingen om de handhaving te verbeteren en overlast in de toekomst te beperken.</p>'

        if signal.sub_category in ['Gezonken boot']:
            text = '<p>We geven uw melding door aan de handhavers. Zij beoordelen of het nodig is direct actie te ondernemen. Bijvoorbeeld omdat er olie lekt of omdat de situatie gevaar oplevert voor andere boten. </p>'
            text += '<p>Als er geen directe actie nodig is, dan wordt de melding buiten het hoogseizoen afgehandeld. Op de <a href="https://www.waternet.nl/actueel/kennisgevingen/" style="color:red;text-decoration:underline">webpagina van waternet</a>  geven we aan wanneer wij een wrak laten weghalen.</p>'
            text += '<p>Let op: Een boot die vol met water staat, kan soms nog wel drijven. Deze boten mogen wij niet laten weghalen. </p>'
        return render(self.request, 'melden_confirm.html', {'signal': signal,'bedankttekst':text})

from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

def pagelogout(request):
    ''' logout page '''
    logout(request)
    return render(request,'logout.html')


def login_view(request):
    ''' view for login '''
    form = LoginForm(request.POST or None)
    if request.POST and form.is_valid():
        user = form.login(request)
        if user:
            login(request, user)
            return HttpResponseRedirect("/status-inzien-tabel/")
    return render(request, 'login.html', {'login_form': form })