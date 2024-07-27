import random
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from django.db import models


class Bus(models.Model):
    BUS_TYPE_CHOICES = [
        ('Economy Class', 'Economy Class'),
        ('Executive Class', 'Executive Class'),
        ('Business Class', 'Business Class'),
        ('Sleeper Class', 'Sleeper Class'),
        # Add more choices as needed
    ]

    bus_code = models.CharField(max_length=20)
    bus_type = models.CharField(max_length=20, choices=BUS_TYPE_CHOICES)
    
    def __str__(self):
        return f"{self.bus_code}-{self.bus_type}"



class City(models.Model):
    city_name = models.CharField( max_length=50)

    def __str__(self):
        return self.city_name




class Trip(models.Model):
    departure = models.ForeignKey(City, related_name='departure_city', on_delete=models.CASCADE)
    departure_datetime = models.DateTimeField(default=timezone.now)
    destination = models.ForeignKey(City, related_name='destination_city', on_delete=models.CASCADE)
    arrival_datetime = models.DateTimeField(default=timezone.now)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    fare = models.CharField(max_length=15, default='0')
    total_seats = models.IntegerField(default=49)
    available_seats = models.IntegerField(default=49)

    def __str__(self):
        # Convert UTC datetimes to local timezone for display
        departure_datetime_local = timezone.localtime(self.departure_datetime).strftime('%I:%M %p %d-%m-%Y')
        arrival_datetime_local = timezone.localtime(self.arrival_datetime).strftime('%I:%M %p %d-%m-%Y')

        return f"{self.departure} at {departure_datetime_local} to {self.destination} at {arrival_datetime_local}"



    

def generate_reservation_number():
    return str(random.randint(100000, 999999))

class Reservations(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='selected_user', default=1)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='selected_trip', default=1)
    selected_seats = models.CharField(max_length=255, default='', blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    reservation_number = models.CharField(max_length=6, unique=True, editable=False, default=generate_reservation_number)

    def save(self, *args, **kwargs):
        if not self.reservation_number:
            while True:
                reservation_number = str(random.randint(100000, 999999))
                if not Reservations.objects.filter(reservation_number=reservation_number).exists():
                    break

            self.reservation_number = reservation_number

        super().save(*args, **kwargs)



