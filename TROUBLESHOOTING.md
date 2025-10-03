# 🚨 PROBLEMAS COMUNS E SOLUÇÕES - RAILWAY DEPLOY

## ❌ **PROBLEMA 1: "Failed to fetch" na Extensão Chrome**

### **Causa:**
A URL da API na extensão ainda aponta para localhost

### **✅ Solução:**
1. **Após fazer deploy no Railway**, copie a URL do seu projeto
2. **Edite `chrome-extension/popup-simple.js`:**
   ```javascript
   // ANTES:
   const API_BASE = "http://localhost:8000";
   
   // DEPOIS:
   const API_BASE = "https://derrubador-de-precos-production.up.railway.app";
   ```

3. **Recarregue a extensão no Chrome:**
   - Vá em `chrome://extensions/`
   - Clique no botão de "Recarregar" da extensão

---

## ❌ **PROBLEMA 2: "Produto sem título" / "Preço não disponível"**

### **Causa:**
O scraper não conseguiu extrair informações do site

### **✅ Soluções Implementadas:**
1. **Fallback Adapter melhorado** - Agora tenta múltiplas estratégias:
   - OpenGraph meta tags
   - JSON-LD structured data
   - Seletores CSS comuns
   - Regex patterns no texto

2. **Logging detalhado** - Agora mostra no log quando:
   - Preço é encontrado e atualizado
   - Preço não é encontrado
   - Título é atualizado

3. **Error handling** - Scraper não falha completamente se um site der erro

### **🔍 Para debugar:**
- Acesse os logs do Railway
- Procure por mensagens como:
  - `"Preço atualizado para produto X: R$ Y"`
  - `"Preço não encontrado para produto X"`
  - `"Erro ao fazer scraping do produto X"`

---

## ❌ **PROBLEMA 3: "Invalid Date" / Datas vazias**

### **Causa:**
Campos de data não estavam sendo preenchidos corretamente

### **✅ Solução Implementada:**
- **Always update `last_checked_at`** - Mesmo se o scraping falhar
- **Proper datetime handling** - Usando `datetime.utcnow()`
- **Database defaults** - `server_default=func.now()` nos modelos

---

## ❌ **PROBLEMA 4: Histórico de preços vazio**

### **Causa:**
Worker não está rodando no Railway (só o web service)

### **✅ Solução:**
1. **No Railway, criar segundo serviço:**
   - **New Service** → **Deploy from GitHub Repo**
   - **Source:** Mesmo repositório
   - **Name:** `worker`

2. **Configurar o Worker Service:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m app.worker`
   - **Variables:** Copiar as mesmas do web service:
     ```
     ENV=prod
     DATABASE_URL=postgresql+psycopg2://[mesma_url_do_web]
     ```

3. **Verificar se está rodando:**
   - Vá nos logs do worker service
   - Deve aparecer mensagens de scraping a cada 3 horas

---

## ✅ **CHECKLIST DE VALIDAÇÃO**

### **Backend (Web Service):**
- [ ] Deploy feito com sucesso
- [ ] `/docs` abre sem erro
- [ ] `/ui` carrega a interface
- [ ] POST `/track` aceita produtos
- [ ] Logs mostram "API iniciada 🚀"

### **Worker Service:**
- [ ] Segundo serviço criado
- [ ] Start command: `python -m app.worker`
- [ ] Mesmas variáveis de ambiente
- [ ] Logs mostram scraping periódico

### **Extensão Chrome:**
- [ ] `API_BASE` atualizado com URL do Railway
- [ ] Extensão recarregada no Chrome
- [ ] Consegue monitorar produtos sem "Failed to fetch"
- [ ] Produtos aparecem na interface `/ui`

### **Database:**
- [ ] PostgreSQL conectado (Railway Database)
- [ ] Tabelas criadas automaticamente
- [ ] Produtos salvos com `last_checked_at` preenchido
- [ ] Histórico sendo populado pelo worker

---

## 🛠️ **COMANDOS ÚTEIS PARA DEBUG**

### **Testar scraping localmente:**
```python
# No Python/IPython:
from app.core.db import SessionLocal
from app.models.product import Product
from app.scraper.runner import scrape_once

db = SessionLocal()
product = db.query(Product).first()
if product:
    result = scrape_once(db, product)
    print(f"Scraping result: {result}")
```

### **Verificar logs no Railway:**
1. Acesse o dashboard do Railway
2. Clique no serviço (web ou worker)
3. Vá na aba "Deployments"
4. Clique em "View Logs"

### **Testar API manualmente:**
```bash
# Testar se API está respondendo:
curl https://seu-projeto.up.railway.app/docs

# Testar endpoint de track:
curl -X POST "https://seu-projeto.up.railway.app/track" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.magazineluiza.com.br/produto/123","target_price":100,"channel":"email","endpoint":"test@test.com"}'
```

---

## 🎯 **RESULTADO ESPERADO**

Após seguir todas as soluções:

1. **✅ Extensão Chrome** conecta sem erros
2. **✅ Produtos** são salvos com título e preço
3. **✅ Worker** roda automaticamente a cada 3h
4. **✅ Histórico** é populado com dados reais
5. **✅ Logs** mostram atividade de scraping
6. **✅ Interface web** mostra produtos monitorados

**Se ainda houver problemas, verifique os logs específicos de cada serviço no Railway!**
