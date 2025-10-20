from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..core.db import get_db, Base, engine
from ..models.product import Product
from ..models.price_history import PriceHistory
from ..models.watch import Watch
from .schemas import TrackRequest, ProductOut, PricePoint
from ..scraper.runner import scrape_once
from ..scraper.proxy_manager import proxy_manager
from ..scraper.headers import header_manager
from ..core.logger import logger
from urllib.parse import urlparse
from datetime import datetime, timedelta

router = APIRouter()

# Garantir que as tabelas existam
Base.metadata.create_all(bind=engine)

@router.post("/track")
def track(req: TrackRequest, db: Session = Depends(get_db)):
    domain = urlparse(str(req.url)).netloc.replace("www.", "")

    product = db.query(Product).filter(Product.url == str(req.url)).first()
    if not product:
        product = Product(url=str(req.url), domain=domain)
        db.add(product)
        db.commit()
        db.refresh(product)

    # cria watch
    if req.target_price is None and req.drop_percent is None:
        raise HTTPException(400, detail="Defina target_price ou drop_percent")

    watch = Watch(
        product_id=product.id,
        channel=req.channel,
        target_price=req.target_price,
        drop_percent=req.drop_percent,
        endpoint=req.endpoint,
        active=True,
    )
    db.add(watch)
    db.commit()

    # opcional: forçar 1ª checagem
    try:
        updated = scrape_once(db, product)
        logger.info(f"Primeira checagem feita para product={product.id} updated={updated}")
    except Exception as e:
        logger.warning(f"Falha na primeira checagem: {e}")

    return {"product_id": product.id, "watch_id": watch.id}

@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, detail="Produto não encontrado")
    return product

@router.get("/products/{product_id}/history")
def get_history(product_id: int, days: int = Query(default=30, ge=1, le=365), db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=days)
    q = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .filter(PriceHistory.captured_at >= since)
        .order_by(PriceHistory.captured_at.desc())
    )
    return [
        PricePoint(price=ph.price, captured_at=ph.captured_at.isoformat())
        for ph in q.all()
    ]

@router.post("/scrape-now")
def scrape_now(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, detail="Produto não encontrado")
    updated = scrape_once(db, product)
    return {"ok": True, "updated": updated}

@router.get("/products", response_model=list[ProductOut])
def list_products(limit: int = Query(default=50, ge=1, le=100), db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.last_checked_at.desc()).limit(limit).all()
    return products

@router.get("/system/status")
def system_status():
    """Retorna status do sistema incluindo proxies e headers"""
    proxy_stats = proxy_manager.get_stats()
    
    return {
        "proxy_system": {
            "enabled": proxy_manager.is_enabled(),
            "stats": proxy_stats
        },
        "header_system": {
            "enabled": True,
            "user_agents_available": len(header_manager.USER_AGENTS),
            "languages_available": len(header_manager.ACCEPT_LANGUAGES)
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/system/proxy/test")
def test_proxies():
    """Testa todos os proxies configurados"""
    if not proxy_manager.is_enabled():
        raise HTTPException(400, detail="Sistema de proxies não está habilitado")
    
    results = []
    for i, proxy in enumerate(proxy_manager._proxies):
        test_result = proxy_manager.test_proxy(proxy)
        results.append({
            "proxy_index": i + 1,
            "proxy_config": {k: v.split("@")[-1] if "@" in v else v for k, v in proxy.items()},  # Remove credenciais do retorno
            "working": test_result
        })
    
    return {
        "total_tested": len(results),
        "working_proxies": sum(1 for r in results if r["working"]),
        "results": results
    }

@router.post("/system/proxy/rotate")
def rotate_proxy():
    """Força rotação do proxy atual"""
    if not proxy_manager.is_enabled():
        raise HTTPException(400, detail="Sistema de proxies não está habilitado")
    
    old_index = proxy_manager._current_proxy_index
    proxy_manager._rotate_proxy()
    new_index = proxy_manager._current_proxy_index
    
    return {
        "rotated": True,
        "old_proxy_index": old_index + 1,
        "new_proxy_index": new_index + 1
    }
