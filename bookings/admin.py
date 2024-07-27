# admin.py
from django.contrib import admin
from .models import Reservations, Bus, City, Trip


class TripAdmin(admin.ModelAdmin):
    list_display = ('departure', 'departure_datetime', 'destination', 'arrival_datetime', 'bus', 'fare', 'total_seats', 'available_seats')



class ReservationsAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'selected_seats', 'reservation_number', 'trip','date_created')

admin.site.register(Reservations, ReservationsAdmin)  # Register the model and the admin class
admin.site.register(Bus)
admin.site.register(City)
admin.site.register(Trip, TripAdmin)