import json
import firebase_admin
import datetime
import pytz

from datetime import datetime

from firebase_admin import credentials
from firebase_admin import db

from record import Record


tz_TPE = pytz.timezone('Asia/Taipei')

cred = credentials.Certificate("accountingtgbot-firebase-adminsdk.json")
default_app = firebase_admin.initialize_app(
    cred,
    {'databaseURL': 'https://accountingtgbot-default-rtdb.firebaseio.com/'},
)
ref = db.reference("/")

def writeDict(d: dict, path: str="/"):
    ref.child(path).set(d)

def writeRecord(id, record: Record):
    record.amount = int(record.amount)
    balance = ref.child(f"users/{id}/account/{record.account}/balance").get()
    if balance is None:
        balance = 0
    else:
        balance = int(balance)
    balance += -record.amount if record.isExp else record.amount
    ref.child(f"users/{id}/account/{record.account}/balance").set(balance)

    totalBal = ref.child(f"users/{id}/info/totalBalance").get()
    if totalBal is None:
        totalBal = 0
    else:
        totalBal = int(totalBal)
    totalBal += -record.amount if record.isExp else record.amount

    
    ref.child(f"users/{id}/info/totalBalance").set(totalBal)

    totalExp = ref.child(f"users/{id}/info/totalExpense").get()
    if totalExp is None:
        totalExp = 0
    else:
        totalExp = int(totalExp)
    totalExp += record.amount if record.isExp else 0
    
    ref.child(f"users/{id}/info/totalExpense").set(totalExp)
    
    ref.child(f"users/{id}/records").push(record.__dict__)

def getRecord(id) -> list:
    records = ref.child(f"users/{id}/records").get()
    if records is None:
        return []
    else:
        return [Record(**r) for r in records.values()]

def getTodayRecord(id) -> tuple[list, int]:
    records = getRecord(id)
    today = datetime.now(tz_TPE)
    records =  [r for r in records if datetime.strptime(r.time, "%Y/%m/%d %H:%M:%S").date() == today.date()]
    return records, sum([r.amount for r in records])

if __name__ == "__main__":
    with open("test.json", "r") as file:
        data = json.load(file)

    writeDict(data, "booking")

    