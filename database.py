import os

from deta import Deta # pip install deta
from dotenv import load_dotenv # pip install python-dotenv

# load the environment variables
load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")

# initialize with project key
deta = Deta(DETA_KEY)

# create database instance
db = deta.Base("cashflow_tracker")

# CRUD-type functions 
def create(period, incomes, expenses, comment):
    """
    Returns the report on successful creation, otherwise raises error
    key = "January_2023"
    incomes = {'Salary': 1500, 'Blog': 50, 'Other Income': 10}
    expenses = {'Rent': 600, 'Food': 300, 'Saving': 100, 'Other Expenses': 200}
    comment = "Generic comment"
    """
    return db.put({"key": period, 
                   "incomes": incomes, 
                   "expenses": expenses, 
                   "comment": comment})

def fetch_all():
    """Returns a dict of all records"""
    res = db.fetch()
    return res.items

def get(period):
    """If not found, the function will return None"""
    return db.get(period)