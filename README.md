# AccountingTGBot
Yet another accounting telegram bot.

## 功能
- 快速記帳
    - 直接輸入數字紀錄金額
- 分類
- 查看每日總消費金額
- 支援多平台 (Android/iOS/Windows/MacOS/Web)

## 特性
- Python
- Firebase
- Heroku

## 使用說明

直接輸入金額開始記帳

輸入 `/today` 查看今天記帳紀錄

輸入 `/record` 查看最近 5 筆記帳紀錄

輸入 `/help` 顯示此說明

## 安裝說明

1. `pip install -r requirements.txt` or `pipenv install`
2. 申請 Firebase 專案，將對應的 .json 放在檔案目錄
3. 將 Telegram Bot token 放在 secrets.json
