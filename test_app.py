import pytest
from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


@pytest.fixture
def card_number():
    return '1111111111111111'


@pytest.fixture
def expiry_data():
    return {'month': '10', 'year': '2023', 'cvv': '555'}


def test_get_card():
    response = client.get("/")
    assert response.status_code == 200
    assert b"Enter card number" in response.content


def test_check_card_with_valid_card_number(card_number):
    response = client.post("/check_card", data={'card_number': card_number})
    assert response.status_code == 200
    assert b"Enter next data" in response.content


def test_check_card_with_invalid_card_number():
    response = client.post("/check_card", data={'card_number': '0000000000000000'})
    assert response.status_code == 400
    assert b"Card not found" in response.content


def test_check_expiry_with_valid_expiry_data(card_number, expiry_data):
    response = client.post("/check_expiry",
                           cookies={'card_number': card_number},
                           data=expiry_data)
    assert response.status_code == 200
    assert b"Your balance" in response.content


@pytest.mark.parametrize('month, year, cvv, expected_res', [
    (11, 2023, 555, 'Invalid month'),
    (10, 2022, 555, 'Invalid year'),
    (10, 2023, 333, 'Invalid CVV'),
    (5, 1995, 555, 'Invalid month, Invalid year'),
    (10, 2005, 574, 'Invalid year, Invalid CVV'),
    (5, 2019, 157, 'Invalid month, Invalid year, Invalid CVV'),
])
def test_check_expiry_with_invalid_expiry_data(card_number, month: int, year: int, cvv: int, expected_res: str):
    response = client.post("/check_expiry",
                           cookies={'card_number': card_number},
                           data={'month': str(month), 'year': str(year), 'cvv': str(cvv)})
    assert response.status_code == 400
    assert bytes(expected_res, 'utf-8') in response.content


def test_transaction_with_valid_withdrawal(card_number):
    response = client.post("/transaction",
                           cookies={'card_number': card_number, 'balance': '25000'},
                           data={'action': 'withdraw', 'amount': '5000'})
    assert response.status_code == 200
    assert b"New balance" in response.content


def test_transaction_with_invalid_withdrawal(card_number):
    response = client.post("/transaction",
                           cookies={'card_number': card_number, 'balance': '25000'},
                           data={'action': 'withdraw', 'amount': '30000'})
    assert response.status_code == 400
    assert b"Not enough money" in response.content


def test_transaction_with_valid_deposit(card_number):
    response = client.post("/transaction",
                           cookies={'card_number': card_number, 'balance': '25000'},
                           data={'action': 'deposit', 'amount': '5000'})
    assert response.status_code == 200
    assert b"New balance" in response.content


def test_transaction_with_invalid_action(card_number):
    response = client.post("/transaction",
                           cookies={'card_number': card_number, 'balance': '25000'},
                           data={'action': 'invalid', 'amount': '5000'})
    assert response.status_code == 400
    assert b"Invalid action" in response.content
