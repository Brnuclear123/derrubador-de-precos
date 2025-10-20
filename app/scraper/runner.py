import httpx
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from .adapters.magalu import MagaluAdapter
from .adapters.americanas import AmericanasAdapter
from .adapters.fallback import FallbackAdapter
from .headers import header_manager
from .proxy_manager import proxy_manager
from ..models.product import Product
from ..models.price_history import PriceHistory
from ..models.watch import Watch
from ..core.logger import logger

ADAPTERS = {
    "magazineluiza.com.br": MagaluAdapter(),
    "magalu.com": MagaluAdapter(),
    "americanas.com.br": AmericanasAdapter(),
}

async_mode = False  # MVP síncrono


def pick_adapter(domain: str):
    return ADAPTERS.get(domain) or FallbackAdapter()


def fetch_html(url: str) -> str:
    """Faz requisição HTTP com cabeçalhos realistas, proxies rotativos e retry logic"""
    import time
    from ..core.settings import settings
    
    domain = urlparse(url).netloc.replace("www.", "")
    headers = header_manager.get_session_headers(domain)
    
    max_retries = settings.PROXY_MAX_RETRIES if proxy_manager.is_enabled() else 3
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            # Configuração do cliente HTTP
            client_config = {
                "headers": headers,
                "timeout": 15.0,
                "follow_redirects": True
            }
            
            # Adiciona proxy se habilitado
            current_proxy = None
            if proxy_manager.is_enabled():
                current_proxy = proxy_manager.get_proxy(force_rotation=(attempt > 0))
                if current_proxy:
                    client_config["proxies"] = current_proxy
                    logger.info(f"Usando proxy para {domain} (tentativa {attempt + 1})")
            
            start_time = time.time()
            
            with httpx.Client(**client_config) as client:
                resp = client.get(url)
                resp.raise_for_status()
                
                # Marca proxy como bem-sucedido se usado
                if current_proxy:
                    response_time = time.time() - start_time
                    proxy_manager.mark_proxy_success(current_proxy, response_time)
                
                logger.info(f"Requisição bem-sucedida para {domain} em {time.time() - start_time:.2f}s")
                return resp.text
                
        except Exception as e:
            last_exception = e
            logger.warning(f"Tentativa {attempt + 1} falhou para {url}: {str(e)}")
            
            # Marca proxy como falho se usado
            if current_proxy:
                proxy_manager.mark_proxy_failed(current_proxy)
            
            # Aguarda antes da próxima tentativa
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Backoff exponencial
                logger.info(f"Aguardando {wait_time}s antes da próxima tentativa...")
                time.sleep(wait_time)
    
    # Se chegou aqui, todas as tentativas falharam
    logger.error(f"Todas as {max_retries} tentativas falharam para {url}")
    raise last_exception or Exception("Falha desconhecida na requisição")


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
    from datetime import datetime
    
    try:
        domain = urlparse(product.url).netloc.replace("www.", "")
        adapter = pick_adapter(domain)
        html = fetch_html(product.url)
        result = adapter.parse(html)

        updated = False
        
        # Sempre atualizar last_checked_at
        product.last_checked_at = datetime.utcnow()
        
        # Atualizar preço se encontrado
        if result.price is not None:
            ph = PriceHistory(product_id=product.id, price=result.price)
            db.add(ph)
            product.current_price = result.price
            updated = True
            logger.info(f"Preço atualizado para produto {product.id}: R$ {result.price}")
        else:
            logger.warning(f"Preço não encontrado para produto {product.id} ({product.url})")
            
        # Atualizar título se encontrado e não existir
        if result.title and not product.title:
            product.title = result.title
            logger.info(f"Título atualizado para produto {product.id}: {result.title}")
            
        # Atualizar status de estoque
        if result.in_stock is not None:
            product.in_stock = result.in_stock

        db.commit()

        # Disparar triggers se preço foi encontrado
        if result.price is not None:
            apply_triggers(db, product, result.price)

        return updated
        
    except Exception as e:
        logger.error(f"Erro ao fazer scraping do produto {product.id}: {str(e)}")
        # Ainda assim atualizar last_checked_at para evitar tentativas infinitas
        product.last_checked_at = datetime.utcnow()
        db.commit()
        return False
