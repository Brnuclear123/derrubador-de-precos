#!/usr/bin/env python3
"""
Script para rodar o servidor do Derrubador de Preços
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Iniciando Derrubador de Preços...")
    print("📍 Acesse: http://localhost:8000/")
    print("📊 Documentação: http://localhost:8000/docs")
    print("🖼️ Teste da logo: http://localhost:8000/static/images/logo.png")
    print("\n" + "="*50)
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
