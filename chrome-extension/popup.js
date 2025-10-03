// Configurações - ALTERE APÓS DEPLOY NO RAILWAY
const API_BASE = "http://localhost:8000"; // Trocar por: https://SEU-PROJETO.up.railway.app
const STORAGE_KEYS = {
  API_URL: 'apiUrl',
  TRACKED_PRODUCTS: 'trackedProducts'
};

// Elementos DOM
let urlInput, targetPriceInput, dropPercentInput, apiUrlInput, trackBtn, statusDiv, form;

// Inicialização
document.addEventListener('DOMContentLoaded', async () => {
  initializeElements();
  await loadSavedSettings();
  setupEventListeners();
  await getCurrentTabUrl();
});

function initializeElements() {
  urlInput = document.getElementById('url');
  targetPriceInput = document.getElementById('targetPrice');
  dropPercentInput = document.getElementById('dropPercent');
  apiUrlInput = document.getElementById('apiUrl');
  trackBtn = document.getElementById('trackBtn');
  statusDiv = document.getElementById('status');
  form = document.getElementById('trackForm');
}

async function loadSavedSettings() {
  try {
    const result = await chrome.storage.sync.get([STORAGE_KEYS.API_URL]);
    if (result[STORAGE_KEYS.API_URL]) {
      apiUrlInput.value = result[STORAGE_KEYS.API_URL];
    }
  } catch (error) {
    console.error('Erro ao carregar configurações:', error);
  }
}

function setupEventListeners() {
  // Formulário principal
  form.addEventListener('submit', handleTrackSubmit);
  
  // Botão para usar URL atual
  document.getElementById('getCurrentUrl').addEventListener('click', getCurrentTabUrl);
  
  // Salvar API URL quando mudar
  apiUrlInput.addEventListener('change', saveApiUrl);
  
  // Botões do footer
  document.getElementById('viewHistory').addEventListener('click', openHistoryPage);
  document.getElementById('settings').addEventListener('click', openSettingsPage);
  
  // Validação em tempo real
  urlInput.addEventListener('input', validateForm);
  targetPriceInput.addEventListener('input', validateForm);
  dropPercentInput.addEventListener('input', validateForm);
}

async function getCurrentTabUrl() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url && !tab.url.startsWith('chrome://')) {
      urlInput.value = tab.url;
      validateForm();
      showStatus('URL da aba atual carregada', 'info');
    }
  } catch (error) {
    console.error('Erro ao obter URL da aba:', error);
  }
}

async function saveApiUrl() {
  try {
    await chrome.storage.sync.set({
      [STORAGE_KEYS.API_URL]: apiUrlInput.value
    });
  } catch (error) {
    console.error('Erro ao salvar API URL:', error);
  }
}

function validateForm() {
  const hasUrl = urlInput.value.trim() !== '';
  const hasTarget = targetPriceInput.value !== '' || dropPercentInput.value !== '';
  
  trackBtn.disabled = !hasUrl || !hasTarget;
  
  if (hasUrl && !hasTarget) {
    showStatus('Defina um preço alvo ou percentual de queda', 'info');
  } else if (statusDiv.textContent.includes('Defina um preço')) {
    clearStatus();
  }
}

async function handleTrackSubmit(event) {
  event.preventDefault();
  
  const url = urlInput.value.trim();
  const targetPrice = targetPriceInput.value ? parseFloat(targetPriceInput.value) : null;
  const dropPercent = dropPercentInput.value ? parseFloat(dropPercentInput.value) : null;
  const apiUrl = apiUrlInput.value.trim() || DEFAULT_API_URL;
  
  // Validações
  if (!url) {
    showStatus('URL do produto é obrigatória', 'error');
    return;
  }
  
  if (!targetPrice && !dropPercent) {
    showStatus('Defina um preço alvo ou percentual de queda', 'error');
    return;
  }
  
  if (targetPrice && targetPrice <= 0) {
    showStatus('Preço alvo deve ser maior que zero', 'error');
    return;
  }
  
  if (dropPercent && (dropPercent <= 0 || dropPercent > 100)) {
    showStatus('Percentual de queda deve estar entre 0 e 100', 'error');
    return;
  }
  
  // Enviar requisição
  await trackProduct(url, targetPrice, dropPercent, apiUrl);
}

async function trackProduct(url, targetPrice, dropPercent, apiUrl) {
  setLoading(true);
  
  try {
    const requestBody = {
      url: url,
      channel: 'webpush',
      endpoint: 'chrome-extension-user'
    };
    
    if (targetPrice) requestBody.target_price = targetPrice;
    if (dropPercent) requestBody.drop_percent = dropPercent;
    
    const response = await fetch(`${apiUrl}/track`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });
    
    const data = await response.json();
    
    if (response.ok) {
      await saveTrackedProduct(data.product_id, url, targetPrice, dropPercent);
      showStatus(`Produto monitorado com sucesso! ID: ${data.product_id}`, 'success');
      
      // Limpar formulário após sucesso
      setTimeout(() => {
        targetPriceInput.value = '';
        dropPercentInput.value = '';
        clearStatus();
      }, 3000);
      
      // Mostrar notificação
      await showNotification('Produto Adicionado', `Monitoramento ativo para: ${getDomainFromUrl(url)}`);
      
    } else {
      throw new Error(data.detail || 'Erro desconhecido');
    }
    
  } catch (error) {
    console.error('Erro ao rastrear produto:', error);
    
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      showStatus('Erro de conexão. Verifique se a API está rodando.', 'error');
    } else {
      showStatus(`Erro: ${error.message}`, 'error');
    }
  } finally {
    setLoading(false);
  }
}

async function saveTrackedProduct(productId, url, targetPrice, dropPercent) {
  try {
    const result = await chrome.storage.sync.get([STORAGE_KEYS.TRACKED_PRODUCTS]);
    const trackedProducts = result[STORAGE_KEYS.TRACKED_PRODUCTS] || [];
    
    const newProduct = {
      id: productId,
      url: url,
      targetPrice: targetPrice,
      dropPercent: dropPercent,
      addedAt: new Date().toISOString(),
      domain: getDomainFromUrl(url)
    };
    
    trackedProducts.push(newProduct);
    
    await chrome.storage.sync.set({
      [STORAGE_KEYS.TRACKED_PRODUCTS]: trackedProducts
    });
  } catch (error) {
    console.error('Erro ao salvar produto rastreado:', error);
  }
}

function getDomainFromUrl(url) {
  try {
    return new URL(url).hostname.replace('www.', '');
  } catch {
    return 'Desconhecido';
  }
}

async function showNotification(title, message) {
  try {
    await chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon48.png',
      title: title,
      message: message
    });
  } catch (error) {
    console.error('Erro ao mostrar notificação:', error);
  }
}

function setLoading(loading) {
  trackBtn.disabled = loading;
  
  if (loading) {
    document.querySelector('.btn-text').style.display = 'none';
    document.querySelector('.btn-loading').style.display = 'inline';
  } else {
    document.querySelector('.btn-text').style.display = 'inline';
    document.querySelector('.btn-loading').style.display = 'none';
  }
}

function showStatus(message, type = 'info') {
  statusDiv.textContent = message;
  statusDiv.className = `status ${type}`;
  statusDiv.style.display = 'block';
}

function clearStatus() {
  statusDiv.textContent = '';
  statusDiv.className = 'status';
  statusDiv.style.display = 'none';
}

function openHistoryPage() {
  chrome.tabs.create({
    url: `${apiUrlInput.value || DEFAULT_API_URL}/docs`
  });
}

function openSettingsPage() {
  // Por enquanto, apenas mostra as configurações atuais
  const apiUrl = apiUrlInput.value || DEFAULT_API_URL;
  showStatus(`API configurada: ${apiUrl}`, 'info');
}
