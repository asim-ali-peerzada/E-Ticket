from django import forms
from .models import *
from datetime import date, timedelta

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['departure', 'departure_datetime', 'destination', 'arrival_datetime', 'bus', 'fare', 'total_seats', 'available_seats']
        # widgets = {
        #     : forms.HiddenInput(),  # This will hide the available seats field in the form
        # }
class UpdateTrip(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['fare']

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservations
        fields = ['name','selected_seats']
        widgets = {
            'trip': forms.HiddenInput(),
            'date_created': forms.HiddenInput(),
        }



class SearchForm(forms.Form):
    departure_city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label="Select departure city")
    destination_city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label="Select destination city")
    departure_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'min': date.today(), 'max': date.today() + timedelta(days=5)}),
    )

