from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..core.db import get_db, Base, engine
from ..models.product import Product
from ..models.price_history import PriceHistory
from ..models.watch import Watch
from .schemas import TrackRequest, ProductOut, PricePoint
from ..scraper.runner import scrape_once
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
