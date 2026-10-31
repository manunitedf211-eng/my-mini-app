import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def get_user_app():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>index.html አልተገኘም! እባክህ GitHub ላይ index.html መኖሩን አረጋግጥ።</h3>"

@app.get("/admin", response_class=HTMLResponse)
def get_admin_panel():
    if os.path.exists("admin.html"):
        with open("admin.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>admin.html አልተገኘም! እባክህ GitHub ላይ admin.html መኖሩን አረጋግጥ።</h3>"
