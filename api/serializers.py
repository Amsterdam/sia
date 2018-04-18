# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *
import django_filters.rest_framework
from django.contrib.auth.models import User
from rest_framework import permissions

class IsAfhandelaar(permissions.BasePermission):
    ''' Validation to see if user is logged in and part of group Afhandelaar '''
    def has_permission(self, request, view):
        SAFE_METHODS = ('GET','OPTIONS','HEAD')
        if request.user.is_authenticated:
            if request.user.groups.filter(name='Afhandelaar').count() > 0:
                if request.method in permissions.SAFE_METHODS:
                    return True
        return False

class SignalSerializer(serializers.ModelSerializer):   
    ''' Serializer for signal '''
    class Meta:
        model = Signal
        fields = ('id','last_status','adres','datetime','text','waternet_soort_boot','waternet_rederij','waternet_naam_boot','datetime_overlast','afvalapi','email','phone_number','source','afvalapi','text_extra','image','main_category','sub_category','ml_cat','ml_prob','ml_cat_all_prob','ml_sub_cat','ml_sub_prob','ml_sub_all_prob','ml_cat_all','ml_sub_all','adres','stadsdeel','coordinates','verantwoordelijk',)


class StatusSerializer(serializers.ModelSerializer):
    ''' Serializer for status '''
    signal = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Signal.objects.all())
    class Meta:
        model = Status
        fields = ('text','signal','status','extern','datetime','signal','user')

