import re

with open("elektra_web.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add CSS
css_to_add = """
  /* Modal Settings */
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.8); display: none; justify-content: center; align-items: center; z-index: 10000; backdrop-filter: blur(4px); }
  .modal-overlay.open { display: flex; }
  .modal { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 24px; width: 400px; max-width: 90%; }
  .modal h3 { color: var(--accent); margin-bottom: 16px; font-family: 'Syne', sans-serif; }
  .modal input { width: 100%; padding: 10px; background: var(--bg); border: 1px solid var(--border); color: var(--text); border-radius: 6px; margin-bottom: 16px; font-family: 'JetBrains Mono', monospace; }
  .modal-actions { display: flex; justify-content: flex-end; gap: 8px; }
  .modal-btn { padding: 8px 16px; border-radius: 6px; cursor: pointer; border: none; font-weight: bold; }
  .btn-cancel { background: var(--card); color: var(--text); }
  .btn-save { background: var(--accent); color: var(--bg); }
  
  /* Select */
  .agent-model-select { background: var(--bg); color: var(--text); border: 1px solid var(--border); border-radius: 4px; font-size: 9px; padding: 2px 4px; max-width: 120px; outline: none; }
</style>"""
content = content.replace("</style>", css_to_add)

# 2. Add header button and i18n
content = content.replace(
    '<div class="section-title">Agentes activos</div>',
    '<div class="section-title" data-i18n="agents_title">Agentes activos</div>'
)
content = content.replace(
    '<div class="section-title" style="margin-top:8px">Log evolutivo</div>',
    '<div class="section-title" style="margin-top:8px" data-i18n="evo_title">Log evolutivo</div>'
)
content = content.replace(
    '<div class="evo-line" style="color:var(--muted)">— esperando primera ejecución —</div>',
    '<div class="evo-line" style="color:var(--muted)" data-i18n="waiting_run">— esperando primera ejecución —</div>'
)
content = content.replace(
    '<span id="problems-count" style="color:var(--muted)">0 problemas resueltos</span>',
    '<span id="problems-count" style="color:var(--muted)">0 <span data-i18n="problems">problemas resueltos</span></span>'
)
content = content.replace('<label>GENERACIONES:</label>', '<label data-i18n="generations">GENERACIONES:</label>')
content = content.replace('<button class="btn-send" id="send-btn" onclick="sendMessage()">ENVIAR</button>', '<button class="btn-send" id="send-btn" onclick="sendMessage()" data-i18n="send">ENVIAR</button>')
content = content.replace('placeholder="Describe el problema a resolver..."', 'placeholder="Describe el problema a resolver..." data-i18n-ph="placeholder"')

content = content.replace(
    '<div class="conn-status">',
    '<button class="btn-icon" onclick="openSettings()" title="Configuración">⚙️</button>\n      <div class="conn-status">'
)

# 3. Add modal HTML
modal_html = """
  <!-- Settings Modal -->
  <div class="modal-overlay" id="settings-modal">
    <div class="modal">
      <h3 data-i18n="settings_title">Configuración de API</h3>
      <label style="font-size: 11px; color: var(--muted); display: block; margin-bottom: 8px;" data-i18n="api_key_label">Ollama API Key:</label>
      <input type="password" id="api-key-input" placeholder="sk-..." />
      <div class="modal-actions">
        <button class="modal-btn btn-cancel" onclick="closeSettings()" data-i18n="cancel">Cancelar</button>
        <button class="modal-btn btn-save" onclick="saveSettings()" data-i18n="save">Guardar</button>
      </div>
    </div>
  </div>
"""
content = content.replace("</main>\n</div>", "</main>\n</div>\n" + modal_html)

# 4. Add JS state
js_state = """
// ─── Estado ───────────────────────────────────
let availableModels = [];
const i18n = {
  es: {
    connecting: "conectando...", connected: "conectado", reconnecting: "reconectando...",
    agents_title: "Agentes activos", evo_title: "Log evolutivo",
    problems: "problemas resueltos", generations: "GENERACIONES:",
    send: "ENVIAR", settings_title: "Configuración de API", api_key_label: "API Key (Ollama/OpenAI):",
    cancel: "Cancelar", save: "Guardar", thinking: "pensando...",
    waiting_run: "— esperando primera ejecución —",
    placeholder: "Describe el problema a resolver...",
    start_msg: "Hola. Me llamo Elektra.\\n\\nSoy un sistema de inteligencia colectiva formado por 4 agentes..."
  },
  en: {
    connecting: "connecting...", connected: "connected", reconnecting: "reconnecting...",
    agents_title: "Active agents", evo_title: "Evolution log",
    problems: "problems solved", generations: "GENERATIONS:",
    send: "SEND", settings_title: "API Settings", api_key_label: "API Key (Ollama/OpenAI):",
    cancel: "Cancel", save: "Save", thinking: "thinking...",
    waiting_run: "— waiting for first run —",
    placeholder: "Describe the problem to solve...",
    start_msg: "Hello. I am Elektra.\\n\\nI'm a collective intelligence system..."
  }
};
let lang = navigator.language.startsWith('es') ? 'es' : 'en';

function t(key) { return i18n[lang][key] || key; }

function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
  const textInput = document.getElementById('input-text');
  if(textInput) textInput.placeholder = t('placeholder');
  const conn = document.getElementById('conn-label');
  if(conn && conn.textContent === 'conectando...') conn.textContent = t('connecting');
}

async function fetchModels() {
  try {
    const res = await fetch('/api/models');
    availableModels = await res.json();
  } catch (e) { console.error("Error fetching models", e); }
}

function openSettings() {
  document.getElementById('settings-modal').classList.add('open');
  fetch('/api/key').then(r=>r.json()).then(d => {
    document.getElementById('api-key-input').placeholder = d.has_key ? d.preview : "sk-...";
  });
}
function closeSettings() { document.getElementById('settings-modal').classList.remove('open'); }
async function saveSettings() {
  const val = document.getElementById('api-key-input').value;
  if(val) {
    await fetch('/api/key', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({key: val}) });
  }
  closeSettings();
  setTimeout(() => window.location.reload(), 500);
}

function changeAgentModel(agent_id, new_model) {
  if(ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'set_model', agent_id: agent_id, model: new_model }));
  }
}

let ws = null;
"""
content = re.sub(r'// ─── Estado ───────────────────────────────────.*?let ws = null;', js_state, content, flags=re.DOTALL)


# 5. Modify renderAgents
render_agents_new = """
function renderAgents(agents) {
  const container = document.getElementById('agents-list');
  container.innerHTML = '';
  agents.forEach(agent => {
    const pct = Math.round(agent.fitness * 100);
    
    let modelSelector = `<span class="agent-model">${agent.model}</span>`;
    if (availableModels.length > 0) {
      let selectHtml = `<select class="agent-model-select" onchange="changeAgentModel('${agent.id}', this.value)" ${isProcessing ? 'disabled' : ''}>`;
      availableModels.forEach(m => {
        const selected = m.id === agent.model ? 'selected' : '';
        selectHtml += `<option value="${m.id}" ${selected}>${m.id} (${m.tier_label})</option>`;
      });
      selectHtml += `</select>`;
      modelSelector = selectHtml;
    }

    container.innerHTML += `
      <div class="agent-card" id="card-${agent.id}">
        <div class="agent-status"></div>
        <div class="agent-header">
          <span class="agent-id">${agent.id.replace('agente_','').toUpperCase()}</span>
          ${modelSelector}
        </div>
        <div class="agent-role">${agent.role}</div>
        <div class="fitness-bar"><div class="fitness-fill" style="width:${pct}%"></div></div>
        <div class="fitness-label">
          <span>fitness ${agent.fitness.toFixed(2)}</span>
          <span>gen ${agent.generation} · mut ${agent.mutations}</span>
        </div>
      </div>`;
  });
}
"""
content = re.sub(r'function renderAgents\(agents\) \{.*?\}\n', render_agents_new, content, flags=re.DOTALL)

# Update texts
content = content.replace("conectado", "t('connected')").replace("reconectando...", "t('reconnecting')").replace("'conectado' : 'reconectando...'", "t('connected') : t('reconnecting')")

# Setup calls on init
content = content.replace("connect();", "applyTranslations();\nfetchModels().then(() => connect());")

with open("elektra_web.html", "w", encoding="utf-8") as f:
    f.write(content)
