from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.routes import router as api_router
from .ui import router as ui_router
from .core.db import Base, engine
from .core.logger import logger

app = FastAPI(title="Derrubador de Preços")

# CORS liberado p/ extensão e web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste se quiser restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Rotas
app.include_router(api_router)
app.include_router(ui_router)

@app.on_event("startup")
def on_start():
    Base.metadata.create_all(bind=engine)
    logger.info("API iniciada 🚀")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui")
