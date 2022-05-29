from fastapi import FastAPI, status, Response, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Dict

app = FastAPI()


@app.get("/", status_code=status.HTTP_200_OK)  # 1.1
def root():
    return {"start": "1970-01-01"}


# @app.api_route("/test", methods=['GET', 'POST'])
# def testoowanko(request: Request):
#     return f'Client used {request.method} method'


@app.get('/method', status_code=status.HTTP_200_OK)  # 1.2
def methodget():
    return {"method": "GET"}


@app.put('/method', status_code=status.HTTP_200_OK)
def methodput():
    return {"method": "PUT"}


@app.delete('/method', status_code=status.HTTP_200_OK)
def methoddelete():
    return {"method": "DELETE"}


@app.options('/method', status_code=status.HTTP_200_OK)
def methodoptions():
    return {"method": "OPTIONS"}


@app.post('/method', status_code=status.HTTP_201_CREATED)
def methodpost():
    return {"method": "POST"}


days = {1: "monday", 2: "tuesday", 3: "wednesday",
        4: "thursday", 5: "friday", 6: "saturday", 7: "sunday"}


@app.get('/day', status_code=status.HTTP_200_OK)  # 1.3
def check_day(response: Response, name: str | None = None, number: int | None = None):
    if number and name:
        if days[number] == name:
            return
    response.status_code = status.HTTP_400_BAD_REQUEST
    return


class JSONItem(BaseModel):
    date: str
    event: str


# Dict[str, List[JSONItem]]
app.counter = 0
app.events = dict()


@app.put('/events', status_code=status.HTTP_200_OK)  # 1.4
def update_events(item: JSONItem):
    retv = {
        "id": app.counter,
        "name": item.event,
        "date": item.date,
        "date_added": str(date.today())
    }
    try:
        app.events[retv["date"]].append(retv)
    except KeyError:
        app.events[retv["date"]] = [retv]
    app.counter += 1
    return retv


@app.get('/events/{date}', status_code=status.HTTP_200_OK)
def get_events(date: str, response: Response):
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    try:
        return app.events[date]
    except KeyError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return

# Zadania Seria 3

# 3.1


@app.get('/start', response_class=HTMLResponse)
def start(response: Response):
    return """<h1>The unix epoch started at 1970-01-01</h1>"""

# 3.2


@app.post('/check')
def check(username: str, password: str, response: Response, response_class=HTMLResponse):
    response.status_code = status.HTTP_401_UNAUTHORIZED
    try:
        now = datetime.now()
        to_check = datetime.strptime(password, '%Y-%m-%d')
        time_diff = now - to_check
        if time_diff.days < 16*365:
            response.status_code = status.HTTP_200_OK
            return """<h1>Welcome [imie]! You are [wiek]</h1>"""
    except ValueError:
        return


if __name__ == '__main__':
    # now_date_str = str(datetime.now())[0:10]
    # now_date = datetime.date(now_date_str)
    now = datetime.now()
    to_check = datetime.strptime("2001-01-01", '%Y-%m-%d')
    time_diff = now - to_check
    if time_diff.days < 16*365:
        pass  # OK
    print(time_diff.days)
