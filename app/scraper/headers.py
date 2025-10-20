import random
import time
from typing import Dict, List
from datetime import datetime

class HeaderManager:
    """Gerencia cabeçalhos realistas para requisições HTTP"""
    
    # Lista de User-Agents realistas e atualizados
    USER_AGENTS = [
        # Chrome Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        
        # Chrome macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        
        # Firefox Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
        
        # Firefox macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        
        # Safari macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
        
        # Edge Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    ]
    
    # Idiomas comuns no Brasil
    ACCEPT_LANGUAGES = [
        "pt-BR,pt;q=0.9,en;q=0.8",
        "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "pt-BR,pt;q=0.8,en;q=0.6,es;q=0.4",
        "pt-BR,pt;q=0.9",
        "pt-BR,pt;q=0.9,en;q=0.8,es;q=0.7",
    ]
    
    # Encodings aceitos
    ACCEPT_ENCODINGS = [
        "gzip, deflate, br",
        "gzip, deflate, br, zstd",
        "gzip, deflate",
    ]
    
    # Tipos de conteúdo aceitos
    ACCEPT_TYPES = [
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    ]
    
    def __init__(self):
        self._last_rotation = 0
        self._current_headers = None
        self._rotation_interval = 300  # 5 minutos
    
    def get_headers(self, force_new: bool = False) -> Dict[str, str]:
        """
        Retorna cabeçalhos realistas, rotacionando periodicamente
        
        Args:
            force_new: Força geração de novos cabeçalhos
        """
        current_time = time.time()
        
        # Rotaciona cabeçalhos a cada intervalo ou se forçado
        if (force_new or 
            self._current_headers is None or 
            current_time - self._last_rotation > self._rotation_interval):
            
            self._current_headers = self._generate_headers()
            self._last_rotation = current_time
        
        return self._current_headers.copy()
    
    def _generate_headers(self) -> Dict[str, str]:
        """Gera um conjunto de cabeçalhos realistas"""
        headers = {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": random.choice(self.ACCEPT_TYPES),
            "Accept-Language": random.choice(self.ACCEPT_LANGUAGES),
            "Accept-Encoding": random.choice(self.ACCEPT_ENCODINGS),
            "DNT": "1",  # Do Not Track
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        
        # Adiciona cabeçalhos específicos baseados no User-Agent
        user_agent = headers["User-Agent"]
        
        if "Chrome" in user_agent:
            # Cabeçalhos específicos do Chrome
            headers["sec-ch-ua"] = self._get_chrome_sec_ch_ua(user_agent)
            headers["sec-ch-ua-mobile"] = "?0"
            headers["sec-ch-ua-platform"] = self._get_platform_from_ua(user_agent)
        
        # Adiciona referrer ocasionalmente (simula navegação)
        if random.random() < 0.3:  # 30% das vezes
            headers["Referer"] = random.choice([
                "https://www.google.com/",
                "https://www.google.com.br/",
                "https://www.bing.com/",
                "https://duckduckgo.com/",
            ])
        
        return headers
    
    def _get_chrome_sec_ch_ua(self, user_agent: str) -> str:
        """Gera sec-ch-ua baseado na versão do Chrome no User-Agent"""
        if "Chrome/120" in user_agent:
            return '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
        elif "Chrome/119" in user_agent:
            return '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"'
        elif "Chrome/118" in user_agent:
            return '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"'
        else:
            return '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
    
    def _get_platform_from_ua(self, user_agent: str) -> str:
        """Extrai plataforma do User-Agent para sec-ch-ua-platform"""
        if "Windows" in user_agent:
            return '"Windows"'
        elif "Macintosh" in user_agent:
            return '"macOS"'
        elif "Linux" in user_agent:
            return '"Linux"'
        else:
            return '"Windows"'
    
    def get_session_headers(self, domain: str = None) -> Dict[str, str]:
        """
        Retorna cabeçalhos otimizados para uma sessão específica
        
        Args:
            domain: Domínio alvo para otimizações específicas
        """
        headers = self.get_headers()
        
        # Otimizações específicas por domínio
        if domain:
            if "magalu" in domain or "magazineluiza" in domain:
                # Headers específicos para Magazine Luiza
                headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
                headers["Sec-Fetch-Site"] = "same-origin"
                
            elif "americanas" in domain:
                # Headers específicos para Americanas
                headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
                headers["Sec-Fetch-Site"] = "cross-site"
        
        return headers

# Instância global para reutilização
header_manager = HeaderManager()
