from locust import HttpUser, TaskSet


def get_aircrafts(l):
    l.client.get("/get_aircrafts/")


def get_flight_delays(l):
    l.client.get("/get_flight_delays/?limit=100")


def get_ticket_transfer_info(l):
    l.client.get("/get_ticket_transfer_info/?days_ago=7")


def get_ticket_flights(l):
    l.client.get("/get_ticket_flights/?limit=100")


def get_flights(l):
    l.client.get("/get_flights/?limit=100")


class ApiDDoS(TaskSet):
    tasks = {
        get_aircrafts: 5,
        get_flight_delays: 3,
        get_ticket_transfer_info: 5,
        get_ticket_flights: 5,
        get_flights: 5,
    }


class WebsiteUser(HttpUser):
    tasks = [ApiDDoS]
    min_wait = 1000
    max_wait = 2000
