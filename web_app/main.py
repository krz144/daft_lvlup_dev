from fastapi import FastAPI, status, Response, Request, Depends, Query, Header, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Dict
import sqlite3
from typing import NoReturn, Optional

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


# SERIA ZADAŃ 4 (sqlite, sqlalchemy, postgres, ORM, docker)
# ---------------------------------------------------------------------------

def my_text_factory(text: str):
    text = text.decode(encoding='latin1')
    text = text.replace("\n", " ")
    if len(text) > 0:
        while text[-1] == " ":
            text = text[:-1]
    return text


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("./northwind.db")
    # app.db_connection.text_factory = lambda b: b.decode(
    #     errors="ignore")  # northwind specific
    app.db_connection.text_factory = my_text_factory


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/suppliers")
async def root(response: Response):
    app.db_connection.row_factory = sqlite3.Row
    cursor = app.db_connection.cursor().execute(
        "SELECT SupplierID, CompanyName FROM Suppliers")
    data = cursor.fetchall()
    response.status_code = status.HTTP_200_OK
    return data


@app.get("/suppliers")
async def suppliers(response: Response):
    app.db_connection.row_factory = sqlite3.Row
    cursor = app.db_connection.cursor().execute(
        "SELECT SupplierID, CompanyName FROM Suppliers")
    data = cursor.fetchall()
    response.status_code = status.HTTP_200_OK
    return data
    # pobrałem plik northwind.db z githuba, nie działało kodowanie
    # musiałem ręcznie zmienić literki w SQLiteStudio


@app.get("/suppliers/{id}")
async def suppliersid(id: int, response: Response):
    app.db_connection.row_factory = sqlite3.Row
    cursor = app.db_connection.cursor().execute(
        f"SELECT * FROM Suppliers WHERE SupplierID = {id}")
    data = cursor.fetchone()
    if not data:
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    return data


@app.get('/suppliers/{id}/products')
async def suppliersidproducts(id: int,  response: Response):
    app.db_connection.row_factory = sqlite3.Row
    cursor = app.db_connection.cursor().execute(f'''
    SELECT p.ProductID, p.ProductName, c.CategoryID, c.CategoryName, p.Discontinued
    FROM Products as p JOIN Suppliers as s ON p.SupplierID = s.SupplierID
    JOIN Categories as c ON p.CategoryID = c.CategoryID
    WHERE s.SupplierID = {id}
    ORDER BY p.ProductID DESC
    ''')
    data = cursor.fetchall()
    if not data:
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    results = [dict(row) for row in data]
    retv = []
    for d in results:
        r2 = d.copy()
        r2.update(
            {"Category": {'CategoryID': d['CategoryID'], 'CategoryName': d['CategoryName']}})
        r2.pop('CategoryName')
        r2.pop('CategoryID')
        last = int(d['Discontinued'])
        r2.pop('Discontinued')
        r2.update({'Discontinued': last})
        retv.append(r2)
    return retv


class Supplier(BaseModel):
    CompanyName: str
    ContactName: Optional[str] = ""
    ContactTitle: Optional[str] = ""
    Address: Optional[str] = ""
    City: Optional[str] = ""
    PostalCode: Optional[str] = ""
    Country: Optional[str] = ""
    Phone: Optional[str] = ""


class SupplierPut(BaseModel):
    CompanyName: Optional[str] = ""
    ContactName: Optional[str] = ""
    ContactTitle: Optional[str] = ""
    Address: Optional[str] = ""
    City: Optional[str] = ""
    PostalCode: Optional[str] = ""
    Country: Optional[str] = ""
    Phone: Optional[str] = ""

@app.post("/suppliers", status_code=201)
async def post_suppliers(supplier: Supplier):
    for atribute in supplier.__fields__:
        if atribute == "":
            atribute = None
    app.db_connection.execute('''
                                INSERT INTO Suppliers (CompanyName, ContactName, ContactTitle, Address, City, PostalCode, Country, Phone)
                                VALUES (:CompanyName, :ContactName, :ContactTitle, :Address, :City, :PostalCode, :Country, :Phone)
                                ''', {"CompanyName": supplier.CompanyName, "ContactName": supplier.ContactName, "ContactTitle": supplier.ContactTitle,
                                      "Address": supplier.Address, "City": supplier.City, "PostalCode": supplier.PostalCode, "Country": supplier.Country, "Phone": supplier.Phone})
                        
    cursor = app.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    suppliers = cursor.execute('''SELECT *
                                  FROM Suppliers
                                  ORDER BY SupplierID DESC
                                  LIMIT 1''').fetchone()

    suppliers = dict(suppliers)
    for key in suppliers:
        if suppliers[key] == "":
            suppliers[key] = None

    return suppliers


@app.put("/suppliers/{id}")
async def put_suppliers(id: int, supplier: SupplierPut):
    supplier = dict(supplier)

    cursor = app.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    row = cursor.execute('''SELECT * FROM Suppliers WHERE SupplierID = :id''', {"id": id}).fetchone()

    if row is None or len(row) == 0:
        raise HTTPException(status_code=404)

    for key in supplier:
        if supplier[key] == "":
            supplier[key] = row[key]
        
    
    supplier["id"] = id
    app.db_connection.execute('''UPDATE Suppliers
                                 SET CompanyName = :CompanyName, ContactName = :ContactName, ContactTitle = :ContactTitle, Address = :Address, City = :City, PostalCode = :PostalCode, Country = :Country, Phone = :Phone
                                 WHERE SupplierID = :id''', supplier)

    row = cursor.execute('''SELECT * FROM Suppliers WHERE SupplierID = :id''', {"id": id}).fetchone()

    return row


@app.delete("/suppliers/{id}", status_code=204)
async def delete(id: int):
    cursor = app.db_connection.cursor()
    cursor.row_factory = sqlite3.Row
    row = cursor.execute('''SELECT * FROM Suppliers WHERE SupplierID = :id''', {"id": id}).fetchone()

    if row is None or len(row) == 0:
        raise HTTPException(status_code=404)

    cursor.execute("DELETE FROM Suppliers WHERE SupplierID = :id", {"id": id})