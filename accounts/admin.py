from django.contrib import admin

# Register your models here.
from .models import *

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number',  'is_employee')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'date')

admin.site.register(Profile,ProfileAdmin)
admin.site.register(Contact, ContactAdmin)