from fastapi import FastAPI, status, Response, Request, Depends, Query, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Dict

app = FastAPI()
security = HTTPBasic()


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


@app.post('/check', response_class=HTMLResponse)
def check(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    response.status_code = status.HTTP_401_UNAUTHORIZED
    try:
        now = datetime.now()
        to_check = datetime.strptime(password, '%Y-%m-%d')
        time_diff = now - to_check
        if time_diff.days >= 16*365:
            response.status_code = status.HTTP_200_OK
            age = time_diff.days // 365
            return f'<h1>Welcome {username}! You are {age}</h1>'
    except ValueError:
        return

# 3.3


@app.get('/info')
def info(format: str = Query(None), user_agent: str | None = Header(default=None)):
    if format == 'json':
        return {"user_agent": user_agent}
    elif format == 'html':
        return HTMLResponse(f'<input type="text" id=user-agent name=agent value="{user_agent}">')
    else:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)


# 3.4
app.saved_paths = set()


@app.put('/save/{string}')
def saveput(string: str):
    if string not in app.saved_paths:
        app.saved_paths.add(string)
    return Response(status_code=status.HTTP_200_OK)


@app.get('/save/{string}')
def saveget(string: str, response: Response, user_agent: str | None = Header(default=None)):
    if string not in app.saved_paths:
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        url_to = "https://first-app-python-lvlup-dev.herokuapp.com/" + \
            "info?format=json"  # zamienic url na heroku
        return RedirectResponse(url=url_to, status_code=status.HTTP_301_MOVED_PERMANENTLY, headers={"User-Agent": user_agent})


@app.delete('/save/{string}')
def savedelete(string: str):
    app.saved_paths.remove(string)
    return
