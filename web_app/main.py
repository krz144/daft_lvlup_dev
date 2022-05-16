from fastapi import FastAPI, status

app = FastAPI()


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"start": "1970-01-01"}


@app.api_route("/test", methods=['GET', 'POST'])
def testoowanko(request):
    return f'Client used {request.method} method'


@app.get('/method', status_code=status.HTTP_200_OK)
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
