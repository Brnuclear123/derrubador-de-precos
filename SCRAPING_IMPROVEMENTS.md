# Melhorias no Sistema de Scraping

Este documento descreve as novas funcionalidades implementadas para melhorar a eficácia do scraping e evitar bloqueios.

## 🎭 Cabeçalhos Realistas

### Funcionalidades Implementadas

- **User-Agents Rotativos**: 12+ User-Agents realistas e atualizados (Chrome, Firefox, Safari, Edge)
- **Cabeçalhos Completos**: Accept-Language, Accept-Encoding, Accept, DNT, Connection, etc.
- **Cabeçalhos Específicos por Navegador**: sec-ch-ua para Chrome, cabeçalhos específicos por plataforma
- **Otimizações por Domínio**: Cabeçalhos específicos para Magazine Luiza e Americanas
- **Rotação Automática**: Cabeçalhos rotacionam a cada 5 minutos automaticamente
- **Simulação de Navegação**: Referrer ocasional simulando chegada via Google/Bing

### Como Funciona

O sistema automaticamente:
1. Seleciona User-Agent aleatório da lista atualizada
2. Gera cabeçalhos compatíveis com o navegador escolhido
3. Adiciona cabeçalhos específicos do domínio alvo
4. Rotaciona periodicamente para evitar detecção

## 🔄 Proxies Rotativos

### Funcionalidades Implementadas

- **Suporte a Múltiplos Proxies**: Lista configurável de proxies residenciais
- **Rotação Automática**: Troca de proxy a cada 5 minutos ou em caso de falha
- **Sistema de Retry**: Até 3 tentativas com proxies diferentes
- **Monitoramento de Saúde**: Tracking de falhas e tempo de resposta
- **Recuperação Automática**: Proxies falhados são reabilitados após cooldown
- **Autenticação**: Suporte a username/password para proxies premium

### Configuração

Adicione as seguintes variáveis ao seu arquivo `.env`:

```bash
# Habilitar sistema de proxies
PROXY_ENABLED=true

# Lista de proxies (separados por vírgula)
PROXY_LIST=proxy1.example.com:8080,proxy2.example.com:8080,proxy3.example.com:8080

# Credenciais (se necessário)
PROXY_USERNAME=seu-usuario
PROXY_PASSWORD=sua-senha

# Configurações avançadas
PROXY_ROTATION_INTERVAL=300  # 5 minutos
PROXY_MAX_RETRIES=3
```

### Formatos de Proxy Suportados

```bash
# HTTP simples
PROXY_LIST=proxy1.com:8080,proxy2.com:8080

# Com protocolo
PROXY_LIST=http://proxy1.com:8080,https://proxy2.com:8080

# Com autenticação inline
PROXY_LIST=http://user:pass@proxy1.com:8080

# Misto (recomendado usar PROXY_USERNAME/PASSWORD para todos)
PROXY_LIST=proxy1.com:8080,proxy2.com:8080
PROXY_USERNAME=usuario
PROXY_PASSWORD=senha
```

## 📊 Monitoramento

### Endpoints da API

#### Status do Sistema
```bash
GET /system/status
```
Retorna informações sobre proxies e cabeçalhos:
```json
{
  "proxy_system": {
    "enabled": true,
    "stats": {
      "total_proxies": 3,
      "active_proxies": 2,
      "failed_proxies": 1,
      "current_proxy": 2
    }
  },
  "header_system": {
    "enabled": true,
    "user_agents_available": 12,
    "languages_available": 5
  }
}
```

#### Testar Proxies
```bash
POST /system/proxy/test
```
Testa todos os proxies configurados:
```json
{
  "total_tested": 3,
  "working_proxies": 2,
  "results": [
    {
      "proxy_index": 1,
      "proxy_config": {"http://": "proxy1.com:8080"},
      "working": true
    }
  ]
}
```

#### Forçar Rotação
```bash
POST /system/proxy/rotate
```
Força mudança para próximo proxy:
```json
{
  "rotated": true,
  "old_proxy_index": 1,
  "new_proxy_index": 2
}
```

## 🚀 Benefícios

### Redução de Bloqueios
- **User-Agents Realistas**: Simula navegadores reais
- **Rotação de Proxies**: Distribui requisições por diferentes IPs
- **Cabeçalhos Completos**: Requisições indistinguíveis de navegadores reais
- **Retry Inteligente**: Tenta proxies diferentes em caso de falha

### Melhor Performance
- **Proxies Rápidos**: Sistema escolhe automaticamente os proxies mais rápidos
- **Recuperação Automática**: Proxies temporariamente indisponíveis são reabilitados
- **Backoff Exponencial**: Evita spam em caso de falhas

### Monitoramento Avançado
- **Estatísticas Detalhadas**: Tempo de resposta, taxa de falhas por proxy
- **Logs Estruturados**: Informações detalhadas sobre cada requisição
- **API de Status**: Monitoramento em tempo real via endpoints REST

## 🔧 Troubleshooting

### Proxies Não Funcionam
1. Verifique se `PROXY_ENABLED=true`
2. Teste os proxies: `POST /system/proxy/test`
3. Verifique logs para erros de conexão
4. Confirme formato da `PROXY_LIST`

### Muitas Falhas
1. Verifique qualidade dos proxies residenciais
2. Aumente `PROXY_ROTATION_INTERVAL` se necessário
3. Monitore `/system/status` para estatísticas
4. Considere adicionar mais proxies à lista

### Performance Lenta
1. Use `/system/proxy/test` para identificar proxies lentos
2. Remova proxies com alta latência da lista
3. Considere proxies de data centers mais próximos
4. Monitore tempo de resposta médio nas estatísticas

## 📝 Logs

O sistema gera logs detalhados sobre:
- Rotação de User-Agents e proxies
- Tempo de resposta de cada requisição
- Falhas e recuperações de proxies
- Estatísticas de uso

Exemplo de log:
```
INFO: Usando proxy para magalu.com (tentativa 1)
INFO: Requisição bem-sucedida para magalu.com em 2.34s
WARNING: Tentativa 1 falhou para https://example.com: Connection timeout
INFO: Proxy 1 marcado como falho
INFO: Aguardando 2s antes da próxima tentativa...
```

## 🎯 Próximos Passos

Para melhorar ainda mais o sistema, considere:

1. **Proxies Premium**: Investir em proxies residenciais de alta qualidade
2. **Rate Limiting**: Implementar delays inteligentes entre requisições
3. **Captcha Solving**: Integração com serviços de resolução de captcha
4. **Browser Automation**: Selenium/Playwright para sites mais complexos
5. **Machine Learning**: Detecção automática de padrões de bloqueio
