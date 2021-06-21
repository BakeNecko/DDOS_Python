from aiohttp import web
from aiohttp.web_request import Request

routes = web.RouteTableDef()


@routes.get('/get_flights/')
async def get_flights(request: Request):
    limit = request.query.get('limit', 10)

    async with request.app['db'].acquire() as conn:
        query = f"""
            SELECT * FROM flights LIMIT {limit}
        """
        row = await conn.fetch(query)

    return web.json_response(data=[{
        'flight_id': item['flight_id'],
        'flight_no': item['flight_no'],
        'scheduled_departure': str(item['scheduled_departure']),
        'arrival_airport': str(item['arrival_airport']),
        'status': item['status'],
        'aircraft_code': item['aircraft_code'],
        'actual_departure': item['actual_departure'],
        'actual_arrival': item['actual_arrival'],
    } for item in row])


@routes.get('/get_aircrafts/')
async def get_aircrafts(request: Request):
    limit = request.query.get('limit', 10)

    async with request.app['db'].acquire() as conn:
        query = f'SELECT aircraft_code, model, range from aircrafts_data LIMIT {limit}'
        row = await conn.fetch(query)

    return web.json_response(data=[{
        'aircraft_code': item['aircraft_code'],
        'model': item['model'],
        'range': item['range'],
    } for item in row])


@routes.get('/get_flight_delays/')
async def get_flight_delays(request: Request):
    limit = request.query.get('limit', 10)

    sql_query = f"""
        SELECT f.flight_no,f.scheduled_departure,f.actual_departure,f.actual_departure - f.scheduled_departure AS delay FROM flights f 
        WHERE  f.actual_departure IS NOT NULL 
        ORDER BY f.actual_departure - f.scheduled_departure DESC
        LIMIT {limit};
        """

    async with request.app['db'].acquire() as conn:
        row = await conn.fetch(sql_query)

    return web.json_response(data=[{
        'flight_no': item['flight_no'],
        'scheduled_departure': str(item['scheduled_departure']),
        'actual_departure': str(item['actual_departure']),
        'delay': str(item['delay']),
    } for item in row])


@routes.get('/get_ticket_transfer_info/')
async def get_ticket_transfer_info(request: Request):
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

    async with request.app['db'].acquire() as conn:
        row = await conn.fetch(sql_query)

    return web.json_response(data=[{
        'ticket_no': item['ticket_no'],
        'departure_airport': str(item['departure_airport']),
        'arrival_airport': str(item['arrival_airport']),
        'scheduled_arrival': str(item['scheduled_arrival']),
        'next_departure': str(item['next_departure']),
        'gap': str(item['gap']),
    } for item in row])


@routes.get('/get_ticket_flights/')
async def get_ticket_flights(request: Request):
    limit = request.query.get('limit', 10)

    async with request.app['db'].acquire() as conn:
        row = await conn.fetch(f"SELECT * FROM ticket_flights LIMIT {limit}")

    return web.json_response(data=[{
        'ticket_no': item['ticket_no'],
        'flight_id': item['flight_id'],
        'fare_conditions': str(item['fare_conditions']),
        'amount': str(item['amount']),
    } for item in row])
