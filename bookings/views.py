from django.shortcuts import render, get_object_or_404 , redirect 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest,HttpResponseRedirect
from .models import *
from django.db.models import Count
from django.contrib import messages
from.forms import *
from django.db.models import F
from django.utils import timezone
from datetime import date
import datetime
from django.core.mail import send_mail
from django.conf import settings



# Employee Side

# Trip Management

@login_required(login_url='custom_login')
def manage_trip(request):
    today = datetime.date.today()
    trips = Trip.objects.filter(departure_datetime__date__gte=today)

    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_trip')
    else:
        form = TripForm()

    # Handle reservation updates
    if request.method == 'POST' and 'reservation_id' in request.POST:
        reservation_id = request.POST['reservation_id']
        reservation = get_object_or_404(Reservations, pk=reservation_id)

        # Update available seats when a reservation is created or deleted
        Trip.objects.filter(id=reservation.trip.id).update(available_seats=F('available_seats') - reservation.selected_seats)

        # Retrieve the updated trip
        trip = Trip.objects.get(id=reservation.trip.id)
        return render(request, 'bookings/manage_trip.html', {'form': form, 'trips': trips, 'trip': trip}) # Pass the updated trip to the template

    is_authenticated = request.user.is_authenticated
    is_employee = request.user.profile.is_employee if is_authenticated else False
    first_name = request.user.first_name if is_authenticated else ""

    return render(
        request,
        'bookings/manage_trip.html',
        {
            'form': form,
            'trips': trips,
            'today': today,
            'is_authenticated':is_authenticated,
            'first_name': first_name,
            'is_employee': is_employee
        }
    )

# Reservations 
@login_required(login_url='custom_login')
def trip_detail(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    reservations = Reservations.objects.filter(trip=trip)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.trip = trip
            reservation.save()

            # Update available seats when a reservation is created
            selected_seats = request.POST.get('selected_seats', '')
            # if not selected_seats:   Errors in this code i want to stop the form submittion whwn there are no selected seats
            #     return HttpResponseBadRequest("Selected seats cannot be empty")
            selected_seats_list = [int(seat) for seat in selected_seats.split(',') if seat.isdigit()]

            Trip.objects.filter(id=trip_id).update(available_seats=F('available_seats') - len(selected_seats_list))

            # Retrieve the updated trip
            trip = Trip.objects.get(id=trip_id)

            return redirect('trip_detail', trip_id=trip_id)
    else:
        form = ReservationForm()


    # Retrieve already selected seats for this trip
    selected_seats = Reservations.objects.filter(trip=trip).values_list('selected_seats', flat=True)
    # total_fare = trip.fare*trip.total_seats
    # print(total_fare)

    is_authenticated = request.user.is_authenticated
    is_employee = request.user.profile.is_employee if is_authenticated else False
    first_name = request.user.first_name if is_authenticated else ""

    return render(
        request,
        'bookings/trip_detail.html',
        {
            'trip': trip,
            'reservations': reservations,
            'form': form,
            'is_authenticated': is_authenticated,
            'first_name': first_name,
            'is_employee': is_employee,
            'selected_seats': selected_seats
        }
    )



@login_required(login_url='custom_login')
def update_trip(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)

    if request.method == 'POST':
        form = UpdateTrip(request.POST, instance=trip)
        if form.is_valid():
            form.save()
            return redirect('manage_trip')

    form = TripForm(instance=trip)
    return render(request, 'bookings/update_trip.html', {'form': form, 'trip': trip})

@login_required(login_url='custom_login')
def delete_trip(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)

    if request.method == 'POST':
        trip.delete()
        return redirect('manage_trip')

    return render(
        request, 'bookings/delete_trip.html',
        {
            'trip': trip
        }
    )


# Reservations Management


@login_required(login_url='custom_login')
def delete_reservations(request, reservation_id):
    reservation = get_object_or_404(Reservations, reservation_number=reservation_id)

    if request.method == 'POST':
        selected_seats_list = [int(seat) for seat in reservation.selected_seats.split(',') if seat.isdigit()]
        selected_seats_count = len(selected_seats_list)

        Trip.objects.filter(id=reservation.trip.id).update(available_seats=F('available_seats') + selected_seats_count)
        reservation.delete()
        return redirect('trip_detail', trip_id=reservation.trip.id)

    return render(
        request, 'bookings/delete_reservations.html',
        {
            'reservation': reservation
        }
    )




@login_required(login_url='custom_login')
def reservation_history(request):
    # Retrieve trips that have reservations
    trips_with_reservations = Trip.objects.annotate(num_reservations=Count('selected_trip')).filter(num_reservations__gt=0)

    # Create a dictionary to store reservations grouped by trip
    reservations_by_trip = {}

    # Loop through each trip with reservations
    for trip in trips_with_reservations:
        # Retrieve reservations for the current trip
        reservations = Reservations.objects.filter(trip=trip)

        # Store reservations in the dictionary with trip as the key
        reservations_by_trip[trip] = reservations
    
    is_authenticated = request.user.is_authenticated
    is_employee = request.user.profile.is_employee

    return render(
        request, 'bookings/history.html',
        {
            'reservations_by_trip': reservations_by_trip,
            'is_authenticated' : is_authenticated,
            'is_employee': is_employee
        }
    )






# Customer Side

@login_required(login_url='custom_login')
def search_trips(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            departure_city = form.cleaned_data.get('departure_city', '')
            destination_city = form.cleaned_data.get('destination_city', '')
            departure_date = form.cleaned_data.get('departure_date', None)

            if not departure_city and not destination_city and not departure_date :
                messages.warning(request, 'Please provide at least Departure or Destination city or date.')
                return HttpResponseRedirect(request.path_info)
            
            today = date.today()
            trips = Trip.objects.filter(
                departure__city_name__icontains=departure_city,
                destination__city_name__icontains=destination_city,
                departure_datetime__date__gte=today,
                
            )

            if departure_date:
                trips = trips.filter(departure_datetime__date=departure_date)
            

            if trips.exists():
                current_datetime = timezone.now()
                trips = [trip for trip in trips if trip.departure_datetime > current_datetime]
                if not trips:
                    messages.warning(request, 'No Trips Found For Your Desired Date and Time.')
                    return HttpResponseRedirect(request.path_info)
                
                is_authenticated = request.user.is_authenticated
                return render(request, 'bookings/search_results.html', {'trips': trips, 'is_authenticated': is_authenticated})
            else:
                messages.warning(request, 'No trips found for the given cities and date.')
                return HttpResponseRedirect(request.path_info)

    is_authenticated = request.user.is_authenticated
    is_employee = request.user.profile.is_employee if is_authenticated else False
    first_name = request.user.first_name if is_authenticated else ""

    return render(
        request, 'bookings/search_trips.html',
        {
            'form': SearchForm(),
            'is_authenticated': is_authenticated, 
            'first_name': first_name,
            'is_employee': is_employee
        }
    )



@login_required(login_url='custom_login')
def book_ticket(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST)

        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.trip = trip
            reservation.save()

            # Update available seats when a reservation is created
            selected_seats = request.POST.get('selected_seats', '')
            selected_seats_list = [int(seat) for seat in selected_seats.split(',') if seat.isdigit()]

            # selected_seats_int = sum(selected_seats_list)
            trip.available_seats = max(0, int(trip.available_seats) - len(selected_seats_list))
            trip.save()

            subject = 'Reservation Confirmation'
            message = f'Dear {request.user.first_name},\n\nYour reservation for trip: \n\n{trip} with Reservation number: {reservation.reservation_number} has been confirmed.\n\nThank you for choosing our service.\n\nBest regards,\nTravel Company Team'
            recipient_list = [request.user.email]
            sender_email = settings.EMAIL_HOST_USER
            send_mail(subject, message, sender_email, recipient_list)


            # Redirect to the search trips page after booking
            return redirect('bookings')

    else:
        form = ReservationForm()

        # Retrieve already selected seats for this trip
    selected_seats = Reservations.objects.filter(trip=trip).values_list('selected_seats', flat=True)

    is_authenticated = request.user.is_authenticated
    is_employee = request.user.profile.is_employee if is_authenticated else False
    first_name = request.user.first_name if is_authenticated else ""

    return render(
        request, 'bookings/book_ticket.html',
        {
            'trip': trip,
            'form': form,
            'is_authenticated': is_authenticated,
            'first_name': first_name,
            'is_employee': is_employee,
            'selected_seats': selected_seats 
        }
    )


@login_required(login_url='custom_login')
def delete_reservations_customer(request, reservation_id):
    reservation = get_object_or_404(Reservations, reservation_number=reservation_id)

    if request.method == 'POST':
        selected_seats_list = [int(seat) for seat in reservation.selected_seats.split(',') if seat.isdigit()]
        selected_seats_count = len(selected_seats_list)

        Trip.objects.filter(id=reservation.trip.id).update(available_seats=F('available_seats') + selected_seats_count)
        reservation.delete()
        return redirect('dashboard')

    return render(
        request, 'bookings/delete_reservations.html',
        {
            'reservation': reservation
        }
    )

@login_required(login_url='custom_login')
def dashboard(request):
    user_reservations = Reservations.objects.filter(user=request.user)
    is_authenticated = request.user.is_authenticated
    first_name = request.user.first_name if is_authenticated else ""
    current_datetime = timezone.now()
    for reservation in user_reservations:
        reservation.is_deletable = reservation.trip.departure_datetime > current_datetime 

    

    return render(
        request, 'bookings/dashboard.html',
        {
            'user_reservations': user_reservations,
            'is_authenticated': is_authenticated,
            'first_name': first_name,
        }
    )

