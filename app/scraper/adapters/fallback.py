from .base import BaseAdapter, ScrapeResult
from bs4 import BeautifulSoup
import re

class FallbackAdapter(BaseAdapter):
    def parse(self, html: str) -> ScrapeResult:
        soup = BeautifulSoup(html, "lxml")
        
        # Tentar capturar título
        title = self._extract_title(soup)
        
        # Tentar capturar preço
        price = self._extract_price(soup)
        
        # Verificar se está em estoque
        in_stock = self._check_stock(soup)
        
        return ScrapeResult(title=title, price=price, in_stock=in_stock)
    
    def _extract_title(self, soup):
        """Tenta extrair título de várias formas"""
        # OpenGraph
        og_title = soup.select_one("meta[property='og:title']")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()
        
        # Title tag
        title_tag = soup.select_one("title")
        if title_tag and title_tag.text:
            return title_tag.text.strip()
        
        # H1
        h1 = soup.select_one("h1")
        if h1 and h1.text:
            return h1.text.strip()
        
        return None
    
    def _extract_price(self, soup):
        """Tenta extrair preço de várias formas"""
        # JSON-LD structured data
        price = self._extract_price_from_jsonld(soup)
        if price:
            return price
        
        # Meta tags de preço
        price_meta = soup.select_one("meta[property='product:price:amount']")
        if price_meta and price_meta.get("content"):
            return self.parse_price_brl(price_meta["content"])
        
        # Seletores comuns de preço
        price_selectors = [
            "[data-testid*='price']",
            ".price",
            ".valor",
            ".preco",
            "[class*='price']",
            "[class*='valor']",
            "[class*='preco']",
            "[id*='price']",
            "[id*='valor']",
            "[id*='preco']"
        ]
        
        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                price = self.parse_price_brl(text)
                if price:
                    return price
        
        # Busca por padrões de preço no texto
        price_patterns = [
            r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            r'(\d{1,3}(?:\.\d{3})*(?:,\d{2}))\s*reais?',
            r'por\s*R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
        ]
        
        text = soup.get_text()
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return self.parse_price_brl(matches[0])
        
        return None
    
    def _extract_price_from_jsonld(self, soup):
        """Extrai preço de dados estruturados JSON-LD"""
        for script in soup.select("script[type='application/ld+json']"):
            try:
                import json
                data = json.loads(script.text)
                
                # Normalizar para lista
                if isinstance(data, dict):
                    data = [data]
                elif not isinstance(data, list):
                    continue
                
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    
                    # Buscar offers
                    offers = item.get("offers")
                    if offers:
                        if isinstance(offers, dict):
                            price_value = offers.get("price") or offers.get("lowPrice")
                            if price_value:
                                return self.parse_price_brl(str(price_value))
                        elif isinstance(offers, list):
                            for offer in offers:
                                if isinstance(offer, dict):
                                    price_value = offer.get("price") or offer.get("lowPrice")
                                    if price_value:
                                        return self.parse_price_brl(str(price_value))
                    
                    # Buscar price diretamente
                    price_value = item.get("price")
                    if price_value:
                        return self.parse_price_brl(str(price_value))
                        
            except (json.JSONDecodeError, Exception):
                continue
        
        return None
    
    def _check_stock(self, soup):
        """Verifica se o produto está em estoque"""
        # Textos que indicam falta de estoque
        out_of_stock_texts = [
            "indisponível", "fora de estoque", "sem estoque", "esgotado",
            "produto indisponível", "temporariamente indisponível",
            "out of stock", "unavailable"
        ]
        
        text = soup.get_text().lower()
        for oos_text in out_of_stock_texts:
            if oos_text in text:
                return False
        
        # Se não encontrou indicadores de falta de estoque, assume que está disponível
        return True
