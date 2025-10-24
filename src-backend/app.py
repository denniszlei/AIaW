from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response, UploadFile, Form, File
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import aiohttp
from typing import Optional, Dict, Any
from fastapi.staticfiles import StaticFiles
from llama_parse import LlamaParse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os

http_client = None
ACCESS_CODES = os.environ.get('ACCESS_CODE', '').split(',')
ACCESS_CODES = [code.strip() for code in ACCESS_CODES if code.strip()]
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = os.urandom(24).hex()
    print("--- WARNING ---")
    print("SECRET_KEY environment variable not set. Using a temporary secret key.")
    print("For production, please set a strong, persistent SECRET_KEY.")
    print("---------------")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- Environment Variables ---")
    for key, value in os.environ.items():
        print(f"{key}: {value}")
    print("---------------------------")
    global http_client
    http_client = aiohttp.ClientSession()
    yield
    await http_client.close()

app = FastAPI(lifespan=lifespan)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Pass through if no access codes are configured
        if not ACCESS_CODES:
            return await call_next(request)

        # List of paths that are protected by authentication
        protected_paths = ['/cors', '/doc-parse', '/searxng']
        is_protected = any(request.url.path.startswith(p) for p in protected_paths)

        if is_protected:
            # Session is only accessed here, for protected routes
            if not request.session.get('access_code') or request.session.get('access_code') not in ACCESS_CODES:
                return JSONResponse(status_code=401, content={'detail': 'Not authenticated'})

        response = await call_next(request)
        return response

# IMPORTANT: Middleware is added in reverse order of execution.
# AuthMiddleware will run AFTER SessionMiddleware.
app.add_middleware(AuthMiddleware)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

ALLOWED_PREFIXES = [
    'https://lobehub.search1api.com/api/search',
    'https://pollinations.ai-chat.top/api/drawing',
    'https://web-crawler.chat-plugin.lobehub.com/api/v1'
]

class ProxyRequest(BaseModel):
    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Any] = None

@app.post('/cors/proxy')
async def proxy(request: ProxyRequest):
    if not any(request.url.startswith(prefix) for prefix in ALLOWED_PREFIXES):
        raise HTTPException(status_code=403, detail='URL not allowed')

    kwargs = {
        'method': request.method,
        'url': request.url,
        'headers': request.headers or {}
    }

    if request.body is not None:
        if isinstance(request.body, (dict, list)):
            kwargs['json'] = request.body
        else:
            kwargs['data'] = request.body

    try:
        async with http_client.request(**kwargs) as response:
            content = await response.read()
            return Response(content=content, status_code=response.status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/doc-parse/parse')
async def parse_document(
    file: UploadFile = File(...),
    language: Optional[str] = Form(default='en'),
    target_pages: Optional[str] = Form(default=None)
):
    parser = LlamaParse(
        result_type='markdown',
        language=language,
        target_pages=target_pages
    )

    file_content = await file.read()

    try:
        documents = await parser.aload_data(
            file_content,
            {'file_name': file.filename}
        )

        return {
            'success': True,
            'content': [{'text': doc.text, 'meta': doc.metadata} for doc in documents]
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

    finally:
        await file.close()

@app.get('/searxng')
async def searxng(request: Request):
    searxng_url = os.environ.get('SEARXNG_URL')

    if not searxng_url:
        raise HTTPException(status_code=502, detail="SEARXNG_URL environment variable not set")

    query_string = request.url.query
    target_url = f"{searxng_url}?{query_string}" if query_string else searxng_url

    headers = dict(request.headers)
    # 移除 host header 以避免冲突
    headers.pop('host', None)

    try:
        async with http_client.get(target_url, headers=headers) as response:
            content = await response.read()
            return Response(
                content=content,
                status_code=response.status
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.mount('/', StaticFiles(directory='static', html=True), name='static')

class AccessCode(BaseModel):
    code: str

@app.post("/api/auth/verify")
async def verify_access_code(access_code: AccessCode, request: Request):
    if not ACCESS_CODES:
        return {"status": "success"}
    if access_code.code in ACCESS_CODES:
        request.session["access_code"] = access_code.code
        return {"status": "success"}
    else:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid access code"})

@app.get("/api/auth/status")
async def auth_status(request: Request):
    if not ACCESS_CODES:
        return {"authenticated": True}
    if request.session.get('access_code') in ACCESS_CODES:
        return {"authenticated": True}
    return {"authenticated": False}

@app.post("/api/auth/logout")
async def logout(request: Request):
    request.session.pop("access_code", None)
    return {"status": "success"}

@app.exception_handler(404)
async def return_index(request: Request, exc: HTTPException):
    return FileResponse("static/index.html")
