import databases
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from falcon_app.config import DATABASE_URL

database = databases.Database(DATABASE_URL)

engine = create_engine(
    DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

@app.on_event("startup")
async def startup():
    # когда приложение запускается устанавливаем соединение с БД
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    # когда приложение останавливается разрываем соединение с БД
    await database.disconnect()


@app.get("/get_flights/")
async def get_flights(limit: int = 10):
    rows = await database.fetch_all(f'SELECT * FROM flights LIMIT {limit}')
    return [dict(item) for item in rows]


@app.get("/get_aircrafts/")
async def get_aircrafts(limit: int = 10):
    rows = await database.fetch_all(f'SELECT aircraft_code, model, range from aircrafts_data LIMIT {limit}')
    return [dict(item) for item in rows]


@app.get("/get_flight_delays/")
async def get_flight_delays(limit: int = 10):
    sql_query = f"""
        SELECT f.flight_no,f.scheduled_departure,f.actual_departure,f.actual_departure - f.scheduled_departure AS delay FROM flights f 
        WHERE  f.actual_departure IS NOT NULL 
        ORDER BY f.actual_departure - f.scheduled_departure DESC
        LIMIT {limit};
        """
    rows = await database.fetch_all(sql_query)
    return [dict(item) for item in rows]


@app.get("/get_ticket_transfer_info/")
async def get_ticket_transfer_info(days_ago: int = 7):
    sql_query = f"""
        SELECT tf.ticket_no, f.departure_airport, f.arrival_airport, f.scheduled_arrival, lead(f.scheduled_departure) OVER w 
        AS next_departure, lead(f.scheduled_departure) OVER w - f.scheduled_arrival AS gap 
        FROM bookings b 
        JOIN tickets t ON t.book_ref = b.book_ref 
        JOIN ticket_flights tf ON tf.ticket_no = t.ticket_no 
        JOIN flights f ON tf.flight_id = f.flight_id WHERE b.book_date =bookings.now()::date - INTERVAL'{days_ago} day'WINDOW w AS 
        (PARTITION BY tf.ticket_no ORDER BY f.scheduled_departure);
    """
    rows = await database.fetch_all(sql_query)
    return [dict(item) for item in rows]


@app.get("/get_ticket_flights/")
async def get_ticket_flights(limit: int = 10):
    rows = await database.fetch_all(f"SELECT * FROM ticket_flights LIMIT {limit}")
    return [dict(item) for item in rows]
