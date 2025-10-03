chrome.runtime.onInstalled.addListener(() => {
  console.log("Derrubador de Preços instalado.");
});

function notify(title, message) {
  chrome.notifications.create({
    type: "basic",
    iconUrl: "icons/icon128.png",
    title,
    message
  });
}
