from .base import BaseAdapter, ScrapeResult
from bs4 import BeautifulSoup

class FallbackAdapter(BaseAdapter):
    def parse(self, html: str) -> ScrapeResult:
        soup = BeautifulSoup(html, "lxml")
        # tenta OpenGraph
        og_title = soup.select_one("meta[property='og:title']")
        title = og_title.get("content") if og_title else None
        # tenta JSON-LD price
        price = None
        for script in soup.select("script[type='application/ld+json']"):
            try:
                import json
                data = json.loads(script.text)
                if isinstance(data, dict):
                    offers = data.get("offers")
                    if isinstance(offers, dict):
                        price = self.parse_price_brl(offers.get("price") or offers.get("lowPrice"))
                        break
                elif isinstance(data, list):
                    for item in data:
                        offers = item.get("offers") if isinstance(item, dict) else None
                        if isinstance(offers, dict):
                            price = self.parse_price_brl(offers.get("price") or offers.get("lowPrice"))
                            if price:
                                break
            except Exception:
                continue
        return ScrapeResult(title=title, price=price, in_stock=None)
