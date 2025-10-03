from .base import BaseAdapter, ScrapeResult
from bs4 import BeautifulSoup

class AmericanasAdapter(BaseAdapter):
    def parse(self, html: str) -> ScrapeResult:
        soup = BeautifulSoup(html, "lxml")
        title = None
        t = soup.select_one("h1") or soup.select_one('[property="og:title"]')
        if t:
            title = t.get_text(strip=True) if hasattr(t, 'get_text') else t.get('content')

        price = None
        p = soup.select_one("[data-testid='price-value']") or soup.select_one("meta[itemprop='price']")
        if p:
            text = p.get("content") if p.has_attr("content") else p.get_text(" ", strip=True)
            price = self.parse_price_brl(text)

        in_stock = True
        oos = soup.find(text=lambda x: x and ("indisponível" in x.lower() or "esgotado" in x.lower()))
        if oos:
            in_stock = False

        return ScrapeResult(title=title, price=price, in_stock=in_stock)
