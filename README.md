# derrubador-de-precos (MVP)

Monitor de preços com FastAPI + SQLite + Scraper por domínio.

## Rodando local

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
# source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # edite as chaves se quiser e-mail/webpush
uvicorn app.main:app --reload
```

Acesse: [http://localhost:8000/docs](http://localhost:8000/docs)

## Endpoints mínimos

* `POST /track` — cria/reaproveita produto e adiciona watch
* `GET /products/{id}` — detalhes
* `GET /products/{id}/history?days=30` — série histórica
* `POST /scrape-now?product_id=` — força uma checagem

### Exemplo `POST /track`

```json
{
  "url": "https://www.magazineluiza.com.br/produto/xyz",
  "target_price": 1999.90,
  "channel": "email",
  "endpoint": "seuemail@exemplo.com"
}
```

## Scraper

* `adapters/` por domínio (Magalu, Americanas, fallback via OG/JSON-LD)
* Requests com headers realistas (httpx)

## Notificações (MVP)

* **E-mail** pelo SMTP (configurar `.env`)
* **Web Push** com VAPID (preencher chaves). Front-end simples pode cadastrar o subscription e salvar como `endpoint` do watch.

## Próximos passos

* Debounce/cooldown por watch
* /watches (listar/ativar/desativar)
* Worker APScheduler (rodar `scrape_once` de tempos em tempos)
* Testes de parsers com `tests/fixtures`
* Playwright (V1.5) para páginas com JS pesado
