// Background Script para Derrubador de Preços
// Manifest V3 Service Worker

// Configurações
const ALARM_NAME = 'checkPrices';
const CHECK_INTERVAL = 60; // minutos

// Instalação da extensão
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('Derrubador de Preços instalado:', details.reason);
  
  // Configurar alarme para verificações periódicas
  await setupPeriodicChecks();
  
  // Mostrar notificação de boas-vindas
  if (details.reason === 'install') {
    await showWelcomeNotification();
  }
});

// Inicialização quando o service worker inicia
chrome.runtime.onStartup.addListener(async () => {
  console.log('Service worker iniciado');
  await setupPeriodicChecks();
});

// Configurar verificações periódicas
async function setupPeriodicChecks() {
  try {
    // Limpar alarmes existentes
    await chrome.alarms.clear(ALARM_NAME);
    
    // Criar novo alarme
    await chrome.alarms.create(ALARM_NAME, {
      delayInMinutes: CHECK_INTERVAL,
      periodInMinutes: CHECK_INTERVAL
    });
    
    console.log(`Alarme configurado para verificar a cada ${CHECK_INTERVAL} minutos`);
  } catch (error) {
    console.error('Erro ao configurar alarmes:', error);
  }
}

// Listener para alarmes
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === ALARM_NAME) {
    console.log('Executando verificação periódica de preços');
    await checkTrackedProducts();
  }
});

// Verificar produtos rastreados
async function checkTrackedProducts() {
  try {
    const result = await chrome.storage.sync.get(['trackedProducts', 'apiUrl']);
    const trackedProducts = result.trackedProducts || [];
    const apiUrl = result.apiUrl || 'http://localhost:8000';
    
    if (trackedProducts.length === 0) {
      console.log('Nenhum produto sendo rastreado');
      return;
    }
    
    console.log(`Verificando ${trackedProducts.length} produtos...`);
    
    for (const product of trackedProducts) {
      try {
        await checkSingleProduct(product, apiUrl);
        // Pequeno delay entre requisições para não sobrecarregar a API
        await sleep(1000);
      } catch (error) {
        console.error(`Erro ao verificar produto ${product.id}:`, error);
      }
    }
    
  } catch (error) {
    console.error('Erro na verificação periódica:', error);
  }
}

// Verificar um produto específico
async function checkSingleProduct(product, apiUrl) {
  try {
    // Forçar verificação do produto
    const response = await fetch(`${apiUrl}/scrape-now?product_id=${product.id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const result = await response.json();
    console.log(`Produto ${product.id} verificado:`, result);
    
    // Se houve atualização, buscar detalhes do produto
    if (result.updated) {
      await checkForPriceAlerts(product, apiUrl);
    }
    
  } catch (error) {
    console.error(`Erro ao verificar produto ${product.id}:`, error);
  }
}

// Verificar se há alertas de preço
async function checkForPriceAlerts(product, apiUrl) {
  try {
    const response = await fetch(`${apiUrl}/products/${product.id}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const productData = await response.json();
    const currentPrice = productData.current_price;
    
    if (!currentPrice) return;
    
    // Verificar se atingiu preço alvo
    if (product.targetPrice && currentPrice <= product.targetPrice) {
      await showPriceAlert(product, currentPrice, 'target');
    }
    
    // Para verificar queda percentual, precisaríamos do histórico
    // Por simplicidade, vamos apenas notificar sobre preço alvo por enquanto
    
  } catch (error) {
    console.error(`Erro ao verificar alertas para produto ${product.id}:`, error);
  }
}

// Mostrar alerta de preço
async function showPriceAlert(product, currentPrice, alertType) {
  try {
    const domain = getDomainFromUrl(product.url);
    let title, message;
    
    if (alertType === 'target') {
      title = '🎯 Preço Alvo Atingido!';
      message = `${domain}: R$ ${currentPrice.toFixed(2)} (alvo: R$ ${product.targetPrice.toFixed(2)})`;
    } else {
      title = '📉 Queda de Preço Detectada!';
      message = `${domain}: R$ ${currentPrice.toFixed(2)}`;
    }
    
    await chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon48.png',
      title: title,
      message: message,
      buttons: [
        { title: 'Ver Produto' },
        { title: 'Parar Monitoramento' }
      ]
    });
    
    // Tocar som de notificação (se permitido)
    try {
      await chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon48.png',
        title: '🔔',
        message: 'Novo alerta de preço!'
      });
    } catch (e) {
      // Ignorar se não conseguir tocar som
    }
    
  } catch (error) {
    console.error('Erro ao mostrar alerta:', error);
  }
}

// Listener para cliques em notificações
chrome.notifications.onButtonClicked.addListener(async (notificationId, buttonIndex) => {
  if (buttonIndex === 0) {
    // Botão "Ver Produto" - abrir URL do produto
    // Por simplicidade, vamos abrir a API docs
    const result = await chrome.storage.sync.get(['apiUrl']);
    const apiUrl = result.apiUrl || 'http://localhost:8000';
    chrome.tabs.create({ url: `${apiUrl}/docs` });
  } else if (buttonIndex === 1) {
    // Botão "Parar Monitoramento" - implementar futuramente
    console.log('Parar monitoramento solicitado');
  }
  
  // Limpar notificação
  chrome.notifications.clear(notificationId);
});

// Mostrar notificação de boas-vindas
async function showWelcomeNotification() {
  try {
    await chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon48.png',
      title: 'Derrubador de Preços Instalado!',
      message: 'Clique no ícone da extensão para começar a monitorar preços.'
    });
  } catch (error) {
    console.error('Erro ao mostrar notificação de boas-vindas:', error);
  }
}

// Utilitários
function getDomainFromUrl(url) {
  try {
    return new URL(url).hostname.replace('www.', '');
  } catch {
    return 'Produto';
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Listener para mensagens do popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'checkNow') {
    checkTrackedProducts().then(() => {
      sendResponse({ success: true });
    }).catch(error => {
      sendResponse({ success: false, error: error.message });
    });
    return true; // Indica que a resposta será assíncrona
  }
});
