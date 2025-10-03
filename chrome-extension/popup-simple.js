// ALTERE APÓS DEPLOY NO RAILWAY
const API_BASE = "http://localhost:8000"; // Trocar por: https://SEU-PROJETO.up.railway.app

document.addEventListener('DOMContentLoaded', function() {
  // Pegar URL da aba atual
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    if (tabs[0] && tabs[0].url && !tabs[0].url.startsWith('chrome://')) {
      document.getElementById('url').value = tabs[0].url;
    }
  });

  // Evento do botão monitorar
  document.getElementById("monitor").addEventListener("click", async () => {
    const url = document.getElementById("url").value.trim();
    const targetPrice = document.getElementById("target_price").value.trim();
    const dropPercent = document.getElementById("drop_percent").value.trim();

    if (!url) {
      document.getElementById("status").innerText = "URL é obrigatória";
      return;
    }

    if (!targetPrice && !dropPercent) {
      document.getElementById("status").innerText = "Defina preço alvo OU queda %";
      return;
    }

    const payload = {
      url,
      target_price: targetPrice ? parseFloat(targetPrice) : null,
      drop_percent: dropPercent ? parseFloat(dropPercent) : null,
      channel: "webpush",
      endpoint: "chrome-user"
    };

    try {
      document.getElementById("status").innerText = "Processando...";
      
      const res = await fetch(`${API_BASE}/track`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Erro ${res.status}: ${text}`);
      }

      const data = await res.json();
      document.getElementById("status").innerText = `✅ Produto monitorado! ID: ${data.product_id}`;
      
      // Limpar campos após sucesso
      document.getElementById("target_price").value = "";
      document.getElementById("drop_percent").value = "";
      
    } catch (err) {
      document.getElementById("status").innerText = `❌ Falha: ${err.message}`;
    }
  });
});
