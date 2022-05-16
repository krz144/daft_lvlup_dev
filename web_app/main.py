from os import stat
from fastapi import FastAPI, status, Response, Request

app = FastAPI()


@app.get("/", status_code=status.HTTP_200_OK)  # 1.1
def root():
    return {"start": "1970-01-01"}


@app.api_route("/test", methods=['GET', 'POST'])
def testoowanko(request: Request):
    return f'Client used {request.method} method'


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
