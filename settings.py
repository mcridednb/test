import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Tinkoff
TINKOFF_TERMINAL_KEY = os.getenv("TINKOFF_TERMINAL_KEY")
TINKOFF_PASSWORD = os.getenv("TINKOFF_PASSWORD")

if not all([TINKOFF_TERMINAL_KEY, TINKOFF_PASSWORD]):
    raise Exception("Incorrect Tinkoff settings")

# MySQL
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

if not all([MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB]):
    raise Exception("Incorrect database settings")

DEBUG = os.getenv("DEBUG") == "True"
