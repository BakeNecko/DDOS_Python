from django.db import connection
from django.http import HttpRequest, JsonResponse

from .models import AircraftsData


def get_aircrafts(request: HttpRequest, *args, **kwargs):
    """ Получить списки самолётов, которые взлетают/приземляются в аэропорте"""
    limit = request.GET.get('limit', 10)

    return JsonResponse(data=[{
        'aircraft_code': item.aircraft_code,
        'model': item.model,
        'range': item.range,
    } for item in AircraftsData.objects.raw(f'SELECT aircraft_code, model, range from aircrafts_data LIMIT {limit}')], safe=False)


def get_flight_delays(request: HttpRequest, *args, **kwargs):
    """На каких маршрутах произошли самые длительные задержки рейсов"""
    limit = request.GET.get('limit', 10)
    sql_query = f"""
    SELECT f.flight_no,f.scheduled_departure,f.actual_departure,f.actual_departure - f.scheduled_departure AS delay FROM flights f 
    WHERE  f.actual_departure IS NOT NULL 
    ORDER BY f.actual_departure - f.scheduled_departure DESC
    LIMIT {limit};
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        row = cursor.fetchall()
    return JsonResponse(data=[{
        'flight_no': item[0],
        'scheduled_departure': item[1],
        'actual_departure': item[2],
        'delay': item[3],
    } for item in row], safe=False)


def get_ticket_transfer_info(request, *args, **kwargs):
    """Вывести для билета входящие в него перелеты вместе с запасом времени на пересадку на следу-ющий рейс.
     с ограничением выборки, по тем билетам, которые были забронированы days_ago дней назад"""
    days_ago = request.GET.get('days_ago', 7)

    sql_query = f"""
    SELECT tf.ticket_no, f.departure_airport, f.arrival_airport, f.scheduled_arrival, lead(f.scheduled_departure) OVER w 
    AS next_departure, lead(f.scheduled_departure) OVER w - f.scheduled_arrival AS gap 
    FROM bookings b 
    JOIN tickets t ON t.book_ref = b.book_ref 
    JOIN ticket_flights tf ON tf.ticket_no = t.ticket_no 
    JOIN flights f ON tf.flight_id = f.flight_id WHERE b.book_date =bookings.now()::date - INTERVAL'{days_ago} day'WINDOW w AS 
    (PARTITION BY tf.ticket_no ORDER BY f.scheduled_departure);
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        row = cursor.fetchall()

    return JsonResponse(data=[{
        'ticket_no': item[0],
        'departure_airport': item[1],
        'arrival_airport': item[2],
        'scheduled_arrival': item[3],
        'next_departure': item[4],
        'gap': item[5],
    } for item in row], safe=False)


def get_ticket_flights(request):
    """ Получить билеты """
    limit = request.GET.get('limit', 10)
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM ticket_flights LIMIT {limit}")
        row = cursor.fetchall()
    return JsonResponse(data=[{
        'ticket_no': item[0],
        'flight_id': item[1],
        'fare_conditions': item[2],
        'amount': item[3],
    } for item in row], safe=False)


def get_flights(request):
    """ Получить список трансферов """
    limit = request.GET.get('limit', 10)
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM flights LIMIT {limit}")
        row = cursor.fetchall()
    return JsonResponse(data=[{
        'flight_id': item[0],
        'flight_no': item[1],
        'scheduled_departure': item[2],
        'scheduled_arrival': item[3],
        'arrival_airport': item[4],
        'status': item[5],
        'aircraft_code': item[6],
        'actual_departure': item[7],
        'actual_arrival': item[8],
    } for item in row], safe=False)
