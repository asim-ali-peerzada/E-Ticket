from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import *

@shared_task
def update_trips():
    current_date = timezone.now().date()

    # Get the most recent trip before the current date
    last_trip = Trip.objects.filter(
        departure_datetime__lt=current_date
    ).order_by('-departure_datetime').first()

    # Get existing trips for today
    existing_trips_today = Trip.objects.filter(
        departure_datetime__date=current_date
    )

    # Loop over each existing trip for today
    for existing_trip in existing_trips_today:
        # Loop over the next 5 days
        for i in range(5):
            new_date = current_date + timedelta(days=i + 1)

            # Check if a trip already exists for the next 5 days
            existing_trip_next_day = Trip.objects.filter(
                departure=existing_trip.departure,
                destination=existing_trip.destination,
                bus=existing_trip.bus,
                departure_datetime__date=new_date
            ).exists()

            # Create a new trip if one doesn't already exist
            if not existing_trip_next_day:
                new_trip = Trip(
                    departure=existing_trip.departure,
                    destination=existing_trip.destination,
                    bus=existing_trip.bus,
                    fare=last_trip.fare if last_trip else existing_trip.fare,
                    total_seats=existing_trip.total_seats,
                    available_seats=existing_trip.total_seats,
                    departure_datetime=existing_trip.departure_datetime + timedelta(days=i + 1),  # Increase the date by 1 day
                    arrival_datetime=existing_trip.arrival_datetime + timedelta(days=i + 1),
                )
                new_trip.save()

    print('Successfully updated trips for the next 5 days')
