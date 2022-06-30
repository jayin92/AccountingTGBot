import pytz
from datetime import datetime

tz_TPE = pytz.timezone('Asia/Taipei')

class Record:
    def __init__(self, amount, name="", type="", account="default", isExp=True, comment="", time=None) -> None:
        self.name = name
        self.amount = amount
        self.type = type
        self.account = account
        self.isExp = isExp
        self.comment = comment
        if time == None:
            self.time = datetime.now(tz_TPE).strftime("%Y/%m/%d %H:%M:%S")
        else:
            self.time = time
    
    def __str__(self) -> str:
        res = ""
        if self.name and self.name[0] != "/":
            res += f"名稱：{self.name}\n"
        res += f"金額：{self.amount}\n"
        if self.type and self.type[0] != "/":
            res += f"類別：{self.type}\n"
        if self.account != "default" and self.account[0] != "/":
            res += f"帳戶：{self.account}\n"
        if self.comment and self.comment[0] != "/":
            res += f"備註：{self.comment}\n"
        res += f"時間：{self.time}\n"

        return res
        