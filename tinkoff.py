import hashlib

import requests

import settings

INIT_URL = "https://securepay.tinkoff.ru/v2/Init"
GET_STATE_URL = "https://securepay.tinkoff.ru/v2/GetState"


def is_success(status_code: int) -> bool:
    return 200 <= status_code <= 299


def get_token(data: dict) -> str:
    data = dict(**data, Password=settings.TINKOFF_PASSWORD)
    data = dict(sorted(data.items()))
    raw_string = "".join(data.values())
    return hashlib.sha256(raw_string.encode("utf-8")).hexdigest()


def init(amount: int, payment_id: int) -> tuple:
    data = {"TerminalKey": settings.TINKOFF_TERMINAL_KEY, "Amount": str(amount), "OrderId": str(payment_id)}
    response = requests.post(INIT_URL, json=data)

    if is_success(response.status_code):
        data = response.json()
    else:
        raise Exception(f"Tinkoff error: {response.text}")

    if not data["Success"]:
        raise Exception(f"{data['Message']} {data['Details']}")

    return data["PaymentId"], data["PaymentURL"]


def payment_success(tinkoff_payment_id: int) -> bool:
    data = {
        "TerminalKey": settings.TINKOFF_TERMINAL_KEY,
        "PaymentId": str(tinkoff_payment_id),
    }
    data["Token"] = get_token(data)
    response = requests.post(GET_STATE_URL, json=data)

    if is_success(response.status_code):
        data = response.json()
    else:
        raise Exception(f"Tinkoff error: {response.text}")

    if not data["Success"]:
        raise Exception(f"{data.get('Message', '')} {data.get('Details', '')}")

    return data["Status"] == "CONFIRMED"
