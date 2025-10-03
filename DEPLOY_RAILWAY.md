# 🚀 DEPLOY NO RAILWAY - PASSO A PASSO

## 📋 **CHECKLIST PRÉ-DEPLOY**

✅ **Backend preparado:**
- ✅ `requirements.txt` com `psycopg2-binary`
- ✅ `Procfile` com `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- ✅ `app/main.py` com CORS e StaticFiles
- ✅ Database compatível com PostgreSQL
- ✅ Worker para scraping automático

✅ **Extensão Chrome preparada:**
- ✅ `manifest.json` atualizado
- ✅ `popup.html` e `popup-simple.js`
- ✅ `background-simple.js`
- ✅ Ícones (usar SVG convertido para PNG)

---

## 🔧 **1. SUBIR PARA O GITHUB**

```bash
# No PowerShell, dentro da pasta do projeto:
git init
git add .
git commit -m "feat: prepare for Railway deployment"
git branch -M main

# Criar repositório no GitHub primeiro, depois:
git remote add origin https://github.com/SEU-USUARIO/derrubador-de-precos.git
git push -u origin main
```

---

## 🚂 **2. DEPLOY NO RAILWAY**

### **2.1 Criar Projeto**
1. Acesse [railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub Repo**
3. Conecte sua conta GitHub
4. Selecione o repositório `derrubador-de-precos`

### **2.2 Configurar Serviço Web**
1. **Variables** → Adicionar:
   ```
   ENV=prod
   ```

2. **Add Database** → **PostgreSQL**
   - Railway criará automaticamente uma instância PostgreSQL
   - Copie a `POSTGRESQL_URL` gerada

3. **Variables** → Adicionar:
   ```
   DATABASE_URL=postgresql+psycopg2://user:pass@host:port/db
   ```
   *(Use a URL completa que o Railway forneceu)*

4. **Settings** do serviço:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### **2.3 Configurar Worker (Scraping 24/7)**
1. **New Service** no mesmo projeto
2. **Source:** Mesmo repositório GitHub
3. **Name:** `worker`
4. **Variables:** Copiar as mesmas do serviço web (`ENV`, `DATABASE_URL`)
5. **Settings:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python -m app.worker`

---

## 🌐 **3. TESTAR DEPLOY**

Após o deploy, você terá uma URL como:
`https://seu-projeto-abc123.up.railway.app`

### **Testes:**
- ✅ `https://seu-projeto.up.railway.app/ui` → Interface web
- ✅ `https://seu-projeto.up.railway.app/docs` → Swagger API
- ✅ `https://seu-projeto.up.railway.app/status` → Status da API

---

## 🔧 **4. ATUALIZAR EXTENSÃO CHROME**

### **4.1 Atualizar API_BASE**
No arquivo `chrome-extension/popup-simple.js`:

```javascript
// ANTES:
const API_BASE = "http://localhost:8000";

// DEPOIS:
const API_BASE = "https://seu-projeto-abc123.up.railway.app";
```

### **4.2 Atualizar manifest.json**
```json
{
  "host_permissions": [
    "https://seu-projeto-abc123.up.railway.app/*"
  ]
}
```

### **4.3 Gerar Ícones PNG**
Converter o `chrome-extension/icons/icon.svg` para:
- `icon16.png` (16x16)
- `icon32.png` (32x32) 
- `icon48.png` (48x48)
- `icon128.png` (128x128)

**Ferramentas online:**
- [Convertio](https://convertio.co/svg-png/)
- [CloudConvert](https://cloudconvert.com/svg-to-png)

---

## ✅ **5. VALIDAÇÃO FINAL**

### **Backend (Railway):**
- [ ] `/ui` abre e funciona
- [ ] `/docs` mostra Swagger
- [ ] POST `/track` aceita produtos
- [ ] Worker está rodando (logs no Railway)
- [ ] Database PostgreSQL conectado

### **Extensão Chrome:**
- [ ] Carregada em `chrome://extensions/`
- [ ] Popup abre sem erros
- [ ] Consegue monitorar produtos
- [ ] API_BASE aponta para Railway

### **Integração:**
- [ ] Extensão → Railway API funciona
- [ ] Produtos aparecem na interface `/ui`
- [ ] Histórico de preços é salvo

---

## 🎯 **PRÓXIMOS PASSOS**

1. **Publicar extensão:** Chrome Web Store (taxa ~$5)
2. **Domínio personalizado:** Conectar domínio próprio no Railway
3. **Monitoramento:** Configurar alertas de uptime
4. **Analytics:** Adicionar tracking de uso

---

## 🆘 **TROUBLESHOOTING**

### **Erro de CORS:**
- Verificar `allow_origins=["*"]` no `main.py`

### **Database não conecta:**
- Verificar `DATABASE_URL` nas variáveis
- Confirmar que contém `postgresql+psycopg2://`

### **Worker não roda:**
- Verificar logs no Railway
- Confirmar que `app/worker.py` existe
- Verificar comando: `python -m app.worker`

### **Extensão não conecta:**
- Verificar `API_BASE` no `popup-simple.js`
- Confirmar `host_permissions` no `manifest.json`
- Testar API manualmente no navegador
