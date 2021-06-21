import json

from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.response import Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql import text

POOL_SIZE = 10

def db_conn(request: Request):
    DBURL = 'postgresql://postgres:postgres@localhost:5432/demo'
    engine = create_engine(DBURL, poolclass=QueuePool, pool_size=POOL_SIZE)
    Session = sessionmaker(bind=engine)
    session = Session()
    session._model_changes = {}
    def cleanup(request):
        session.close()
    request.add_finished_callback(cleanup)
    return session


def get_flights(request: Request):
    conn = request.db_conn
    limit = request.params.get('limit', 10)

    s = text(f'SELECT * FROM flights LIMIT {limit}')
    cur = conn.execute(s)
    row = cur.fetchall()

    return Response(json.dumps([{
        'flight_id': item['flight_id'],
        'flight_no': item['flight_no'],
        'scheduled_departure': str(item['scheduled_departure']),
        'scheduled_arrival': str(item['scheduled_arrival']),
        'arrival_airport': item['arrival_airport'],
        'status': item['status'],
        'aircraft_code': item['aircraft_code'],
        'actual_departure': str(item['actual_departure']),
        'actual_arrival': str(item['actual_arrival']),
    } for item in row]))


def get_aircrafts(request: Request):
    conn = request.db_conn
    limit = request.params.get('limit', 10)

    s = text(f'SELECT aircraft_code, model, range from aircrafts_data LIMIT {limit}')
    cur = conn.execute(s)
    row = cur.fetchall()

    return Response(json.dumps([{
        'aircraft_code': item['aircraft_code'],
        'model': item['model'],
        'range': item['range'],
    } for item in row]))


def get_flight_delays(request: Request):
    conn = request.db_conn
    limit = request.params.get('limit', 10)

    sql_query = f"""
        SELECT f.flight_no,f.scheduled_departure,f.actual_departure,f.actual_departure - f.scheduled_departure AS delay FROM flights f 
        WHERE  f.actual_departure IS NOT NULL 
        ORDER BY f.actual_departure - f.scheduled_departure DESC
        LIMIT {limit};
        """

    s = text(sql_query)
    cur = conn.execute(s)
    row = cur.fetchall()

    return Response(json.dumps([{
        'flight_no': item['flight_no'],
        'scheduled_departure': str(item['scheduled_departure']),
        'actual_departure': str(item['actual_departure']),
        'delay': str(item['delay']),
    } for item in row]))


def get_ticket_transfer_info(request: Request):
    conn = request.db_conn
    days_ago = request.params.get('days_ago', 7)

    sql_query = f"""
            SELECT tf.ticket_no, f.departure_airport, f.arrival_airport, f.scheduled_arrival, lead(f.scheduled_departure) OVER w 
            AS next_departure, lead(f.scheduled_departure) OVER w - f.scheduled_arrival AS gap 
            FROM bookings b 
            JOIN tickets t ON t.book_ref = b.book_ref 
            JOIN ticket_flights tf ON tf.ticket_no = t.ticket_no 
            JOIN flights f ON tf.flight_id = f.flight_id WHERE b.book_date =bookings.now()::date - INTERVAL'{days_ago} day'WINDOW w AS 
            (PARTITION BY tf.ticket_no ORDER BY f.scheduled_departure);
        """

    s = text(sql_query)
    cur = conn.execute(s)
    row = cur.fetchall()

    return Response(json.dumps([{
        'ticket_no': item['ticket_no'],
        'departure_airport': str(item['departure_airport']),
        'arrival_airport': str(item['arrival_airport']),
        'scheduled_arrival': str(item['scheduled_arrival']),
        'next_departure': str(item['next_departure']),
        'gap': str(item['gap']),
    } for item in row]))


def get_ticket_flights(request: Request):
    conn = request.db_conn
    limit = request.params.get('limit', 10)

    s = text(f"SELECT * FROM ticket_flights LIMIT {limit}")
    cur = conn.execute(s)
    row = cur.fetchall()

    return Response(json.dumps([{
        'ticket_no': item['ticket_no'],
        'flight_id': item['flight_id'],
        'fare_conditions': str(item['fare_conditions']),
        'amount': str(item['amount']),
    } for item in row]))


def main():
    config = Configurator()
    config.add_request_method(db_conn, reify=True)
    config.add_route('get_flights', '/get_flights/')
    config.add_view(get_flights, route_name='get_flights')
    config.add_route('get_aircrafts', '/get_aircrafts/')
    config.add_view(get_aircrafts, route_name='get_aircrafts')
    config.add_route('get_flight_delays', '/get_flight_delays/')
    config.add_view(get_flight_delays, route_name='get_flight_delays')
    config.add_route('get_ticket_transfer_info', '/get_ticket_transfer_info/')
    config.add_view(get_ticket_transfer_info, route_name='get_ticket_transfer_info')
    config.add_route('get_ticket_flights', '/get_ticket_flights/')
    config.add_view(get_ticket_flights, route_name='get_ticket_flights')
    app = config.make_wsgi_app()
    return app


application = main()
