## Установка:
* Необходимо создать .env файл с переменными окружения
* Необходимо создать виртуальное окружение и установить зависимости:
```
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
```

## Запуск проекта:
    FLASK_APP=api.py flask run

## Использование:
```python
import requests
payment_url = "http://127.0.0.1:5000/payments"
payload = {"amount": 400, "user_id": 1}
response = requests.post(payment_url, data=payload)
response.json()
# >>> {'success': True, 'payment_id': 47, 'payment_url': 'https://securepay.tinkoff.ru/new/*****'}
# Переходим по ссылке payment_url, заполняем данные карты
state_url = f"http://127.0.0.1:5000/state/{response.json()['payment_id']}"
response = requests.get(state_url)
response.json()
# >>> {'success': True}
```
