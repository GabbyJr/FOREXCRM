from fastapi import FastAPI, Form, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from supabase import create_client
from dotenv import load_dotenv
import os
import webbrowser
import threading
import time
print("TEMPLATES DIRECTORY:", os.path.abspath("templates"))
print("FILES:", os.listdir("templates"))


load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

current_agent = None

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(email: str = Form(), password: str = Form()):
    global current_agent
    res = supabase.table("agents").select("*").eq("email", email).execute()
    if res.data and password == "12345":  # simple for now
        current_agent = res.data[0]
        return RedirectResponse("/dashboard", status_code=303)
    return HTMLResponse("<h1 style='color:red;text-align:center;margin-top:100px'>Wrong password! Use 12345</h1>", status_code=400)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not current_agent:
        return RedirectResponse("/")
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "agent": current_agent,
            "invite_link": f"https://t.me/yourbot?start={current_agent.get('agent_code', 'GABBY001')}",
            "clients": [],
            "pending": []
        }
    )


# THIS IS THE MAGIC — opens browser automatically
def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)