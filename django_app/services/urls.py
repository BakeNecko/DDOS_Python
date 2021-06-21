from django.urls import path

from .views import (get_aircrafts, get_flight_delays, get_flights,
                    get_ticket_flights, get_ticket_transfer_info)

urlpatterns = [
    path('get_aircrafts/', get_aircrafts),
    path('get_flight_delays/', get_flight_delays),
    path('get_ticket_transfer_info/', get_ticket_transfer_info),
    path('get_ticket_flights/', get_ticket_flights),
    path('get_flights/', get_flights),
]
