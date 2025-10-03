# 🚀 **GUIA COMPLETO DE DEPLOY - Derrubador de Preços**

## 📋 **PARTE 1: Deploy do Backend no Railway**

### **1. Preparação do Repositório**

✅ **Arquivos necessários já criados:**
- `requirements.txt` (com pydantic-settings)
- `Procfile` (configurado para Railway)
- `app/main.py` (com CORS e rota raiz)
- `.env.example` (template de configuração)

### **2. Deploy no Railway**

**Passo 1: Criar conta no Railway**
1. Acesse [railway.app](https://railway.app)
2. Faça login com GitHub

**Passo 2: Conectar repositório**
1. Clique em "New Project"
2. Selecione "Deploy from GitHub repo"
3. Escolha o repositório `derrubador-de-precos`

**Passo 3: Configurar o projeto**
1. Railway detectará automaticamente que é Python
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Passo 4: Configurar variáveis de ambiente**
```env
ENV=prod
DATABASE_URL=sqlite:///./data.db
TZ=America/Sao_Paulo
```

**Passo 5: Deploy**
1. Clique em "Deploy"
2. Aguarde o build completar
3. Anote a URL gerada (ex: `https://seu-app.up.railway.app`)

### **3. Testar a API**

**Interface Web:** `https://seu-app.up.railway.app/ui`
**Documentação:** `https://seu-app.up.railway.app/docs`

Você deve ver:
- ✅ Interface web moderna funcionando
- ✅ Swagger UI funcionando
- ✅ Endpoints disponíveis
- ✅ Rota raiz retornando mensagem de sucesso

---

## 🔧 **PARTE 2: Instalar Extensão Chrome**

### **1. Preparar Extensão**

✅ **Arquivos da extensão já criados:**
```
chrome-extension/
├── manifest.json
├── popup.html
├── popup.css
├── popup.js
└── background.js
```

### **2. Criar Ícones da Extensão**

**Você precisa criar os ícones (ou usar temporários):**
- `icon16.png` (16x16px)
- `icon32.png` (32x32px) 
- `icon48.png` (48x48px)
- `icon128.png` (128x128px)

**Dica:** Use um gerador online ou crie um ícone simples com:
- Fundo azul/roxo
- Símbolo de preço (R$ ou gráfico)

### **3. Instalar no Chrome**

**Passo 1: Ativar modo desenvolvedor**
1. Abra Chrome → `chrome://extensions/`
2. Ative "Modo do desenvolvedor" (canto superior direito)

**Passo 2: Carregar extensão**
1. Clique "Carregar sem compactação"
2. Selecione a pasta `chrome-extension/`
3. A extensão aparecerá na lista

**Passo 3: Configurar**
1. Clique no ícone da extensão na barra
2. Configure a "URL da API" para sua URL do Railway
3. Exemplo: `https://seu-app.up.railway.app`

---

## 🎯 **PARTE 3: Como Usar o Sistema Completo**

### **1. Monitorar um Produto**

**Via Interface Web (Mais Fácil):**
1. Acesse `https://seu-app.railway.app/ui`
2. Cole a URL do produto
3. Defina preço alvo OU percentual de queda
4. Escolha canal de notificação (email/webpush)
5. Clique "Monitorar Produto"

**Via Extensão Chrome:**
1. Vá para uma página de produto (Magalu, Americanas, etc.)
2. Clique no ícone da extensão
3. Clique "Usar URL Atual" (ou cole manualmente)
4. Defina preço alvo OU percentual de queda
5. Clique "Monitorar Produto"

**Exemplo prático:**
```
URL: https://www.magazineluiza.com.br/notebook-gamer/p/abc123
Preço Alvo: R$ 2.500,00
Queda %: 15%
Email: seu-email@gmail.com
```

### **2. Verificar Status**

**Via Interface Web (Recomendado):**
1. Acesse `https://seu-app.railway.app/ui`
2. Vá na aba "Meus Produtos"
3. Veja todos os produtos monitorados
4. Clique "🔄 Verificar Agora" para forçar checagem
5. Clique "📊 Ver Histórico" para ver dados detalhados

**Via API (navegador):**
- Lista: `https://seu-app.railway.app/products`
- Detalhes: `https://seu-app.railway.app/products/1`
- Histórico: `https://seu-app.railway.app/products/1/history`
- Forçar check: `https://seu-app.railway.app/scrape-now?product_id=1`

**Via Extensão:**
- Clique "Ver Histórico" para abrir a documentação da API

### **3. Receber Notificações**

A extensão verificará automaticamente a cada 60 minutos e mostrará notificações do Chrome quando:
- Preço atingir o valor alvo
- Houver queda percentual significativa

---

## ⚙️ **PARTE 4: Configurações Avançadas**

### **1. Configurar Email (Opcional)**

**No Railway, adicione as variáveis:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASS=sua-senha-de-app
SMTP_FROM="Derrubador <seu-email@gmail.com>"
```

**Para Gmail:**
1. Ative verificação em 2 etapas
2. Gere uma "Senha de app"
3. Use essa senha no `SMTP_PASS`

### **2. Worker Automático (Opcional)**

**Para verificações automáticas no servidor:**
1. No Railway, adicione um novo serviço
2. Configure para rodar: `python -m app.worker`
3. Isso verificará todos os produtos a cada 3 horas

### **3. Monitoramento**

**Logs do Railway:**
- Acesse o dashboard do projeto
- Vá em "Deployments" → "View Logs"
- Monitore requisições e erros

---

## 🔍 **PARTE 5: Troubleshooting**

### **Problemas Comuns**

**1. "Erro de conexão" na extensão**
```
Solução: Verifique se a URL da API está correta
Teste: Acesse https://seu-app.railway.app/ no navegador
```

**2. "Build failed" no Railway**
```
Solução: Verifique se requirements.txt está correto
Verifique se Procfile existe e está correto
```

**3. "Produto não encontrado"**
```
Solução: Alguns sites podem bloquear scraping
Teste com URLs simples (sem parâmetros UTM)
Sites suportados: Magalu, Americanas
```

**4. Extensão não aparece**
```
Solução: Verifique se manifest.json está válido
Recarregue a extensão em chrome://extensions/
```

**5. Notificações não funcionam**
```
Solução: Permita notificações do Chrome
Verifique se a extensão tem permissões
```

### **Testando o Sistema**

**1. Teste básico:**
```bash
curl https://seu-app.railway.app/
# Deve retornar: {"message": "Derrubador de Preços API está rodando 🚀"}
```

**2. Teste de tracking:**
```bash
curl -X POST https://seu-app.railway.app/track \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.magazineluiza.com.br/produto/teste",
    "target_price": 100.0,
    "channel": "webpush",
    "endpoint": "test-user"
  }'
```

---

## 📊 **PARTE 6: Próximos Passos**

### **Melhorias Futuras:**

1. **Dashboard Web:** Interface web para gerenciar produtos
2. **Mais Lojas:** Adapters para Amazon, Mercado Livre, etc.
3. **Telegram Bot:** Notificações via Telegram
4. **Histórico Avançado:** Gráficos de preço
5. **Alertas Inteligentes:** ML para detectar padrões

### **Escalabilidade:**

1. **Banco PostgreSQL:** Migrar do SQLite
2. **Redis:** Cache para melhor performance
3. **Celery:** Queue para processamento assíncrono
4. **Docker:** Containerização completa

---

## 🎉 **Resumo Final**

**Você agora tem:**
✅ API completa rodando no Railway  
✅ **Interface Web moderna integrada**  
✅ Extensão Chrome profissional  
✅ Sistema de notificações  
✅ Monitoramento automático  
✅ Suporte a múltiplas lojas  

**Para usar diariamente:**
1. **OPÇÃO 1 (Mais Fácil):** Acesse `https://seu-app.railway.app/ui`
2. **OPÇÃO 2:** Instale a extensão Chrome e configure a URL da API
3. Adicione produtos para monitorar
4. Defina preços alvo ou quedas percentuais
5. Receba notificações automáticas!

**🚀 Seu sistema de monitoramento de preços está pronto para uso profissional!**
