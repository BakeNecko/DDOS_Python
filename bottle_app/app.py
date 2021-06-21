import json

from bottle import Bottle, HTTPError, Response, get, request, run
from bottle_pgsql import PgSQLPlugin

POOL_SIZE = 10

app = Bottle()
plugin = PgSQLPlugin('host=localhost port=5432 dbname=demo user=postgres password=postgres')
app.install(plugin)


@app.get('/get_flights/')
def get_flights(db):
    limit = request.query.get('limit', 10)
    db.execute(f'SELECT * FROM flights LIMIT {limit}')
    row = db.fetchall()
    if row:
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
    return HTTPError(404, "Page not found")


@app.get('/get_aircrafts/')
def get_aircrafts(db):
    limit = request.query.get('limit', 10)

    db.execute(f'SELECT aircraft_code, model, range from aircrafts_data LIMIT {limit}')
    row = db.fetchall()
    if row:
        return Response(json.dumps([{
            'aircraft_code': item['aircraft_code'],
            'model': item['model'],
            'range': item['range'],
        } for item in row]))
    return HTTPError(404, "Page not found")


@app.get('/get_flight_delays/')
def get_flight_delays(db):
    limit = request.query.get('limit', 10)

    sql_query = f"""
        SELECT f.flight_no,f.scheduled_departure,f.actual_departure,f.actual_departure - f.scheduled_departure AS delay FROM flights f 
        WHERE  f.actual_departure IS NOT NULL 
        ORDER BY f.actual_departure - f.scheduled_departure DESC
        LIMIT {limit};
        """

    db.execute(sql_query)
    row = db.fetchall()
    if row:
        return Response(json.dumps([{
            'flight_no': item['flight_no'],
            'scheduled_departure': str(item['scheduled_departure']),
            'actual_departure': str(item['actual_departure']),
            'delay': str(item['delay']),
        } for item in row]))
    return HTTPError(404, "Page not found")


@app.get('/get_ticket_transfer_info/')
def get_ticket_transfer_info(db):
    days_ago = request.query.get('days_ago', 7)

    sql_query = f"""
            SELECT tf.ticket_no, f.departure_airport, f.arrival_airport, f.scheduled_arrival, lead(f.scheduled_departure) OVER w 
            AS next_departure, lead(f.scheduled_departure) OVER w - f.scheduled_arrival AS gap 
            FROM bookings b 
            JOIN tickets t ON t.book_ref = b.book_ref 
            JOIN ticket_flights tf ON tf.ticket_no = t.ticket_no 
            JOIN flights f ON tf.flight_id = f.flight_id WHERE b.book_date =bookings.now()::date - INTERVAL'{days_ago} day'WINDOW w AS 
            (PARTITION BY tf.ticket_no ORDER BY f.scheduled_departure);
        """

    db.execute(sql_query)
    row = db.fetchall()
    if row:
        return Response(json.dumps([{
            'ticket_no': item['ticket_no'],
            'departure_airport': str(item['departure_airport']),
            'arrival_airport': str(item['arrival_airport']),
            'scheduled_arrival': str(item['scheduled_arrival']),
            'next_departure': str(item['next_departure']),
            'gap': str(item['gap']),
        } for item in row]))

    return HTTPError(404, "Page not found")


@app.get('/get_ticket_flights/')
def get_ticket_flights(db):
    limit = request.query.get('limit', 10)

    db.execute(f"SELECT * FROM ticket_flights LIMIT {limit}")
    row = db.fetchall()
    if row:
        return Response(json.dumps([{
            'ticket_no': item['ticket_no'],
            'flight_id': item['flight_id'],
            'fare_conditions': str(item['fare_conditions']),
            'amount': str(item['amount']),
        } for item in row]))

    return HTTPError(404, "Page not found")


run(app=app, host='localhost', port=8000, server='gunicorn', workers=5)
