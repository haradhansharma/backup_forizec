# app/views/public.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):    
    return request.app.state.templates.TemplateResponse(request, "index.html", {})