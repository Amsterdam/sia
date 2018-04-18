from django.contrib import admin
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework import routers
from api import views
from api import forms
from rest_framework.documentation import include_docs_urls
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from django.contrib.auth.decorators import user_passes_test

router = routers.DefaultRouter()

router.register(r'signal', views.SignalViewSet,base_name = 'signal')
router.register(r'status', views.StatusViewSet)

FORMS = [("form1",forms.Form1),
         ("formWaternet", forms.FormWaternet),
         ("form2", forms.Form2),
         ("form3", forms.Form3)]

FORMS_INTERN = [("form1Intern",forms.Form1Intern),
         ("formWaternet", forms.FormWaternet),
         ("form2", forms.Form2),
         ("form3", forms.Form3)]

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^logout', views.pagelogout, name='logout'),
    url(r'^login/$', views.login_view,name='login'),
    url(r'^login$', views.login_view,name='login'),
    url(r'^melden-intern/$', views.MeldInternWizard.as_view(FORMS_INTERN),name='melden_intern'),
    url(r'^melden/$', views.MeldInternWizard.as_view(FORMS_INTERN),name='melden_intern'),
    url(r'^$', views.MeldWizard.as_view(FORMS),name='melden'),
    url(r'^status-inzien-tabel/$', views.afhandel, name='afhandel'),
    url(r'^status-inzien-kaart/$', views.afhandel_kaart, name='afhandel_kaart'),
    url(r'^melding/(?P<pk>\d+)$', views.afhandel_detail),
    url(r'^docs/', include_docs_urls(title='Meldingen API',public=False)),
        url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 




