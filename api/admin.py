# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *

@admin.register(Status)
class statusAdmin(admin.ModelAdmin):
	list_display = ('text','datetime')

class statusInline(admin.TabularInline):
	model = Status
	extra = 0

@admin.register(Signal)
class signalAdmin(admin.ModelAdmin):
	inlines = [statusInline]
	list_display = ('text','datetime')

@admin.register(Rederij)
class rederijAdmin(admin.ModelAdmin):
	list_display = ('naam',)

@admin.register(Source)
class sourceAdmin(admin.ModelAdmin):
	list_display = ('naam',)


