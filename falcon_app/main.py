# -*- coding: utf-8 -*-

import falcon

from falcon_app import log
from falcon_app.middleware import JSONTranslator, DatabaseSessionManager
from falcon_app.database import db_session, init_session
from falcon_app.api.v1 import GetFlights, GetTicketFlights, GetTicketTransferInfo, GetAircrafts, GetFlightDelays
from falcon_app.api.common import base
from falcon_app.errors import AppError

LOG = log.get_logger()


class App(falcon.API):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        LOG.info("API Server is starting")

        self.add_route("/", base.BaseResource())
        self.add_route("/get_flights/", GetFlights())
        self.add_route("/get_aircrafts/", GetTicketFlights())
        self.add_route("/get_flight_delays/", GetTicketTransferInfo())
        self.add_route("/get_ticket_transfer_info/", GetAircrafts())
        self.add_route("/get_ticket_flights/", GetFlightDelays())
        self.add_error_handler(AppError, AppError.handle)


init_session()
middleware = [JSONTranslator(), DatabaseSessionManager(db_session)]
application = App(middleware=middleware)
