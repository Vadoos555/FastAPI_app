import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

fake_db = [
    {
        'card': '1111111111111111',
        'month': '10',
        'year': '2023',
        'cvv': '555',
        'balance': '25000'
    },
    {
        'card': '2222333344445555',
        'month': '5',
        'year': '2023',
        'cvv': '777',
        'balance': '100000'
    },
]


@app.get('/', response_class=HTMLResponse)
async def get_card(request: Request):
    return templates.TemplateResponse('enter_card.html',
                                      {'request': request, 'title': 'Enter card number'},
                                      status_code=200)


@app.post('/check_card', response_class=HTMLResponse)
async def check_card(request: Request, card_number: str = Form(...)):

    for card in fake_db:
        if card['card'] == card_number:
            response = templates.TemplateResponse('enter_expiry.html',
                                                  {'request': request, 'title': 'Enter next data'},
                                                  status_code=200)
            response.set_cookie(key='card_number', value=card_number)
            return response

    return templates.TemplateResponse('error.html',
                                      {'request': request, 'message': 'Card not found', 'title': 'Error'},
                                      status_code=400)


@app.post('/check_expiry', response_class=HTMLResponse)
async def check_expiry(request: Request, month: str = Form(...), year: str = Form(...), cvv: str = Form(...)):

    card_number = request.cookies.get('card_number')
    card = None
    for c in fake_db:
        if c['card'] == card_number:
            card = c
            break

    if card is None:
        return templates.TemplateResponse('error.html',
                                          {'request': request, 'message': 'Card not found', 'title': 'Error'},
                                          status_code=400)

    errors = []
    if int(card['month']) != int(month):
        errors.append('Invalid month')
    if card['year'] != year:
        errors.append('Invalid year')
    if card['cvv'] != cvv:
        errors.append('Invalid CVV')

    if errors:
        return templates.TemplateResponse('error.html',
                                          {'request': request, 'message': ', '.join(errors), 'title': 'Error'},
                                          status_code=400)

    balance = card['balance']
    response = templates.TemplateResponse('balance.html',
                                          {'request': request, 'balance': balance, 'title': 'Your balance'},
                                          status_code=200)
    response.set_cookie(key='balance', value=balance)
    return response


@app.post('/transaction', response_class=HTMLResponse)
async def transaction(request: Request, action: str = Form(...), amount: int = Form(...)):
    card_number = request.cookies.get('card_number')
    balance = int(request.cookies.get('balance'))

    card = None
    for c in fake_db:
        if c['card'] == card_number:
            card = c
            break

    if card is None:
        return templates.TemplateResponse('error.html',
                                          {'request': request, 'message': 'Card not found', 'title': 'Error'},
                                          status_code=400)

    if action == 'withdraw':
        if amount > balance:
            return templates.TemplateResponse('error.html',
                                              {'request': request, 'message': 'Not enough money', 'title': 'Error'},
                                              status_code=400)
        new_balance = balance - amount
    elif action == 'deposit':
        new_balance = balance + amount
    else:
        return templates.TemplateResponse('error.html',
                                          {'request': request, 'message': 'Invalid action', 'title': 'Error'},
                                          status_code=400)

    for i, c in enumerate(fake_db):
        if c['card'] == card_number:
            fake_db[i]['balance'] = str(new_balance)
            break

    response = templates.TemplateResponse('balance.html',
                                          {'request': request, 'balance': new_balance, 'title': 'New balance'},
                                          status_code=200)
    response.set_cookie(key='balance', value=str(new_balance))
    return response


if __name__ == '__main__':
    uvicorn.run(app)
