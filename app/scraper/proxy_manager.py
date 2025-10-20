import random
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import httpx
from ..core.settings import settings
from ..core.logger import logger

class ProxyManager:
    """Gerencia proxies rotativos para evitar bloqueios"""
    
    def __init__(self):
        self._proxies: List[Dict[str, str]] = []
        self._current_proxy_index = 0
        self._last_rotation = 0
        self._failed_proxies = set()
        self._proxy_stats = {}  # Estatísticas de uso dos proxies
        self._load_proxies()
    
    def _load_proxies(self):
        """Carrega lista de proxies das configurações"""
        if not settings.PROXY_ENABLED or not settings.PROXY_LIST:
            logger.info("Proxies desabilitados ou lista vazia")
            return
        
        proxy_list = [p.strip() for p in settings.PROXY_LIST.split(",") if p.strip()]
        
        for proxy_url in proxy_list:
            try:
                parsed = urlparse(proxy_url if "://" in proxy_url else f"http://{proxy_url}")
                
                proxy_config = {
                    "http://": f"{parsed.scheme}://{proxy_url}",
                    "https://": f"{parsed.scheme}://{proxy_url}",
                }
                
                # Adiciona autenticação se configurada
                if settings.PROXY_USERNAME and settings.PROXY_PASSWORD:
                    auth_proxy = f"{parsed.scheme}://{settings.PROXY_USERNAME}:{settings.PROXY_PASSWORD}@{parsed.netloc}"
                    proxy_config = {
                        "http://": auth_proxy,
                        "https://": auth_proxy,
                    }
                
                self._proxies.append(proxy_config)
                self._proxy_stats[len(self._proxies) - 1] = {
                    "requests": 0,
                    "failures": 0,
                    "last_used": 0,
                    "avg_response_time": 0
                }
                
            except Exception as e:
                logger.warning(f"Erro ao processar proxy {proxy_url}: {e}")
        
        logger.info(f"Carregados {len(self._proxies)} proxies")
    
    def get_proxy(self, force_rotation: bool = False) -> Optional[Dict[str, str]]:
        """
        Retorna proxy atual ou rotaciona se necessário
        
        Args:
            force_rotation: Força rotação para próximo proxy
        """
        if not self._proxies:
            return None
        
        current_time = time.time()
        
        # Rotaciona proxy se necessário
        if (force_rotation or 
            current_time - self._last_rotation > settings.PROXY_ROTATION_INTERVAL):
            self._rotate_proxy()
            self._last_rotation = current_time
        
        # Remove proxies que falharam muito
        self._cleanup_failed_proxies()
        
        if not self._proxies:
            logger.warning("Todos os proxies falharam")
            return None
        
        return self._proxies[self._current_proxy_index]
    
    def _rotate_proxy(self):
        """Rotaciona para o próximo proxy disponível"""
        if len(self._proxies) <= 1:
            return
        
        # Encontra próximo proxy que não falhou recentemente
        attempts = 0
        while attempts < len(self._proxies):
            self._current_proxy_index = (self._current_proxy_index + 1) % len(self._proxies)
            
            if self._current_proxy_index not in self._failed_proxies:
                break
                
            attempts += 1
        
        logger.info(f"Rotacionado para proxy {self._current_proxy_index + 1}/{len(self._proxies)}")
    
    def mark_proxy_failed(self, proxy_config: Dict[str, str]):
        """Marca proxy como falho temporariamente"""
        for i, proxy in enumerate(self._proxies):
            if proxy == proxy_config:
                self._failed_proxies.add(i)
                self._proxy_stats[i]["failures"] += 1
                logger.warning(f"Proxy {i + 1} marcado como falho")
                break
    
    def mark_proxy_success(self, proxy_config: Dict[str, str], response_time: float):
        """Marca proxy como bem-sucedido e atualiza estatísticas"""
        for i, proxy in enumerate(self._proxies):
            if proxy == proxy_config:
                # Remove da lista de falhos
                self._failed_proxies.discard(i)
                
                # Atualiza estatísticas
                stats = self._proxy_stats[i]
                stats["requests"] += 1
                stats["last_used"] = time.time()
                
                # Calcula tempo médio de resposta
                if stats["avg_response_time"] == 0:
                    stats["avg_response_time"] = response_time
                else:
                    stats["avg_response_time"] = (stats["avg_response_time"] + response_time) / 2
                
                break
    
    def _cleanup_failed_proxies(self):
        """Remove proxies da lista de falhos após um tempo"""
        current_time = time.time()
        cleanup_interval = 1800  # 30 minutos
        
        to_remove = []
        for proxy_index in self._failed_proxies:
            if proxy_index < len(self._proxy_stats):
                last_failure_time = self._proxy_stats[proxy_index].get("last_failure", 0)
                if current_time - last_failure_time > cleanup_interval:
                    to_remove.append(proxy_index)
        
        for proxy_index in to_remove:
            self._failed_proxies.discard(proxy_index)
            logger.info(f"Proxy {proxy_index + 1} reabilitado após cooldown")
    
    def get_best_proxy(self) -> Optional[Dict[str, str]]:
        """Retorna o proxy com melhor performance"""
        if not self._proxies:
            return None
        
        best_proxy_index = 0
        best_score = float('inf')
        
        for i, proxy in enumerate(self._proxies):
            if i in self._failed_proxies:
                continue
            
            stats = self._proxy_stats[i]
            
            # Calcula score baseado em falhas e tempo de resposta
            failure_rate = stats["failures"] / max(stats["requests"], 1)
            response_time = stats["avg_response_time"]
            
            score = failure_rate * 100 + response_time
            
            if score < best_score:
                best_score = score
                best_proxy_index = i
        
        self._current_proxy_index = best_proxy_index
        return self._proxies[best_proxy_index]
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas dos proxies"""
        return {
            "total_proxies": len(self._proxies),
            "active_proxies": len(self._proxies) - len(self._failed_proxies),
            "failed_proxies": len(self._failed_proxies),
            "current_proxy": self._current_proxy_index + 1 if self._proxies else 0,
            "proxy_stats": self._proxy_stats
        }
    
    def test_proxy(self, proxy_config: Dict[str, str], test_url: str = "https://httpbin.org/ip") -> bool:
        """
        Testa se um proxy está funcionando
        
        Args:
            proxy_config: Configuração do proxy
            test_url: URL para teste
        """
        try:
            start_time = time.time()
            
            with httpx.Client(proxies=proxy_config, timeout=10.0) as client:
                response = client.get(test_url)
                response.raise_for_status()
                
                response_time = time.time() - start_time
                self.mark_proxy_success(proxy_config, response_time)
                
                logger.info(f"Proxy testado com sucesso - Tempo: {response_time:.2f}s")
                return True
                
        except Exception as e:
            logger.warning(f"Falha no teste do proxy: {e}")
            self.mark_proxy_failed(proxy_config)
            return False
    
    def is_enabled(self) -> bool:
        """Verifica se o sistema de proxies está habilitado"""
        return settings.PROXY_ENABLED and len(self._proxies) > 0

# Instância global
proxy_manager = ProxyManager()
