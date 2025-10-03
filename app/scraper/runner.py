import httpx
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from .adapters.magalu import MagaluAdapter
from .adapters.americanas import AmericanasAdapter
from .adapters.fallback import FallbackAdapter
from ..models.product import Product
from ..models.price_history import PriceHistory
from ..models.watch import Watch
from ..core.logger import logger

ADAPTERS = {
    "magazineluiza.com.br": MagaluAdapter(),
    "magalu.com": MagaluAdapter(),
    "americanas.com.br": AmericanasAdapter(),
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

async_mode = False  # MVP síncrono


def pick_adapter(domain: str):
    return ADAPTERS.get(domain) or FallbackAdapter()


def fetch_html(url: str) -> str:
    with httpx.Client(headers=HEADERS, timeout=15.0, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.text


def apply_triggers(db: Session, product: Product, new_price: float):
    # busca último preço anterior
    last = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product.id)
        .order_by(PriceHistory.captured_at.desc())
        .offset(1)
        .first()
    )
    last_price = last.price if last else None

    watches = db.query(Watch).filter(Watch.product_id == product.id, Watch.active == True).all()
    fired = []
    for w in watches:
        triggered = False
        reasons = []
        if w.target_price is not None and new_price is not None:
            if new_price <= w.target_price:
                triggered = True
                reasons.append(f"<= alvo {w.target_price}")
        if w.drop_percent is not None and last_price is not None and new_price is not None:
            delta = (last_price - new_price) / last_price * 100.0
            if delta >= w.drop_percent:
                triggered = True
                reasons.append(f"queda {delta:.1f}% >= {w.drop_percent}%")
        if triggered:
            fired.append((w, "; ".join(reasons)))
    # TODO cooldown/debounce + enfileirar notificação real
    if fired:
        logger.info({
            "event": "triggers_fired",
            "product_id": product.id,
            "count": len(fired),
            "details": [dict(watch_id=w.id, reason=r) for w, r in fired],
        })


def scrape_once(db: Session, product: Product) -> bool:
    domain = urlparse(product.url).netloc.replace("www.", "")
    adapter = pick_adapter(domain)
    html = fetch_html(product.url)
    result = adapter.parse(html)

    updated = False
    if result.price is not None:
        ph = PriceHistory(product_id=product.id, price=result.price)
        db.add(ph)
        product.current_price = result.price
        updated = True
    if result.title and not product.title:
        product.title = result.title
    if result.in_stock is not None:
        product.in_stock = result.in_stock

    db.commit()

    if result.price is not None:
        apply_triggers(db, product, result.price)

    return updated
