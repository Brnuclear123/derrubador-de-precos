from .base import BaseAdapter, ScrapeResult
from bs4 import BeautifulSoup

class MagaluAdapter(BaseAdapter):
    def parse(self, html: str) -> ScrapeResult:
        soup = BeautifulSoup(html, "lxml")
        # seletores simples (ajustar com HTML real)
        title = None
        t = soup.select_one("h1") or soup.select_one('[itemprop="name"]')
        if t:
            title = t.get_text(strip=True)

        price = None
        p = soup.select_one("[data-testid='price-value']") or soup.select_one(".price__buy-box .price-template__text")
        if p:
            price = self.parse_price_brl(p.get_text(" ", strip=True))

        in_stock = True
        oos = soup.find(text=lambda x: x and "indisponível" in x.lower())
        if oos:
            in_stock = False

        return ScrapeResult(title=title, price=price, in_stock=in_stock)
