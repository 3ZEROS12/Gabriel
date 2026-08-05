const dict = {
    "en": {
        "nav_chat": "Chat", "nav_radar": "Radar", "nav_kb": "KB", "nav_settings": "Settings",
        "chat_terminal": "Terminal Context", "chat_waiting_log": "Waiting for terminal tailing...",
        "chat_assistant": "🧠 Assistant", "chat_merge": "Merge to KB", "chat_welcome": "Gabriel launched. Terminal snapshot is actively tracked.",
        "chat_placeholder": "Ask Gabriel...",
        "radar_title": "Agent Radar", "radar_desc": "Monitor active CLI Agents (Antigravity, Claude Code).", "radar_auto": "Auto-detect Active Terminal (Smart Cursor)",
        "sort_mtime_desc": "Last Active (Newest First)", "sort_mtime_asc": "Last Active (Oldest First)",
        "sort_ctime_desc": "Creation Date (Newest First)", "sort_ctime_asc": "Creation Date (Oldest First)",
        "sort_steps_desc": "Volume (Highest First)", "sort_steps_asc": "Volume (Lowest First)",
        "kb_title": "Knowledge Draft", "kb_copy": "Copy Injection Command", "kb_desc": "Review Gabriel's insight before injecting into main CLI.",
        "kb_placeholder": "Gabriel's insights will appear here...", "kb_save": "Save Draft",
        "settings_title": "API & Model Settings", "settings_desc": "Universal configuration for OpenAI-compatible endpoints.",
        "settings_baseurl": "Base URL", "settings_apikey": "API Key", "settings_model": "Model Name",
        "settings_workflow": "Workflow Strategy", "settings_merge": "Knowledge Base Merge", "settings_save": "Save Configuration",
        "mode_manual": "Manual (Geek)", "mode_auto": "Automatic",
        "settings_ui": "UI Preferences", "settings_lang": "Language", "lang_en": "English", "lang_zh": "中文 (Chinese)",
        "copied": "Copied to Clipboard!", "saved": "Saved", "scanning": "Scanning...""radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
    },
    "zh": {
        "nav_chat": "对话", "nav_radar": "雷达", "nav_kb": "知识库", "nav_settings": "设置",
        "chat_terminal": "终端上下文", "chat_waiting_log": "等待终端日志同步...",
        "chat_assistant": "🧠 智能副脑", "chat_merge": "合并至知识库", "chat_welcome": "加百列已启动。正在静默监听终端上下文。",
        "chat_placeholder": "向加百列提问...",
        "radar_title": "终端雷达", "radar_desc": "监控活跃的 CLI 终端 (Antigravity, Claude Code)。", "radar_auto": "自动追踪当前活跃终端 (智能游标)",
        "sort_mtime_desc": "最后活跃 (最近优先)", "sort_mtime_asc": "最后活跃 (最旧优先)",
        "sort_ctime_desc": "创建时间 (最新优先)", "sort_ctime_asc": "创建时间 (最早优先)",
        "sort_steps_desc": "对话体量 (最多优先)", "sort_steps_asc": "对话体量 (最少优先)",
        "kb_title": "知识注入草稿", "kb_copy": "复制注入指令", "kb_desc": "在注入主终端前，检查加百列整理的方案。",
        "kb_placeholder": "加百列的知识草稿将在此生成...", "kb_save": "保存草稿",
        "settings_title": "API 与模型设置", "settings_desc": "配置兼容 OpenAI 格式的大语言模型服务。",
        "settings_baseurl": "接口地址 (Base URL)", "settings_apikey": "密钥 (API Key)", "settings_model": "模型名称 (Model)",
        "settings_workflow": "工作流策略", "settings_merge": "知识库合并模式", "settings_save": "保存配置",
        "mode_manual": "手动提取 (极客)", "mode_auto": "全自动注入",
        "settings_ui": "界面偏好", "settings_lang": "显示语言",
        "copied": "已复制到剪贴板！", "saved": "已保存", "scanning": "正在扫描...""radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
    },
    "ja": {
        "nav_chat": "チャット", "nav_radar": "レーダー", "nav_kb": "知識ベース", "nav_settings": "設定",
        "chat_terminal": "ターミナルコンテキスト", "chat_waiting_log": "ログの同期を待機中...",
        "chat_assistant": "🧠 アシスタント", "chat_merge": "知識ベースに結合", "chat_welcome": "ガブリエルが起動しました。ターミナルを監視中。",
        "chat_placeholder": "ガブリエルに質問する...",
        "radar_title": "エージェントレーダー", "radar_desc": "アクティブな CLI エージェントを監視します。", "radar_auto": "アクティブなターミナルを自動検出",
        "sort_mtime_desc": "最終アクティブ (新しい順)", "sort_mtime_asc": "最終アクティブ (古い順)",
        "sort_ctime_desc": "作成日時 (新しい順)", "sort_ctime_asc": "作成日時 (古い順)",
        "sort_steps_desc": "会話量 (多い順)", "sort_steps_asc": "会話量 (少ない順)",
        "kb_title": "知識ドラフト", "kb_copy": "コマンドをコピー", "kb_desc": "メインCLIに注入する前にインサイトを確認します。",
        "kb_placeholder": "ここにインサイトが生成されます...", "kb_save": "保存",
        "settings_title": "API とモデル設定", "settings_desc": "OpenAI 互換エンドポイントの共通設定。",
        "settings_baseurl": "ベース URL", "settings_apikey": "API キー", "settings_model": "モデル名",
        "settings_workflow": "ワークフロー戦略", "settings_merge": "知識ベース結合モード", "settings_save": "設定を保存",
        "mode_manual": "手動抽出", "mode_auto": "自動注入",
        "settings_ui": "UI 設定", "settings_lang": "表示言語",
        "copied": "コピーしました！", "saved": "保存しました", "scanning": "スキャン中...""radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
    },
    "zh-TW": {
        "nav_chat": "對話", "nav_radar": "雷達", "nav_kb": "知識庫", "nav_settings": "設定",
        "chat_terminal": "終端上下文", "chat_waiting_log": "等待終端日誌同步...",
        "chat_assistant": "🧠 智能副腦", "chat_merge": "合併至知識庫", "chat_welcome": "加百列已啟動。正在靜默監聽終端上下文。",
        "chat_placeholder": "向加百列提問...",
        "radar_title": "終端雷達", "radar_desc": "監控活躍的 CLI 終端 (Antigravity, Claude Code)。", "radar_auto": "自動追蹤當前活躍終端 (智能游標)",
        "sort_mtime_desc": "最後活躍 (最近優先)", "sort_mtime_asc": "最後活躍 (最舊優先)",
        "sort_ctime_desc": "創建時間 (最新優先)", "sort_ctime_asc": "創建時間 (最早優先)",
        "sort_steps_desc": "對話體量 (最多優先)", "sort_steps_asc": "對話體量 (最少優先)",
        "kb_title": "知識注入草稿", "kb_copy": "複製注入指令", "kb_desc": "在注入主終端前，檢查加百列整理的方案。",
        "kb_placeholder": "加百列的知識草稿將在此生成...", "kb_save": "保存草稿",
        "settings_title": "API 與模型設定", "settings_desc": "配置相容 OpenAI 格式的大型語言模型服務。",
        "settings_baseurl": "介面位址 (Base URL)", "settings_apikey": "密鑰 (API Key)", "settings_model": "模型名稱 (Model)",
        "settings_workflow": "工作流策略", "settings_merge": "知識庫合併模式", "settings_save": "保存配置",
        "mode_manual": "手動提取 (極客)", "mode_auto": "全自動注入",
        "settings_ui": "介面偏好", "settings_lang": "顯示語言",
        "copied": "已複製到剪貼簿！", "saved": "已保存", "scanning": "正在掃描...""radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
    },
    "fr": {
        "nav_chat": "Chat", "nav_radar": "Radar", "nav_kb": "Base de C.", "nav_settings": "Paramètres",
        "chat_terminal": "Contexte Terminal", "chat_waiting_log": "En attente des journaux...",
        "chat_assistant": "🧠 Assistant", "chat_merge": "Fusionner à la base", "chat_welcome": "Gabriel lancé. Terminal surveillé.",
        "chat_placeholder": "Demandez à Gabriel...",
        "radar_title": "Radar d'Agents", "radar_desc": "Surveiller les agents CLI actifs.", "radar_auto": "Détection automatique",
        "sort_mtime_desc": "Dernier Actif (Plus récent)", "sort_mtime_asc": "Dernier Actif (Plus ancien)",
        "sort_ctime_desc": "Date de création (Plus récent)", "sort_ctime_asc": "Date de création (Plus ancien)",
        "sort_steps_desc": "Volume (Plus élevé)", "sort_steps_asc": "Volume (Plus bas)",
        "kb_title": "Brouillon", "kb_copy": "Copier la Commande", "kb_desc": "Vérifiez les insights avant l'injection.",
        "kb_placeholder": "Les insights apparaîtront ici...", "kb_save": "Enregistrer",
        "settings_title": "Paramètres API", "settings_desc": "Configuration des points d'accès OpenAI.",
        "settings_baseurl": "URL de base", "settings_apikey": "Clé API", "settings_model": "Modèle",
        "settings_workflow": "Stratégie de Workflow", "settings_merge": "Mode de Fusion", "settings_save": "Enregistrer",
        "mode_manual": "Manuel (Geek)", "mode_auto": "Automatique",
        "settings_ui": "Préférences UI", "settings_lang": "Langue",
        "copied": "Copié !", "saved": "Enregistré", "scanning": "Analyse...""radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
    },
    "es": {
        "nav_chat": "Chat", "nav_radar": "Radar", "nav_kb": "Base C.", "nav_settings": "Ajustes",
        "chat_terminal": "Contexto", "chat_waiting_log": "Esperando registros...",
        "chat_assistant": "🧠 Asistente", "chat_merge": "Combinar a KB", "chat_welcome": "Gabriel iniciado.",
        "chat_placeholder": "Preguntar a Gabriel...",
        "radar_title": "Radar de Agentes", "radar_desc": "Monitorear agentes CLI activos.", "radar_auto": "Detección automática",
        "sort_mtime_desc": "Último Activo (Más reciente)", "sort_mtime_asc": "Último Activo (Más antiguo)",
        "sort_ctime_desc": "Creación (Más reciente)", "sort_ctime_asc": "Creación (Más antiguo)",
        "sort_steps_desc": "Volumen (Mayor)", "sort_steps_asc": "Volumen (Menor)",
        "kb_title": "Borrador", "kb_copy": "Copiar Comando", "kb_desc": "Revisar insights antes de inyectar.",
        "kb_placeholder": "Los insights aparecerán aquí...", "kb_save": "Guardar",
        "settings_title": "Ajustes de API", "settings_desc": "Configuración para endpoints de OpenAI.",
        "settings_baseurl": "URL Base", "settings_apikey": "Clave API", "settings_model": "Modelo",
        "settings_workflow": "Flujo de trabajo", "settings_merge": "Modo de Fusión", "settings_save": "Guardar Ajustes",
        "mode_manual": "Manual (Geek)", "mode_auto": "Automático",
        "settings_ui": "Preferencias de IU", "settings_lang": "Idioma",
        "copied": "¡Copiado!", "saved": "Guardado", "scanning": "Escaneando...""radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
    },
    "ko": {
        "nav_chat": "채팅", "nav_radar": "레이더", "nav_kb": "지식 베이스", "nav_settings": "설정",
        "chat_terminal": "터미널 컨텍스트", "chat_waiting_log": "터미널 대기 중...",
        "chat_assistant": "🧠 어시스턴트", "chat_merge": "KB에 병합", "chat_welcome": "가브리엘 시작됨. 터미널 추적 중.",
        "chat_placeholder": "질문 입력...",
        "radar_title": "에이전트 레이더", "radar_desc": "활성 CLI 에이전트 모니터링.", "radar_auto": "활성 터미널 자동 감지",
        "sort_mtime_desc": "최근 활동 (최신순)", "sort_mtime_asc": "최근 활동 (오래된순)",
        "sort_ctime_desc": "생성일 (최신순)", "sort_ctime_asc": "생성일 (오래된순)",
        "sort_steps_desc": "대화량 (많은순)", "sort_steps_asc": "대화량 (적은순)",
        "kb_title": "지식 초안", "kb_copy": "명령 복사", "kb_desc": "메인 CLI에 주입하기 전 확인.",
        "kb_placeholder": "가브리엘의 통찰력이 생성됩니다...", "kb_save": "초안 저장",
        "settings_title": "API 및 모델 설정", "settings_desc": "OpenAI 호환 엔드포인트 공통 설정.",
        "settings_baseurl": "기본 URL", "settings_apikey": "API 키", "settings_model": "모델명",
        "settings_workflow": "워크플로 전략", "settings_merge": "지식 베이스 병합 모드", "settings_save": "설정 저장",
        "mode_manual": "수동", "mode_auto": "자동",
        "settings_ui": "UI 환경설정", "settings_lang": "언어",
        "copied": "복사 완료!", "saved": "저장됨", "scanning": "스캔 중..."
    }
};

let currentLang = localStorage.getItem('gabriel_lang') || "en";

const urlParams = new URLSearchParams(window.location.search);
let localToken = urlParams.get('token') || sessionStorage.getItem('gabriel_token');
if (localToken) {
    sessionStorage.setItem('gabriel_token', localToken);
    window.history.replaceState({}, document.title, window.location.pathname);
} else {
    document.getElementById('loginModal').style.display = 'flex';
}

document.getElementById('btnLogin').addEventListener('click', () => {
    const t = document.getElementById('inputToken').value.trim();
    if (t) {
        sessionStorage.setItem('gabriel_token', t);
        window.location.reload();
    }
});

function applyLang() {
    const map = dict[currentLang];
    document.querySelectorAll('[data-i18n]').forEach(el => {
        el.innerText = map[el.getAttribute('data-i18n')];
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        el.placeholder = map[el.getAttribute('data-i18n-placeholder')];
    });
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
        if(map[el.getAttribute('data-i18n-title')]) {
            el.title = map[el.getAttribute('data-i18n-title')];
        }
    });
}

document.getElementById('langSelect').value = currentLang;

document.getElementById('langSelect').addEventListener('change', (e) => {
    currentLang = e.target.value;
    localStorage.setItem('gabriel_lang', currentLang);
    applyLang();
});

// --- Window Controls ---
document.getElementById('btnClose').addEventListener('click', () => {
    if(window.pywebview && window.pywebview.api) { window.pywebview.api.close(); }
});
document.getElementById('btnMin').addEventListener('click', () => {
    if(window.pywebview && window.pywebview.api) { window.pywebview.api.minimize(); }
});

// --- Tab Navigation ---
const navItems = document.querySelectorAll('.nav-item');
const tabPanes = document.querySelectorAll('.tab-pane');

navItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        navItems.forEach(n => n.classList.remove('active'));
        tabPanes.forEach(p => p.classList.add('hidden'));
        
        item.classList.add('active');
        const target = document.getElementById(item.dataset.tab);
        target.classList.remove('hidden');
        
        if(item.dataset.tab === 'tab-monitor') fetchAgents();
        if(item.dataset.tab === 'tab-kb') loadKb();
    });
});

// --- Toggle Context Panel ---
const contextPanel = document.getElementById('contextPanel');
const dragResizer = document.getElementById('dragResizer');
document.getElementById('btnToggleContext').addEventListener('click', () => {
    contextPanel.classList.toggle('collapsed');
    dragResizer.style.display = contextPanel.classList.contains('collapsed') ? 'none' : 'block';
});

// Toggle Context Panel with Ctrl+B
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key.toLowerCase() === 'b') {
        e.preventDefault();
        document.getElementById('btnToggleContext').click();
    }
});

// --- Resizer Logic ---
let isResizing = false;
dragResizer.addEventListener('mousedown', (e) => {
    isResizing = true;
    document.body.style.cursor = 'col-resize';
});
document.addEventListener('mousemove', (e) => {
    if (!isResizing) return;
    const newWidth = e.clientX - 60; // 60 is sidebar width
    if (newWidth > 200 && newWidth < window.innerWidth - 300) {
        contextPanel.style.flex = 'none';
        contextPanel.style.width = newWidth + 'px';
    }
});
document.addEventListener('mouseup', () => {
    if (isResizing) {
        isResizing = false;
        document.body.style.cursor = 'default';
    }
});

// --- API Settings ---
const cfgBaseUrl = document.getElementById('cfgBaseUrl');
const cfgApiKey = document.getElementById('cfgApiKey');
const cfgModel = document.getElementById('cfgModel');
let currentMergeMode = "manual";
let currentTargetAgent = "auto";

async function loadConfig() {
    try {
        const res = await fetch('/api/config');
        const data = await res.json();
        if(data.base_url) cfgBaseUrl.value = data.base_url;
        if(data.api_key) cfgApiKey.value = data.api_key;
        if(data.model) cfgModel.value = data.model;
        currentMergeMode = data.merge_mode || "manual";
        document.querySelector(`input[name="mergeMode"][value="${currentMergeMode}"]`).checked = true;
        currentTargetAgent = data.target_agent || "auto";
        document.getElementById('toggleAutoCursor').checked = (currentTargetAgent === "auto");
    } catch(e) { console.error("Config load error", e); }
}

async function saveConfig() {
    currentMergeMode = document.querySelector('input[name="mergeMode"]:checked').value;
    const isAuto = document.getElementById('toggleAutoCursor').checked;
    if(isAuto) currentTargetAgent = "auto";
    
    const payload = {
        base_url: cfgBaseUrl.value,
        api_key: cfgApiKey.value,
        model: cfgModel.value,
        merge_mode: currentMergeMode,
        target_agent: currentTargetAgent
    };
    try {
        await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Gabriel-Token': localToken
            },
            body: JSON.stringify(payload)
        });
    } catch(e) { console.error("Save config error", e); }
}

document.getElementById('btnSaveConfig').addEventListener('click', async () => {
    const btn = document.getElementById('btnSaveConfig');
    const originalText = btn.innerText;
    btn.innerText = dict[currentLang].saving || "Saving...";
    await saveConfig();
    btn.innerText = dict[currentLang].saved;
    setTimeout(() => btn.innerText = originalText, 1500);
});

// --- Agent Monitor ---
document.getElementById('toggleAutoCursor').addEventListener('change', async (e) => {
    if(e.target.checked) {
        currentTargetAgent = "auto";
        await saveConfig();
        fetchAgents();
    }
});

async function fetchAgents() {
    const list = document.getElementById('agentList');
    list.innerHTML = `<div class="agent-item">${dict[currentLang].scanning}</div>`;
    try {
        await fetch('/api/agents', {
            headers: { 'X-Gabriel-Token': localToken }
        })
        .then(r => r.json())
        .then(agents => {
            // Sorting Logic
            const sortMode = document.getElementById('agentSortSelect').value;
            const [sortKey, sortDir] = sortMode.split('_');
            
            agents.sort((a, b) => {
                let valA = a[sortKey] || 0;
                let valB = b[sortKey] || 0;
                if (sortDir === 'asc') return valA - valB;
                return valB - valA;
            });

            list.innerHTML = "";
            if (agents.length === 0) {
                list.innerHTML = `
                    <div class="agent-item" style="justify-content: center; opacity: 0.5; flex-direction: column; padding: 32px 16px;">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:12px; color:var(--text-secondary);"><circle cx="12" cy="12" r="10"></circle><path d="M12 8v4m0 4h.01"></path></svg>
                        <div class="agent-name" style="color:var(--text-secondary);" data-i18n="radar_empty">No Active Agents Found</div>
                        <div style="font-size:0.75rem; color:var(--text-secondary); margin-top:8px; text-align:center;" data-i18n="radar_no_agents_hint">Start an agent in your terminal to see it here</div>
                    </div>
                `;
                applyLang();
                return;
            }
            agents.forEach(a => {
                const isLocked = (currentTargetAgent === a.path);
                const date = new Date(a.mtime * 1000).toLocaleString();
                const div = document.createElement('div');
                div.className = `agent-item ${isLocked ? 'locked' : ''}`;
                div.innerHTML = `
                    <div class="agent-info">
                        <span class="agent-name">${a.name} ${isLocked ? '🔒' : ''}</span>
                        <span class="agent-time">⏱ ${dict[currentLang].agent_last_active || "Last Active:"} ${date} &nbsp;|&nbsp; 📊 ${dict[currentLang].agent_volume || "Volume:"} ${a.steps || 0} ${dict[currentLang].agent_steps || "steps"}</span>
                    </div>
                    ${!isLocked ? `<button class="btn-outline" style="padding:4px 8px; font-size:0.75rem;" onclick="lockAgent('${a.path.replace(/\\/g, '\\\\')}')">${dict[currentLang].btn_lock || 'Lock'}</button>` : ''}
                `;
                list.appendChild(div);
            });
        });
    } catch(e) {
        list.innerHTML = `<div class="agent-item">${dict[currentLang].err_fetching_agents || "Error fetching agents."}</div>`;
    }
}
window.lockAgent = async function(path) {
    document.getElementById('toggleAutoCursor').checked = false;
    currentTargetAgent = path;
    await saveConfig();
    fetchAgents();
}

document.getElementById('agentSortSelect').addEventListener('change', fetchAgents);

// --- Knowledge Base ---
const kbEditor = document.getElementById('kbEditor');
async function loadKb() {
    try {
        const res = await fetch('/api/kb', {
            headers: { 'X-Gabriel-Token': localToken }
        });
        const data = await res.json();
        kbEditor.value = data.content || "";
    } catch(e) {}
}
document.getElementById('btnSaveKb').addEventListener('click', async () => {
    const content = document.getElementById('kbEditor').value;
    await fetch('/api/kb', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Gabriel-Token': localToken
        },
        body: JSON.stringify({content: content})
    });

    const btn = document.getElementById('btnSaveKb');
    const originalText = btn.innerText;
    btn.innerText = dict[currentLang].saved;
    setTimeout(() => btn.innerText = originalText, 1500);
});

// Markdown Preview Toggle
const btnPreviewKb = document.getElementById('btnPreviewKb');
const kbEditor = document.getElementById('kbEditor');
const kbPreview = document.getElementById('kbPreview');
btnPreviewKb.addEventListener('click', () => {
    if (kbPreview.classList.contains('hidden')) {
        // Show Preview
        const rawHtml = window.marked ? marked.parse(kbEditor.value) : kbEditor.value;
        kbPreview.innerHTML = window.DOMPurify ? DOMPurify.sanitize(rawHtml) : rawHtml;
        kbPreview.classList.remove('hidden');
        kbEditor.style.display = 'none';
        btnPreviewKb.innerText = dict[currentLang].btn_edit || '✏️ Edit';
        btnPreviewKb.style.background = 'var(--accent)';
        btnPreviewKb.style.color = '#fff';
    } else {
        // Show Editor
        kbPreview.classList.add('hidden');
        kbEditor.style.display = 'block';
        btnPreviewKb.innerText = dict[currentLang].btn_preview || '👁 Preview';
        btnPreviewKb.style.background = 'transparent';
        btnPreviewKb.style.color = 'var(--text-primary)';
    }
});

document.getElementById('btnCopyInject').addEventListener('click', () => {
    const textToCopy = "Please read Gabriel_Insight.md in the current directory and execute the fix.";
    navigator.clipboard.writeText(textToCopy).then(() => {
        const btn = document.getElementById('btnCopyInject');
        const originalText = btn.innerText;
        btn.innerText = dict[currentLang].copied;
        setTimeout(() => btn.innerText = originalText, 2000);
    });
});

// --- Chart.js Telemetry ---
let telemetryChart;
const chartData = {
    labels: Array(20).fill(''),
    datasets: [{
        label: 'Neural Activity (Load %)',
        data: Array(20).fill(5),
        borderColor: 'rgba(16, 185, 129, 0.8)', // var(--success)
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointRadius: 0
    }]
};

function initChart() {
    const ctx = document.getElementById('telemetryChart');
    if (!ctx) return;
    telemetryChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 300 },
            plugins: { legend: { display: false } },
            scales: {
                y: { min: 0, max: 100, display: false },
                x: { display: false }
            }
        }
    });

    // Idle cooldown loop
    setInterval(() => {
        const lastVal = chartData.datasets[0].data[19];
        const newVal = Math.max(5, lastVal - (lastVal * 0.2)); // Cool down by 20%
        chartData.datasets[0].data.shift();
        chartData.datasets[0].data.push(newVal);
        telemetryChart.update('none');
    }, 1000);
}

// --- WebSocket & Chat ---
let ws;
let reconnectAttempts = 0;
const MAX_RECONNECT_DELAY = 30000;

function connectWebSocket() {
    if (!localToken) return;
    const wsUrl = `ws://${window.location.host || '127.0.0.1:8080'}/ws?token=${localToken}`;
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        document.getElementById('wsStatus').classList.remove('disconnected');
        document.getElementById('wsStatus').classList.add('connected');
        reconnectAttempts = 0;
    };
    
    ws.onclose = (e) => {
        document.getElementById('wsStatus').classList.remove('connected');
        document.getElementById('wsStatus').classList.add('disconnected');
        
        const delay = Math.min(1000 * Math.pow(1.5, reconnectAttempts), MAX_RECONNECT_DELAY);
        setTimeout(() => {
            reconnectAttempts++;
            connectWebSocket();
        }, delay);
    };

    ws.onerror = (err) => {
        ws.close();
    };

    let currentAiMessageDiv = null;
    let currentAiMessageContent = "";

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === "context_update") {
            // Spike the telemetry chart to simulate agent computation
            if (telemetryChart) {
                const spike = Math.min(100, Math.floor(Math.random() * 40) + 60);
                chartData.datasets[0].data.shift();
                chartData.datasets[0].data.push(spike);
                telemetryChart.update('none');
            }
            
            // Render logs and preserve scroll position
            const display = document.getElementById('contextDisplay');
            if (display) {
                const parent = display.parentElement;
                const isAtBottom = parent.scrollHeight - parent.scrollTop - parent.clientHeight < 50;
                
                display.innerHTML = window.DOMPurify ? DOMPurify.sanitize(msg.content) : msg.content;
                
                if (isAtBottom) {
                    parent.scrollTop = parent.scrollHeight;
                }
            }
            
            // Trigger Telemetry Pulse (Agent MX Design)
            const pulse = document.getElementById('telemetryPulse');
            if (pulse) {
                pulse.style.background = 'var(--success)';
                pulse.style.boxShadow = '0 0 10px var(--success)';
                setTimeout(() => {
                    pulse.style.background = 'transparent';
                    pulse.style.boxShadow = 'none';
                }, 150);
            }
        } else if (msg.type === "ai_response_start") {
            currentAiMessageContent = "";
            currentAiMessageDiv = createMessageDiv('ai-message');
            document.getElementById('chatHistory').appendChild(currentAiMessageDiv);
        } else if (msg.type === "ai_response_chunk") {
            currentAiMessageContent += msg.content;
            if(window.marked) {
                const parsed = marked.parse(currentAiMessageContent);
                currentAiMessageDiv.innerHTML = window.DOMPurify ? DOMPurify.sanitize(parsed) : parsed;
            } else {
                currentAiMessageDiv.innerText = currentAiMessageContent;
            }
            const container = document.getElementById('chatHistory');
            container.scrollTop = container.scrollHeight;
        } else if (msg.type === "ai_response_end") {
            currentAiMessageDiv = null;
        } else if (msg.type === "ai_response") {
            appendMessage(msg.content, 'ai-message');
        } else if (msg.type === "sys_message") {
            appendMessage(msg.content, 'sys-message');
        }
    };
    ws.onclose = () => {
        document.getElementById('statusText').innerText = dict[currentLang].status_disconnected || "Disconnected";
        document.querySelector('.status-dot').classList.add('disconnected');
        setTimeout(connectWebSocket, 3000);
    };
}

function createMessageDiv(className) {
    const div = document.createElement('div');
    div.className = `message ${className}`;
    return div;
}

function appendMessage(text, className) {
    const container = document.getElementById('chatHistory');
    const div = createMessageDiv(className);
    if(className === 'ai-message' && window.marked) {
        const parsed = marked.parse(text);
        div.innerHTML = window.DOMPurify ? DOMPurify.sanitize(parsed) : parsed;
    } else {
        div.innerText = text;
    }
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

document.getElementById('btnSend').addEventListener('click', () => {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (text && ws && ws.readyState === WebSocket.OPEN) {
        appendMessage(text, 'user-message');
        ws.send(JSON.stringify({type: "chat", content: text}));
        input.value = '';
    }
});
document.getElementById('chatInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('btnSend').click();
    }
});

document.getElementById('btnMerge').addEventListener('click', () => {
    initTabs();
    initChart();
    document.getElementById('btnStartTerminal').addEventListener('click', () => {
    if(ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({type: "merge_kb", content: ""}));
        appendMessage(dict[currentLang].gen_draft || "⏳ Generating solution draft...", "sys-message");
    }
});
});

// Init
applyLang();
loadConfig();
connectWebSocket();
