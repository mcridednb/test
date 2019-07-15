from contextlib import closing

from flask import Flask, request
from flask_mysqldb import MySQL
from flask_restful import Resource, Api

import settings
import tinkoff

app = Flask(__name__)
api = Api(app)

app.config["MYSQL_HOST"] = settings.MYSQL_HOST
app.config["MYSQL_USER"] = settings.MYSQL_USER
app.config["MYSQL_PASSWORD"] = settings.MYSQL_PASSWORD
app.config["MYSQL_DB"] = settings.MYSQL_DB

mysql = MySQL(app)


class Payment(Resource):
    @staticmethod
    def _exist_user(user_id: int) -> bool:
        with closing(mysql.connection.cursor()) as cursor:
            cursor.execute(f"SELECT count(*) FROM Users WHERE id = {user_id}")
            count = cursor.fetchone()[0]

        return count == 1

    @classmethod
    def _validate(cls) -> tuple:
        amount = request.form.get("amount")
        user_id = request.form.get("user_id")

        try:
            amount = int(amount)
        except Exception:
            raise Exception("Invalid amount")

        if amount <= 0:
            raise Exception("Amount must be greater than 0")

        try:
            user_id = int(user_id)
        except Exception:
            raise Exception("Invalid user_id")

        if not cls._exist_user(user_id):
            raise Exception("User does not exist")

        return user_id, amount

    @staticmethod
    def _create_payment(user_id: int, amount: int) -> int:
        with closing(mysql.connection.cursor()) as cursor:
            cursor.execute(f"INSERT INTO Tinkoff(userId, amount) VALUES ({user_id}, {amount})")
            mysql.connection.commit()
            payment_id = cursor.lastrowid

        return payment_id

    @staticmethod
    def _update_payment(payment_id: int, tinkoff_payment_id: int) -> None:
        with closing(mysql.connection.cursor()) as cursor:
            cursor.execute(f"UPDATE Tinkoff SET paymentId={tinkoff_payment_id} WHERE id = {payment_id}")
            mysql.connection.commit()

    def post(self):
        try:
            user_id, amount = self._validate()
        except Exception as e:
            return {"success": False, "error": "Request data are invalid", "detail": str(e)}, 400

        try:
            payment_id = self._create_payment(user_id, amount)
        except Exception as e:
            return {"success": False, "error": "Could not create payment", "detail": str(e)}, 500

        try:
            tinkoff_payment_id, payment_url = tinkoff.init(amount, payment_id)
        except Exception as e:
            return {"success": False, "error": "Could not create payment", "detail": str(e)}, 500

        try:
            self._update_payment(payment_id, tinkoff_payment_id)
        except Exception as e:
            return {
                "success": False,
                "error": "Could not update payment",
                "detail": str(e),
                "tinkoff_payment_id": tinkoff_payment_id
            }, 500

        return {"success": True, "payment_id": payment_id, "payment_url": payment_url}, 201


class State(Resource):
    @staticmethod
    def _get_tinkoff_data(payment_id: int) -> tuple:
        with closing(mysql.connection.cursor()) as cursor:
            cursor.execute(f"SELECT userId, amount, paymentId FROM Tinkoff WHERE id = {payment_id}")
            user_id, amount, tinkoff_payment_id = cursor.fetchall()[0]

        return user_id, amount, tinkoff_payment_id

    @staticmethod
    def _add_balance(amount: int, user_id: int) -> None:
        with closing(mysql.connection.cursor()) as cursor:
            cursor.execute(f"UPDATE Users SET balance = (balance + {amount}) WHERE id = {user_id}")
            mysql.connection.commit()

    def get(self, payment_id: int):
        try:
            user_id, amount, tinkoff_payment_id = self._get_tinkoff_data(payment_id)
        except Exception as e:
            return {"success": False, "error": "Failed to get payment details from db", "detail": str(e)}, 500

        try:
            success = tinkoff.payment_success(amount, payment_id, tinkoff_payment_id)
        except Exception as e:
            return {"success": False, "error": "Failed to get payment details from tinkoff", "detail": str(e)}, 500

        if not success:
            return {"success": False, "error": "Payment not completed"}, 200

        self._add_balance(amount, user_id)

        return {"success": True}, 200


api.add_resource(Payment, '/payments')
api.add_resource(State, '/state/<int:payment_id>')

if __name__ == '__main__':
    app.run(debug=settings.DEBUG)
