from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .core.db import get_db
from .models.product import Product
from .models.price_history import PriceHistory
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/ui/history/{product_id}", response_class=HTMLResponse)
def history_page(product_id: int, db: Session = Depends(get_db)):
    # Buscar produto
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, detail="Produto não encontrado")
    
    # Buscar histórico dos últimos 30 dias
    since = datetime.utcnow() - timedelta(days=30)
    history = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .filter(PriceHistory.captured_at >= since)
        .order_by(PriceHistory.captured_at.desc())
        .limit(10)  # Apenas as 10 últimas verificações
        .all()
    )
    
    # Formatação segura dos preços
    current_price = f"R$ {product.current_price:.2f}" if product.current_price else "N/A"
    last_checked = product.last_checked_at.strftime('%d/%m/%Y %H:%M') if product.last_checked_at else 'N/A'
    
    # Verificar se houve mudanças de preço
    price_changes = []
    if len(history) > 1:
        for i in range(len(history) - 1):
            current_entry = history[i]
            previous_entry = history[i + 1]
            
            if current_entry.price != previous_entry.price:
                change = {
                    'date': current_entry.captured_at.strftime('%d/%m/%Y %H:%M'),
                    'old_price': f"R$ {previous_entry.price:.2f}",
                    'new_price': f"R$ {current_entry.price:.2f}",
                    'difference': current_entry.price - previous_entry.price,
                    'percentage': ((current_entry.price - previous_entry.price) / previous_entry.price) * 100
                }
                price_changes.append(change)
    
    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Histórico de Preços - {product.title or 'Produto'}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #a8e6cf 0%, #88d8a3 100%);
                min-height: 100vh;
                padding: 20px;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}

            .header {{
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}

            .header h1 {{
                font-size: 28px;
                margin-bottom: 8px;
                font-weight: 600;
            }}

            .header p {{
                opacity: 0.9;
                font-size: 16px;
            }}

            .content {{
                padding: 30px;
            }}

            .product-info {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
                border-left: 4px solid #4CAF50;
            }}

            .product-title {{
                font-size: 20px;
                font-weight: 600;
                color: #333;
                margin-bottom: 10px;
            }}

            .product-details {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }}

            .detail-item {{
                display: flex;
                flex-direction: column;
            }}

            .detail-label {{
                font-size: 12px;
                color: #666;
                text-transform: uppercase;
                font-weight: 500;
                margin-bottom: 4px;
            }}

            .detail-value {{
                font-size: 16px;
                color: #333;
                font-weight: 500;
            }}

            .chart-container {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #e9ecef;
                margin-bottom: 20px;
            }}

            .chart-title {{
                font-size: 18px;
                font-weight: 600;
                color: #333;
                margin-bottom: 20px;
                text-align: center;
            }}

            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}

            .stat-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                border: 1px solid #e9ecef;
            }}

            .stat-number {{
                font-size: 24px;
                font-weight: 600;
                color: #4CAF50;
                margin-bottom: 5px;
            }}

            .stat-label {{
                color: #666;
                font-size: 14px;
            }}

            .actions {{
                display: flex;
                gap: 15px;
                justify-content: center;
                margin-top: 30px;
            }}

            .btn {{
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
                text-decoration: none;
                display: inline-block;
                text-align: center;
            }}

            .btn-primary {{
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
            }}

            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(76, 175, 80, 0.3);
            }}

            .btn-secondary {{
                background: #f8f9fa;
                color: #495057;
                border: 1px solid #dee2e6;
            }}

            .btn-secondary:hover {{
                background: #e9ecef;
            }}

            @media (max-width: 768px) {{
                .container {{
                    margin: 10px;
                    border-radius: 10px;
                }}

                .content {{
                    padding: 20px;
                }}

                .header {{
                    flex-direction: column;
                    text-align: center;
                    gap: 15px;
                }}

                .actions {{
                    flex-direction: column;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="header-content">
                    <h1>Histórico de Preços</h1>
                    <p>Mudanças de preço detectadas</p>
                </div>
            </div>

            <div class="content">
                <div class="product-info">
                    <div class="product-title">{product.title or 'Produto sem título'}</div>
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">Preço Atual</div>
                            <div class="info-value">{current_price}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Status</div>
                            <div class="info-value">{'Em estoque' if product.in_stock else 'Fora de estoque'}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Domínio</div>
                            <div class="info-value">{product.domain}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Última Verificação</div>
                            <div class="info-value">{last_checked}</div>
                        </div>
                    </div>
                </div>

                <div class="changes-section">
                    <div class="section-title">Mudanças de Preço Recentes</div>
                    {''.join([f'''
                    <div class="change-item">
                        <div>
                            <div class="change-date">{change['date']}</div>
                            <div class="price-change">
                                <span class="old-price">{change['old_price']}</span>
                                <span>→</span>
                                <span class="new-price">{change['new_price']}</span>
                            </div>
                        </div>
                        <div class="change-indicator {'price-down' if change['difference'] < 0 else 'price-up'}">
                            {'+' if change['difference'] > 0 else ''}{change['percentage']:.1f}%
                        </div>
                    </div>
                    ''' for change in price_changes]) if price_changes else '''
                    <div class="no-changes">
                        <h4>Nenhuma mudança de preço detectada</h4>
                        <p>O preço se manteve estável nas últimas verificações.</p>
                    </div>
                    '''}
                </div>

                <div class="actions">
                    <a href="/ui" class="btn btn-secondary">Voltar</a>
                    <a href="{product.url}" target="_blank" class="btn btn-primary">Ver Produto</a>
                    <button onclick="forceCheck()" class="btn btn-primary">Verificar Agora</button>
                </div>
            </div>
        </div>

        <script>
            async function forceCheck() {{
                try {{
                    const response = await fetch('/scrape-now?product_id={product_id}', {{
                        method: 'POST'
                    }});
                    
                    if (response.ok) {{
                        alert('Verificação realizada com sucesso! Recarregando página...');
                        window.location.reload();
                    }} else {{
                        alert('Erro na verificação. Tente novamente.');
                    }}
                }} catch (error) {{
                    alert('Erro: ' + error.message);
                }}
            }}
        </script>
    </body>
    </html>
    """

@router.get("/ui", response_class=HTMLResponse)
def ui():
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Derrubador de Preços - Interface Web</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #a8e6cf 0%, #88d8a3 100%);
                min-height: 100vh;
                padding: 20px;
            }

            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }

            .header {
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }


            .header h1 {
                font-size: 28px;
                margin-bottom: 8px;
                font-weight: 600;
            }

            .header p {
                opacity: 0.9;
                font-size: 16px;
                margin: 0;
            }

            .content {
                padding: 30px;
            }

            .tabs {
                display: flex;
                border-bottom: 2px solid #f0f0f0;
                margin-bottom: 30px;
            }

            .tab {
                padding: 12px 24px;
                cursor: pointer;
                border: none;
                background: none;
                font-size: 14px;
                font-weight: 500;
                color: #666;
                transition: all 0.2s;
            }

            .tab.active {
                color: #4CAF50;
                border-bottom: 2px solid #4CAF50;
            }

            .tab-content {
                display: none;
            }

            .tab-content.active {
                display: block;
                animation: fadeIn 0.3s ease;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .form-group {
                margin-bottom: 20px;
            }

            .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }

            label {
                display: block;
                margin-bottom: 6px;
                font-weight: 500;
                color: #333;
                font-size: 14px;
            }

            input[type="text"], input[type="url"], input[type="number"], input[type="email"] {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                font-size: 14px;
                transition: all 0.2s ease;
                background: #fafbfc;
            }

            input:focus {
                outline: none;
                border-color: #4CAF50;
                background: white;
                box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
            }

            .btn {
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
                text-decoration: none;
                display: inline-block;
                text-align: center;
            }

            .btn-primary {
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
            }

            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(76, 175, 80, 0.3);
            }

            .btn-secondary {
                background: #f8f9fa;
                color: #495057;
                border: 1px solid #dee2e6;
            }

            .btn-secondary:hover {
                background: #e9ecef;
            }

            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none !important;
            }

            .status {
                margin-top: 20px;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
                display: none;
            }

            .status.success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }

            .status.error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }

            .status.info {
                background: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }

            .products-list {
                margin-top: 20px;
            }

            .product-card {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 15px;
                background: #fafbfc;
                transition: all 0.2s ease;
            }

            .product-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }

            .product-title {
                font-weight: 600;
                color: #333;
                margin-bottom: 8px;
                font-size: 16px;
            }

            .product-url {
                color: #667eea;
                font-size: 12px;
                margin-bottom: 10px;
                word-break: break-all;
            }

            .product-price {
                font-size: 18px;
                font-weight: 600;
                color: #28a745;
                margin-bottom: 10px;
            }

            .product-actions {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }

            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .stat-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                border: 1px solid #e9ecef;
            }

            .stat-number {
                font-size: 24px;
                font-weight: 600;
                color: #667eea;
                margin-bottom: 5px;
            }

            .stat-label {
                color: #666;
                font-size: 14px;
            }

            @media (max-width: 768px) {
                .container {
                    margin: 10px;
                    border-radius: 10px;
                }

                .content {
                    padding: 20px;
                }

                .form-row {
                    grid-template-columns: 1fr;
                }

                .tabs {
                    overflow-x: auto;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="header-content">
                    <h1>Derrubador de Preços</h1>
                    <p>Monitore preços e receba alertas quando houver quedas</p>
                </div>
            </div>

            <div class="content">
                <div class="tabs">
                    <button class="tab active" onclick="switchTab('track')">Monitorar Produto</button>
                    <button class="tab" onclick="switchTab('products')">Meus Produtos</button>
                    <button class="tab" onclick="switchTab('stats')">Estatísticas</button>
                </div>

                <!-- Tab: Monitorar Produto -->
                <div id="track-tab" class="tab-content active">
                    <form id="trackForm">
                        <div class="form-group">
                            <label for="url">URL do Produto *</label>
                            <input type="url" id="url" placeholder="https://www.magazineluiza.com.br/produto..." required>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="targetPrice">Preço Alvo (R$)</label>
                                <input type="number" id="targetPrice" placeholder="1999.90" step="0.01" min="0">
                            </div>
                            <div class="form-group">
                                <label for="dropPercent">Queda Percentual (%)</label>
                                <input type="number" id="dropPercent" placeholder="15" step="0.1" min="0" max="100">
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="channel">Canal de Notificação</label>
                                <select id="channel" style="width: 100%; padding: 12px 15px; border: 2px solid #e1e5e9; border-radius: 8px; background: #fafbfc;">
                                    <option value="email">Email</option>
                                    <option value="webpush">Web Push</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="endpoint">Email/Endpoint</label>
                                <input type="email" id="endpoint" placeholder="seu-email@exemplo.com">
                            </div>
                        </div>

                        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 10px;">
                            Monitorar Produto
                        </button>
                    </form>

                    <div id="trackStatus" class="status"></div>
                </div>

                <!-- Tab: Meus Produtos -->
                <div id="products-tab" class="tab-content">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3>Produtos Monitorados</h3>
                        <button class="btn btn-secondary" onclick="loadProducts()">Atualizar Lista</button>
                    </div>
                    <div id="productsList" class="products-list">
                        <p style="text-align: center; color: #666; padding: 40px;">Carregando produtos...</p>
                    </div>
                </div>

                <!-- Tab: Estatísticas -->
                <div id="stats-tab" class="tab-content">
                    <div class="stats" id="statsContainer">
                        <div class="stat-card">
                            <div class="stat-number" id="totalProducts">-</div>
                            <div class="stat-label">Produtos Monitorados</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="totalChecks">-</div>
                            <div class="stat-label">Verificações Hoje</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="avgPrice">-</div>
                            <div class="stat-label">Preço Médio</div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="/docs" class="btn btn-primary" target="_blank">Ver Documentação da API</a>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Estado global
            let products = [];
            let currentTab = 'track';

            // Inicialização
            document.addEventListener('DOMContentLoaded', function() {
                setupEventListeners();
                loadProducts();
            });

            function setupEventListeners() {
                document.getElementById('trackForm').addEventListener('submit', handleTrackSubmit);
                document.getElementById('channel').addEventListener('change', updateEndpointPlaceholder);
            }

            function switchTab(tabName) {
                // Atualizar botões
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                document.querySelector(`[onclick="switchTab('${tabName}')"]`).classList.add('active');

                // Atualizar conteúdo
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                document.getElementById(`${tabName}-tab`).classList.add('active');

                currentTab = tabName;

                // Carregar dados específicos da aba
                if (tabName === 'products') {
                    loadProducts();
                } else if (tabName === 'stats') {
                    loadStats();
                }
            }

            function updateEndpointPlaceholder() {
                const channel = document.getElementById('channel').value;
                const endpoint = document.getElementById('endpoint');
                
                if (channel === 'email') {
                    endpoint.type = 'email';
                    endpoint.placeholder = 'seu-email@exemplo.com';
                } else {
                    endpoint.type = 'text';
                    endpoint.placeholder = 'web-push-endpoint';
                }
            }

            async function handleTrackSubmit(event) {
                event.preventDefault();
                
                const url = document.getElementById('url').value.trim();
                const targetPrice = document.getElementById('targetPrice').value;
                const dropPercent = document.getElementById('dropPercent').value;
                const channel = document.getElementById('channel').value;
                const endpoint = document.getElementById('endpoint').value.trim();

                // Validações
                if (!url) {
                    showStatus('trackStatus', 'URL do produto é obrigatória', 'error');
                    return;
                }

                if (!targetPrice && !dropPercent) {
                    showStatus('trackStatus', 'Defina um preço alvo ou percentual de queda', 'error');
                    return;
                }

                if (!endpoint) {
                    showStatus('trackStatus', 'Email/endpoint é obrigatório', 'error');
                    return;
                }

                // Preparar dados
                const requestBody = {
                    url: url,
                    channel: channel,
                    endpoint: endpoint
                };

                if (targetPrice) requestBody.target_price = parseFloat(targetPrice);
                if (dropPercent) requestBody.drop_percent = parseFloat(dropPercent);

                // Enviar requisição
                await trackProduct(requestBody);
            }

            async function trackProduct(data) {
                const btn = document.querySelector('#trackForm button[type="submit"]');
                const originalText = btn.innerHTML;
                
                try {
                    btn.innerHTML = '<span class="loading"></span>Processando...';
                    btn.disabled = true;

                    const response = await fetch('/track', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();

                    if (response.ok) {
                        showStatus('trackStatus', `Produto monitorado com sucesso! ID: ${result.product_id}`, 'success');
                        
                        // Limpar formulário
                        document.getElementById('trackForm').reset();
                        
                        // Atualizar lista de produtos se estiver na aba
                        if (currentTab === 'products') {
                            setTimeout(loadProducts, 1000);
                        }
                    } else {
                        throw new Error(result.detail || 'Erro desconhecido');
                    }

                } catch (error) {
                    console.error('Erro:', error);
                    showStatus('trackStatus', `Erro: ${error.message}`, 'error');
                } finally {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                }
            }

            async function loadProducts() {
                const container = document.getElementById('productsList');
                
                try {
                    container.innerHTML = '<div style="text-align: center; padding: 20px;"><span class="loading"></span> Carregando produtos...</div>';
                    
                    const response = await fetch('/products');
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    
                    const products = await response.json();
                    
                    if (products.length === 0) {
                        container.innerHTML = `
                            <div style="text-align: center; padding: 40px; color: #666;">
                                <h4>Nenhum produto monitorado ainda</h4>
                                <p>Vá para a aba "Monitorar Produto" para adicionar seu primeiro produto!</p>
                                <button class="btn btn-primary" onclick="switchTab('track')" style="margin-top: 15px;">
                                    Adicionar Produto
                                </button>
                            </div>
                        `;
                        return;
                    }
                    
                    let html = '';
                    products.forEach(product => {
                        const domain = getDomainFromUrl(product.url);
                        const price = product.current_price ? `R$ ${product.current_price.toFixed(2)}` : 'Preço não disponível';
                        const stock = product.in_stock ? 'Em estoque' : 'Fora de estoque';
                        
                        html += `
                            <div class="product-card">
                                <div class="product-title">${product.title || 'Produto sem título'}</div>
                                <div class="product-url">${domain} • ID: ${product.id}</div>
                                <div class="product-price">${price}</div>
                                <div style="margin-bottom: 15px; font-size: 14px; color: #666;">
                                    ${stock} • Última verificação: ${formatDate(product.last_checked_at)}
                                </div>
                                <div class="product-actions">
                                    <button class="btn btn-secondary" onclick="scrapeProduct(${product.id})">
                                        Verificar Agora
                                    </button>
                                    <button class="btn btn-secondary" onclick="viewHistory(${product.id})">
                                        Ver Histórico
                                    </button>
                                    <a href="${product.url}" target="_blank" class="btn btn-secondary">
                                        Ver Produto
                                    </a>
                                </div>
                            </div>
                        `;
                    });
                    
                    container.innerHTML = html;
                    
                    // Atualizar estatísticas
                    document.getElementById('totalProducts').textContent = products.length;
                    
                } catch (error) {
                    console.error('Erro ao carregar produtos:', error);
                    container.innerHTML = `
                        <div style="text-align: center; padding: 40px; color: #e74c3c;">
                            ❌ Erro ao carregar produtos: ${error.message}
                            <br><br>
                            <button class="btn btn-secondary" onclick="loadProducts()">Tentar Novamente</button>
                        </div>
                    `;
                }
            }

            async function loadStats() {
                try {
                    // Estatísticas simuladas - em produção, criar endpoints específicos
                    document.getElementById('totalProducts').textContent = '0';
                    document.getElementById('totalChecks').textContent = '0';
                    document.getElementById('avgPrice').textContent = 'R$ 0';
                } catch (error) {
                    console.error('Erro ao carregar estatísticas:', error);
                }
            }

            async function scrapeProduct(productId) {
                try {
                    const response = await fetch(`/scrape-now?product_id=${productId}`, {
                        method: 'POST'
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        alert('Verificação realizada com sucesso!');
                        loadProducts();
                    } else {
                        alert('Erro na verificação: ' + (result.detail || 'Erro desconhecido'));
                    }
                } catch (error) {
                    alert('Erro: ' + error.message);
                }
            }

            function viewHistory(productId) {
                window.open(`/ui/history/${productId}`, '_blank');
            }

            function getDomainFromUrl(url) {
                try {
                    return new URL(url).hostname.replace('www.', '');
                } catch {
                    return 'Desconhecido';
                }
            }

            function formatDate(dateString) {
                try {
                    const date = new Date(dateString);
                    return date.toLocaleString('pt-BR', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                } catch {
                    return 'Data inválida';
                }
            }

            function showStatus(elementId, message, type) {
                const statusEl = document.getElementById(elementId);
                statusEl.textContent = message;
                statusEl.className = `status ${type}`;
                statusEl.style.display = 'block';

                // Auto-hide após 5 segundos para mensagens de sucesso
                if (type === 'success') {
                    setTimeout(() => {
                        statusEl.style.display = 'none';
                    }, 5000);
                }
            }

            // Função para testar a API
            async function testAPI() {
                try {
                    const response = await fetch('/');
                    const data = await response.json();
                    console.log('API Status:', data);
                    return response.ok;
                } catch (error) {
                    console.error('API não disponível:', error);
                    return false;
                }
            }

            // Testar API na inicialização
            testAPI().then(isOnline => {
                if (!isOnline) {
                    showStatus('trackStatus', '⚠️ API offline. Verifique se o servidor está rodando.', 'error');
                }
            });
        </script>
    </body>
    </html>
    """
