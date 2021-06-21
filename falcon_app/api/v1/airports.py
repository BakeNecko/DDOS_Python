# -*- coding: utf-8 -*-
from falcon import Request

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text
from falcon_app import log
from falcon_app.api.common import BaseResource
from falcon_app.errors import (
    NotFoundError,
)

LOG = log.get_logger()


class GetFlights(BaseResource):
    def on_get(self, req: Request, res, *args, **kwargs):
        session = req.context["session"]
        limit = req.params.get('limit', 10)
        try:
            result = session.execute(text(f'SELECT * FROM flights LIMIT {limit}'))
            data = []
            for row in result:
                data.append([str(item) for item in row])
            self.on_success(res, data)
        except NoResultFound:
            raise NotFoundError("Not Found")


class GetAircrafts(BaseResource):
    def on_get(self, req: Request, res, *args, **kwargs):
        session = req.context["session"]
        limit = req.params.get('limit', 10)
        try:
            result = session.execute(text(f'SELECT aircraft_code, model, range from aircrafts_data LIMIT {limit}'))
            data = []
            for row in result:
                data.append([str(item) for item in row])
            self.on_success(res, data)
        except NoResultFound:
            raise NotFoundError("Not Found")


class GetFlightDelays(BaseResource):
    def on_get(self, req: Request, res, *args, **kwargs):
        session = req.context["session"]
        limit = req.params.get('limit', 10)
        sql_query = f"""
                SELECT f.flight_no,f.scheduled_departure,f.actual_departure,f.actual_departure - f.scheduled_departure AS delay FROM flights f 
                WHERE  f.actual_departure IS NOT NULL 
                ORDER BY f.actual_departure - f.scheduled_departure DESC
                LIMIT {limit};
                """
        try:
            result = session.execute(text(sql_query))
            data = []
            for row in result:
                data.append([str(x) for x in row])
            self.on_success(res, data)
        except NoResultFound:
            raise NotFoundError("Not Found")


class GetTicketTransferInfo(BaseResource):
    def on_get(self, req: Request, res, *args, **kwargs):
        session = req.context["session"]
        days_ago = req.params.get('days_ago', 7)
        sql_query = f"""
                SELECT tf.ticket_no, f.departure_airport, f.arrival_airport, f.scheduled_arrival, lead(f.scheduled_departure) OVER w 
                AS next_departure, lead(f.scheduled_departure) OVER w - f.scheduled_arrival AS gap 
                FROM bookings b 
                JOIN tickets t ON t.book_ref = b.book_ref 
                JOIN ticket_flights tf ON tf.ticket_no = t.ticket_no 
                JOIN flights f ON tf.flight_id = f.flight_id WHERE b.book_date =bookings.now()::date - INTERVAL'{days_ago} day'WINDOW w AS 
                (PARTITION BY tf.ticket_no ORDER BY f.scheduled_departure);
            """
        try:
            result = session.execute(text(sql_query))
            data = []
            for row in result:
                data.append([str(x) for x in row])
            self.on_success(res, data)
        except NoResultFound:
            raise NotFoundError("Not Found")


class GetTicketFlights(BaseResource):
    def on_get(self, req: Request, res, *args, **kwargs):
        session = req.context["session"]
        limit = req.params.get('limit', 10)

        try:
            result = session.execute(text(f"SELECT * FROM ticket_flights LIMIT {limit}"))
            data = []
            for row in result:
                data.append([str(x) for x in row])
            self.on_success(res, data)
        except NoResultFound:
            raise NotFoundError("Not Found")
