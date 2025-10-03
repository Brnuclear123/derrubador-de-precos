from dataclasses import dataclass
from typing import Optional
from bs4 import BeautifulSoup
import re

@dataclass
class ScrapeResult:
    title: Optional[str]
    price: Optional[float]
    in_stock: Optional[bool]

class BaseAdapter:
    def parse(self, html: str) -> ScrapeResult:
        """Implementar no adapter específico."""
        raise NotImplementedError

    # Utilitário básico para BRL: extrai 1234.56 de strings tipo "R$ 1.234,56"
    def parse_price_brl(self, text: str) -> Optional[float]:
        if not text:
            return None
        # remove espaços, R$, pontos de milhar; troca vírgula por ponto
        cleaned = re.sub(r"[^0-9,\.]", "", text)
        # heurística: se tem vírgula e não tem ponto, vírgula = decimal
        if "," in cleaned and cleaned.count(",") == 1 and cleaned.count(".") <= 1:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None
