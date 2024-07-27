# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('manage_trip/', manage_trip, name='manage_trip'),
    path('update_trip/<int:trip_id>/', update_trip, name='update_trip'),
    path('delete_trip/<int:trip_id>/', delete_trip, name='delete_trip'),
    path('trip/<int:trip_id>/',trip_detail, name='trip_detail'),
    path('delete_reservations/<int:reservation_id>/', delete_reservations, name='delete_reservations'),
    path('reservation_history/', reservation_history, name='reservation_history'),
    path('search/', search_trips, name='search_trips'),
    path('book/<int:trip_id>/', book_ticket, name='book_ticket'),
    path('delete_reservations_customer/<int:reservation_id>/', delete_reservations_customer, name='delete_reservations_customer'),
    path('dashboard/', dashboard, name='dashboard'),
]