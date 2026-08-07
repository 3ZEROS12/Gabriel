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
        "copied": "Copied to Clipboard!", "saved": "Saved", "scanning": "Scanning...","radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        "chat_feedback": "Feedback", "kb_recommendation": "Knowledge Base Recommendation"
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
        "copied": "已复制到剪贴板！", "saved": "已保存", "scanning": "正在扫描...", "radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
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
        "copied": "コピーしました！", "saved": "保存しました", "scanning": "スキャン中...", "radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
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
        "copied": "已複製到剪貼簿！", "saved": "已保存", "scanning": "正在掃描...", "radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
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
        "copied": "Copié !", "saved": "Enregistré", "scanning": "Analyse...", "radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
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
        "copied": "¡Copiado!", "saved": "Guardado", "scanning": "Escaneando...", "radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
        
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

if (window.marked && window.hljs) {
    const renderer = new marked.Renderer();
    renderer.code = function(code, language) {
        const validLang = hljs.getLanguage(language) ? language : 'plaintext';
        const highlighted = hljs.highlight(code, { language: validLang }).value;
        const encodedCode = encodeURIComponent(code);
        return `<div class="code-block-wrapper" style="position: relative; margin-bottom: 1em;">
            <button class="code-copy-btn" onclick="navigator.clipboard.writeText(decodeURIComponent('${encodedCode}')); this.innerText='Copied!'; setTimeout(() => this.innerText='Copy', 2000);" style="position: absolute; right: 8px; top: 8px; padding: 4px 8px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; color: #fff; font-size: 12px; cursor: pointer; z-index: 10;">Copy</button>
            <pre><code class="hljs ${validLang}">${highlighted}</code></pre>
        </div>`;
    };
    marked.setOptions({ renderer });
}

// [NOTE]: Using localStorage for token is acceptable for this local single-machine tool. 
// If Gabriel supports multi-user LAN access in the future, this must be re-evaluated.
let localToken = urlParams.get('token') || sessionStorage.getItem('gabriel_token') || localStorage.getItem('gabriel_token');
if (localToken) {
    sessionStorage.setItem('gabriel_token', localToken);
    localStorage.setItem('gabriel_token', localToken);
    window.history.replaceState({}, document.title, window.location.pathname);
} else {
    document.getElementById('loginModal').style.display = 'flex';
}

document.getElementById('btnLogin').addEventListener('click', () => {
    const t = document.getElementById('inputToken').value.trim();
    if (t) {
        sessionStorage.setItem('gabriel_token', t);
        localStorage.setItem('gabriel_token', t);
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
            const chatSelect = document.getElementById('chatTargetAgent');
            const radarSelect = document.getElementById('targetAgent');
            let optionsHTML = `<option value="auto" data-i18n="auto_track">${dict[currentLang]?.auto_track || "Auto-track Newest"}</option>`;

            if (agents.length === 0) {
                if(chatSelect) { chatSelect.innerHTML = optionsHTML; chatSelect.value = "auto"; }
                if(radarSelect) { radarSelect.innerHTML = optionsHTML; radarSelect.value = "auto"; }
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
                const safePath = a.path.replace(/\\/g, '\\\\');
                optionsHTML += `<option value="${safePath}">${a.name}</option>`;
                const isLocked = (currentTargetAgent === a.path);
                const timeAgo = (ts) => {
                    const seconds = Math.floor((new Date() - ts) / 1000);
                    if (seconds < 60) return `${Math.max(0, seconds)} seconds ago`;
                    const minutes = Math.floor(seconds / 60);
                    if (minutes < 60) return `${minutes} minutes ago`;
                    const hours = Math.floor(minutes / 60);
                    if (hours < 24) return `${hours} hours ago`;
                    return `${Math.floor(hours / 24)} days ago`;
                };
                const date = timeAgo(a.mtime * 1000);
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
            
            if(chatSelect) {
                chatSelect.innerHTML = optionsHTML;
                chatSelect.value = currentTargetAgent;
            }
            if(radarSelect) {
                radarSelect.innerHTML = optionsHTML;
                radarSelect.value = currentTargetAgent;
            }
        });
    } catch(e) {
        list.innerHTML = `<div class="agent-item">${dict[currentLang].err_fetching_agents || "Error fetching agents."}</div>`;
    }
}
window.lockAgent = async function(path) {
    const toggleAuto = document.getElementById('toggleAutoCursor');
    if (toggleAuto) toggleAuto.checked = (path === "auto");
    currentTargetAgent = path;
    await saveConfig();
    fetchAgents();
}

document.getElementById('agentSortSelect').addEventListener('change', fetchAgents);
const chatSelectEl = document.getElementById('chatTargetAgent');
if(chatSelectEl) {
    chatSelectEl.addEventListener('change', (e) => lockAgent(e.target.value));
}
const radarSelectEl = document.getElementById('targetAgent');
if(radarSelectEl) {
    radarSelectEl.addEventListener('change', (e) => lockAgent(e.target.value));
}

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
const kbPreview = document.getElementById('kbPreview');
btnPreviewKb.addEventListener('click', () => {
    if (kbPreview.classList.contains('hidden')) {
        // Show Preview
        const rawHtml = window.marked ? marked.parse(kbEditor.value) : kbEditor.value;
        if (window.DOMPurify) {
            kbPreview.innerHTML = DOMPurify.sanitize(rawHtml);
        } else {
            kbPreview.textContent = rawHtml;
        }
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



// ==========================================
// Safe Rendering
// ==========================================
function renderAgentContent(codeEl, content) {
    // Round 52: DOM Memory Profiling & Cap (prevent UI freezing from 10k line logs)
    const lines = content.split('\n');
    let displayContent = content;
    if (lines.length > 800) {
        displayContent = "...\n[Gabriel DOM Capper: Older logs hidden for performance]\n...\n\n" + lines.slice(-800).join('\n');
    }

    if (window.DOMPurify && typeof DOMPurify.sanitize === 'function') {
        codeEl.innerHTML = DOMPurify.sanitize(displayContent, {
            ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'code', 'pre', 'span', 'br'],
            ALLOWED_ATTR: ['class']
        });
    } else {
        codeEl.textContent = displayContent;
        console.warn('[Gabriel] DOMPurify 未加载，已降级为纯文本渲染');
    }
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
        // Round 62: Offline Recovery
        document.getElementById('wsStatus').classList.remove('disconnected');
        document.getElementById('wsStatus').classList.add('connected');
        document.getElementById('wsStatus').innerText = 'System Online';
        const chatInput = document.getElementById('chatInput');
        if (chatInput) chatInput.disabled = false;
        
        // Round 64: Jitter tolerance
        reconnectAttempts = 0;
        
        // Round 65: State Recovery
        ws.send(JSON.stringify({ type: "request_full_sync" }));
        
        // Round 63: Keepalive Ping (30s)
        if (window.pingInterval) clearInterval(window.pingInterval);
        window.pingInterval = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: "ping" }));
            }
        }, 30000);
    };
    
    ws.onclose = (e) => {
        if (window.pingInterval) clearInterval(window.pingInterval);
        
        const wsStatus = document.getElementById('wsStatus');
        wsStatus.classList.remove('connected');
        wsStatus.classList.add('disconnected');
        
        const chatInput = document.getElementById('chatInput');
        if (chatInput) chatInput.disabled = true;
        
        const delay = Math.min(1000 * Math.pow(1.5, reconnectAttempts), MAX_RECONNECT_DELAY);
        
        // Round 61: UI Graceful Reconnect Notification
        let countdown = Math.ceil(delay / 1000);
        wsStatus.innerHTML = `Offline. Reconnecting in <span id="reconnectCountdown">${countdown}</span>s`;
        
        if (window.reconnectCountdownTimer) clearInterval(window.reconnectCountdownTimer);
        window.reconnectCountdownTimer = setInterval(() => {
            countdown--;
            const countEl = document.getElementById('reconnectCountdown');
            if (countEl) countEl.innerText = countdown > 0 ? countdown : 0;
            if (countdown <= 0) clearInterval(window.reconnectCountdownTimer);
        }, 1000);

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
            
            // Render logs into grid
            const grid = document.getElementById('contextGrid');
            if (grid && msg.path && msg.path !== "all") {
                // Remove the waiting placeholder if it exists
                const placeholder = document.getElementById('contextDisplay');
                if (placeholder && placeholder.parentElement) {
                    placeholder.parentElement.remove();
                }
                
                let agentId = 'agent_' + msg.path.replace(/[^a-zA-Z0-9]/g, '_');
                let displayCard = document.getElementById(agentId);
                
                if (!displayCard) {
                    displayCard = document.createElement('div');
                    displayCard.id = agentId;
                    displayCard.className = 'agent-terminal-card';
                    displayCard.style.cssText = 'background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; display: flex; flex-direction: column; height: 400px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.3); transition: all 0.3s;';
                    displayCard.innerHTML = `
                        <div style="background: rgba(0,0,0,0.4); padding: 6px 12px; border-bottom: 1px solid var(--panel-border); font-size: 0.8rem; font-weight: bold; color: var(--accent); display:flex; justify-content:space-between; align-items:center;">
                            <span>🖥️ ${msg.agent}</span>
                            <button onclick="exportAgentLog('${msg.agent}', '${agentId}')" style="background:none; border:1px solid rgba(255,255,255,0.1); color:#a1a1aa; border-radius:4px; padding:2px 6px; font-size:0.7rem; cursor:pointer;" onmouseover="this.style.color='#fff'; this.style.borderColor='#8b5cf6'" onmouseout="this.style.color='#a1a1aa'; this.style.borderColor='rgba(255,255,255,0.1)'">💾 Export MD</button>
                        </div>
                        <pre style="margin:0; padding:12px; height:calc(100% - 30px); overflow-y:auto; white-space:pre-wrap; word-wrap:break-word;"><code class="agent-display-code"></code></pre>
                    `;
                    grid.appendChild(displayCard);
                }
                
                const codeEl = displayCard.querySelector('.agent-display-code');
                const parent = codeEl.parentElement;
                const isAtBottom = parent.scrollHeight - parent.scrollTop - parent.clientHeight < 50;
                
                renderAgentContent(codeEl, msg.content);
                
                // Rounds 91-95: Auto-Scroll Lock with UI Feedback
                let headerStatus = displayCard.querySelector('.scroll-lock-status');
                if (!headerStatus) {
                    headerStatus = document.createElement('span');
                    headerStatus.className = 'scroll-lock-status';
                    headerStatus.style.cssText = 'color: var(--warning); font-size: 0.7rem; margin-left: auto; margin-right: 8px; display: none;';
                    headerStatus.innerText = '⏸ Scroll Locked';
                    displayCard.querySelector('div').insertBefore(headerStatus, displayCard.querySelector('button'));
                }

                if (isAtBottom) {
                    parent.scrollTop = parent.scrollHeight;
                    headerStatus.style.display = 'none';
                    parent.style.borderBottom = 'none';
                } else {
                    headerStatus.style.display = 'inline-block';
                    parent.style.borderBottom = '2px solid var(--warning)';
                }
            } else if (msg.path === "all") {
                // Handle initial loading sync
                const placeholder = document.getElementById('contextDisplay');
                if (placeholder) {
                    placeholder.innerHTML = "Connected. Waiting for agent updates...";
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
            
            // Round 42: UI topology update for touched files
            if (msg.touched_files && msg.touched_files.length > 0) {
                let agentId = 'agent_' + msg.path.replace(/[^a-zA-Z0-9]/g, '_');
                let displayCard = document.getElementById(agentId);
                if (displayCard) {
                    let headerSpan = displayCard.querySelector('div span');
                    if (headerSpan) {
                        let filesStr = msg.touched_files.map(f => f.split(/[\\/]/).pop()).join(', ');
                        headerSpan.innerHTML = `🖥️ ${msg.agent} <span style="color:#a1a1aa; font-size:0.7rem; margin-left:8px;">(Touches: ${filesStr})</span>`;
                    }
                }
            }
        } else if (msg.type === "agent_spawn") {
            // Round 46: Build Agent Radar footprint
            const radarList = document.getElementById('agentList');
            if (radarList) {
                let agentId = 'radar_' + msg.path.replace(/[^a-zA-Z0-9]/g, '_');
                if (!document.getElementById(agentId)) {
                    let el = document.createElement('div');
                    el.id = agentId;
                    el.className = 'agent-item';
                    el.innerHTML = `
                        <div class="status-indicator"></div>
                        <span style="flex:1;">${msg.agent}</span>
                        <span style="font-size:0.7rem; color:var(--success);">ACTIVE</span>
                    `;
                    radarList.appendChild(el);
                }
            }
        } else if (msg.type === "agent_frozen") {
            // Round 47: Freeze Agent Radar footprint
            let agentId = 'radar_' + msg.path.replace(/[^a-zA-Z0-9]/g, '_');
            let el = document.getElementById(agentId);
            if (el) {
                el.querySelector('.status-indicator').style.background = 'var(--text-secondary)';
                el.querySelector('.status-indicator').style.boxShadow = 'none';
                el.querySelector('span:last-child').innerText = 'FROZEN';
                el.querySelector('span:last-child').style.color = 'var(--text-secondary)';
            }
            // Remove from context grid
            let cardId = 'agent_' + msg.path.replace(/[^a-zA-Z0-9]/g, '_');
            let card = document.getElementById(cardId);
            if (card) card.remove();
        } else if (msg.type === "kb_recommendation" || msg.type === "kb_toast") {
            const toast = document.getElementById('kbToast');
            const toastContent = document.getElementById('kbToastContent');
            if (toast && toastContent) {
                const encodedText = encodeURIComponent(msg.content);
                const parsed = window.marked ? marked.parse(msg.content) : msg.content;
                const htmlContent = window.DOMPurify ? DOMPurify.sanitize(parsed) : parsed;
                toastContent.innerHTML = `
                    <div class="insight-card-header">
                        <span>⚡ Agent Instruction / Insight</span>
                        <div>
                            <button class="btn-insight-copy" style="border-color:#8b5cf6; color:#8b5cf6; background:rgba(139, 92, 246, 0.1); margin-right:4px;" onclick="ws.send(JSON.stringify({type: 'inject_insight', content: decodeURIComponent('${encodedText}')})); this.classList.add('success-pulse'); this.innerText='Injected!'; setTimeout(() => { this.classList.remove('success-pulse'); this.innerText='⚡ Inject'; }, 2000);">⚡ Add to KB</button>
                            <button class="btn-insight-copy" onclick="navigator.clipboard.writeText(decodeURIComponent('${encodedText}')); this.classList.add('success-pulse'); this.innerText='Copied!'; setTimeout(() => { this.classList.remove('success-pulse'); this.innerText='Copy'; }, 2000);">Copy</button>
                        </div>
                    </div>
                    <div class="insight-content">${htmlContent}</div>
                `;
                toast.classList.remove('hidden');
                
                // Round 32: Dynamic Toast Auto-hide logic (15s)
                if (window.kbToastTimeout) clearTimeout(window.kbToastTimeout);
                window.kbToastTimeout = setTimeout(() => {
                    toast.classList.add('hidden');
                }, 15000);
            }
        } else if (msg.type === "ai_response_start") {
            if (window.currentThinkingId) {
                const el = document.getElementById(window.currentThinkingId);
                if (el) el.remove();
                window.currentThinkingId = null;
            }
            currentAiMessageContent = "";
            currentAiMessageDiv = createMessageDiv('ai-message');
            document.getElementById('chatHistory').appendChild(currentAiMessageDiv);
        } else if (msg.type === "ai_response_chunk") {
            currentAiMessageContent += msg.content;
            if(window.marked) {
                const parsed = marked.parse(currentAiMessageContent);
                if (window.DOMPurify) {
                    currentAiMessageDiv.innerHTML = DOMPurify.sanitize(parsed);
                } else {
                    currentAiMessageDiv.textContent = parsed;
                }
            } else {
                currentAiMessageDiv.innerText = currentAiMessageContent;
            }
            // Round 11 (UX): Cinematic Scroll Smoothness & Auto-Scroll Lock
            const container = document.getElementById('chatHistory');
            // Allow 80px threshold for breathing room
            const isScrolledToBottom = container.scrollHeight - container.clientHeight <= container.scrollTop + 80;
            if (isScrolledToBottom) {
                // Use requestAnimationFrame to sync scrolling with display refresh rate, preventing jitter
                window.requestAnimationFrame(() => {
                    container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
                });
            }
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
        if (window.DOMPurify) {
            div.innerHTML = DOMPurify.sanitize(parsed);
        } else {
            div.textContent = parsed;
        }
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
        input.style.height = 'auto';
        
        // Add typing indicator
        window.currentThinkingId = 'thinking-' + Date.now();
        const thinkingDiv = document.createElement('div');
        thinkingDiv.id = window.currentThinkingId;
        thinkingDiv.className = 'message sys-message';
        thinkingDiv.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span> Gabriel is thinking...';
        document.getElementById('chatHistory').appendChild(thinkingDiv);
        document.getElementById('chatHistory').scrollTop = document.getElementById('chatHistory').scrollHeight;
    }
});
document.getElementById('chatInput').addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    if (this.scrollHeight > 150) {
        this.style.overflowY = 'auto';
    } else {
        this.style.overflowY = 'hidden';
    }
});

document.getElementById('chatInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('btnSend').click();
        const input = document.getElementById('chatInput');
        input.style.height = 'auto';
    }
});

document.getElementById('btnMerge').addEventListener('click', () => {
    if(ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({type: "merge_kb", content: ""}));
        appendMessage(dict[currentLang].gen_draft || "⏳ Generating solution draft...", "sys-message");
    }
});

const btnClearChat = document.getElementById('btnClearChat');
if(btnClearChat) {
    btnClearChat.addEventListener('click', () => {
        if(ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({type: "clear_history", content: ""}));
            const chatHistory = document.getElementById('chatHistory');
            chatHistory.innerHTML = `<div class="message sys-message" data-i18n="chat_welcome">${dict[currentLang]?.chat_welcome || "Gabriel launched. Terminal snapshot is actively tracked."}</div>`;
        }
    });
}

const btnExportChat = document.getElementById('btnExportChat');
if (btnExportChat) {
    btnExportChat.addEventListener('click', () => {
        const historyEl = document.getElementById('chatHistory');
        const messages = historyEl.querySelectorAll('.message');
        let md = "# Gabriel Side-Screen Chat Export\n\n";
        md += `*Exported on: ${new Date().toLocaleString()}*\n\n---\n\n`;
        
        messages.forEach(msg => {
            if (msg.classList.contains('sys-message') && msg.id && msg.id.startsWith('thinking-')) return;
            const isUser = msg.classList.contains('user-message');
            const isSys = msg.classList.contains('sys-message');
            const role = isUser ? "**User**" : (isSys ? "**System**" : "**Gabriel**");
            let text = isUser || isSys ? msg.innerText : msg.innerText; 
            md += `${role}:\n${text}\n\n`;
        });
        
        const blob = new Blob([md], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Gabriel_Export_${new Date().getTime()}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
}

document.getElementById('btnFeedback').addEventListener('click', () => {
    document.getElementById('feedbackModal').style.display = 'flex';
});
document.getElementById('btnPreviewFeedback').addEventListener('click', () => {
    const text = document.getElementById('feedbackText').value;
    if (!text) return;
    
    // Gather all agent contents for feedback
    let combinedCtx = "";
    document.querySelectorAll('.agent-display-code').forEach(el => {
        combinedCtx += "\n---\n" + el.innerText;
    });
    
    const contextPreview = combinedCtx.slice(-1500);
    const fullPreview = `Issue:\n${text}\n\nContext:\n${contextPreview}`;
    
    document.getElementById('feedbackPreviewText').value = fullPreview;
    document.getElementById('feedbackModal').style.display = 'none';
    document.getElementById('feedbackPreviewModal').style.display = 'flex';
});

document.getElementById('btnConfirmFeedback').addEventListener('click', async () => {
    const content = document.getElementById('feedbackPreviewText').value;
    if (!content) return;
    
    const parts = content.split("\n\nContext:\n");
    const issue = parts[0].replace(/^Issue:\n/, '');
    const context = parts.length > 1 ? parts[1] : '';

    try {
        await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Gabriel-Token': localToken },
            body: JSON.stringify({ issue: issue, context: context })
        });
        document.getElementById('feedbackPreviewModal').style.display = 'none';
        document.getElementById('feedbackText').value = '';
    } catch(e) {}
});

document.getElementById('btnForgetToken').addEventListener('click', () => {
    localStorage.removeItem('gabriel_token');
    sessionStorage.removeItem('gabriel_token');
    window.location.reload();
});

// Init
applyLang();
loadConfig();
connectWebSocket();

async function pollHealth() {
    if (!localToken) return;
    try {
        const res = await fetch('/api/health', { headers: { 'X-Gabriel-Token': localToken } });
        if (!res.ok) {
            document.getElementById('healthAlertBanner').style.display = 'block';
        } else {
            document.getElementById('healthAlertBanner').style.display = 'none';
        }
    } catch(e) {
        document.getElementById('healthAlertBanner').style.display = 'block';
    }
}

setInterval(pollHealth, 10000);
setTimeout(pollHealth, 2000);

// ==========================================
// Round 3 Optimization: Cyber-Dark Telemetry Visualizer
// ==========================================
let telemetryChart;
const chartData = {
    labels: Array(20).fill(''),
    datasets: [{
        label: 'Neural Activity (Load %)',
        data: Array(20).fill(5),
        borderColor: 'rgba(139, 92, 246, 0.8)', // Purple glowing line
        backgroundColor: (context) => {
            if (!context.chart.chartArea) return;
            const ctx = context.chart.ctx;
            const gradient = ctx.createLinearGradient(0, 0, 0, context.chart.chartArea.bottom);
            gradient.addColorStop(0, 'rgba(139, 92, 246, 0.4)');
            gradient.addColorStop(1, 'rgba(139, 92, 246, 0.0)');
            return gradient;
        },
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointRadius: 0
    }]
};

function initChart() {
    const ctx = document.getElementById('telemetryChart');
    if (!ctx) return;
    
    // Add glow effect via plugin
    Chart.register({
        id: 'glow',
        beforeDraw: (chart) => {
            if (chart.ctx) {
                chart.ctx.save();
                chart.ctx.shadowColor = 'rgba(139, 92, 246, 0.8)';
                chart.ctx.shadowBlur = 10;
                chart.ctx.shadowOffsetX = 0;
                chart.ctx.shadowOffsetY = 4;
            }
        },
        afterDraw: (chart) => {
            if (chart.ctx) chart.ctx.restore();
        }
    });

    telemetryChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 300, easing: 'easeOutQuart' },
            plugins: { legend: { display: false } },
            scales: {
                y: { min: 0, max: 100, display: false },
                x: { display: false }
            },
            interaction: { intersect: false, mode: 'index' }
        }
    });

    // Idle cooldown loop
    setInterval(() => {
        const lastVal = chartData.datasets[0].data[19];
        // Jitter the cooldown to look alive
        const newVal = Math.max(5, lastVal - (lastVal * (0.05 + Math.random() * 0.1)));
        chartData.datasets[0].data.shift();
        chartData.datasets[0].data.push(newVal);
        telemetryChart.update('none');
    }, 1000);
}

// Call initChart immediately
initChart();

// ==========================================
// Round 13 Optimization: Reveal-on-Hover Copy Button for Code Blocks
// ==========================================
const codeObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.addedNodes.length) {
            document.querySelectorAll('.chat-history pre').forEach((preBlock) => {
                // If it already has a copy button, skip
                if (preBlock.querySelector('.btn-code-copy')) return;
                
                // Also apply hljs if available
                const codeBlock = preBlock.querySelector('code');
                if (codeBlock && window.hljs && !codeBlock.classList.contains('hljs')) {
                    hljs.highlightElement(codeBlock);
                }

                // Create floating copy button
                const copyBtn = document.createElement('button');
                copyBtn.className = 'btn-code-copy';
                copyBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
                
                copyBtn.addEventListener('click', () => {
                    const text = codeBlock ? codeBlock.innerText : preBlock.innerText;
                    navigator.clipboard.writeText(text);
                    
                    // Trigger success animation
                    copyBtn.classList.add('success-pulse');
                    copyBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>';
                    
                    setTimeout(() => {
                        copyBtn.classList.remove('success-pulse');
                        copyBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
                    }, 2000);
                });
                
                preBlock.appendChild(copyBtn);
            });
        }
    });
});
codeObserver.observe(document.getElementById('chatHistory'), { childList: true, subtree: true });

// ==========================================
// Round 38 Optimization: Knowledge Graph Fetch Logic
// ==========================================
async function fetchKbRules() {
    const listEl = document.getElementById('kbRulesList');
    if (!listEl) return;
    try {
        listEl.innerHTML = '<div style="color:var(--text-secondary); font-size:0.9rem; text-align:center; margin-top:20px;">Fetching...</div>';
        const res = await fetch('/api/knowledge');
        const json = await res.json();
        
        if (json.status !== "success" || !json.data || json.data.length === 0) {
            listEl.innerHTML = '<div style="color:var(--text-secondary); font-size:0.9rem; text-align:center; margin-top:20px;">No insights found yet.</div>';
            return;
        }
        
        listEl.innerHTML = '';
        json.data.forEach(rule => {
            const date = new Date(rule.timestamp * 1000).toLocaleString();
            const div = document.createElement('div');
            div.className = 'kb-rule-card';
            
            // Format content: truncate if too long
            const displayContent = rule.content.length > 150 ? rule.content.substring(0, 150) + '...' : rule.content;
            const parsed = window.DOMPurify && window.marked ? DOMPurify.sanitize(marked.parse(displayContent)) : displayContent;
            
            div.innerHTML = `
                <span class="kb-rule-date">🕒 ${date}</span>
                <div style="font-family:var(--font-ui);">${parsed}</div>
            `;
            
            // Clicking a rule populates the editor
            div.addEventListener('click', () => {
                const editor = document.getElementById('kbEditor');
                if (editor) {
                    editor.value = rule.content;
                    editor.dispatchEvent(new Event('input'));
                }
            });
            
            listEl.appendChild(div);
        });
    } catch (e) {
        listEl.innerHTML = `<div style="color:var(--error); font-size:0.9rem; text-align:center; margin-top:20px;">Error loading KB: ${e.message}</div>`;
    }
}

const btnRefreshKb = document.getElementById('btnRefreshKb');
if (btnRefreshKb) {
    btnRefreshKb.addEventListener('click', fetchKbRules);
}

// Fetch on startup if tab is clicked
document.querySelectorAll('.nav-item').forEach(el => {
    el.addEventListener('click', (e) => {
        if (el.getAttribute('data-tab') === 'tab-kb') {
            fetchKbRules();
        }
    });
});

// ==========================================
// Rounds 81-85: Power-User Ergonomics
// ==========================================
document.addEventListener('keydown', (e) => {
    // Cmd+K or Ctrl+K to focus AI chat
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        const chatInput = document.getElementById('chatInput');
        if (chatInput) chatInput.focus();
    }
    
    // Cmd+/ or Ctrl+/ to switch to Knowledge Base Tab
    if ((e.metaKey || e.ctrlKey) && e.key === '/') {
        e.preventDefault();
        const kbTab = document.querySelector('.nav-item[data-tab="tab-kb"]');
        if (kbTab) kbTab.click();
    }
    
    // Escape to unfocus
    if (e.key === 'Escape') {
        if (document.activeElement === document.getElementById('chatInput')) {
            document.activeElement.blur();
        }
    }
});

// ==========================================
// Rounds 86-90: Markdown Export Engine
// ==========================================
window.exportAgentLog = function(agentName, cardId) {
    const card = document.getElementById(cardId);
    if (!card) return;
    
    const codeEl = card.querySelector('.agent-display-code');
    if (!codeEl) return;
    
    const rawText = codeEl.textContent || "";
    const blob = new Blob([`# Gabriel AI Telemetry Log\nAgent: ${agentName}\nExported: ${new Date().toISOString()}\n\n---\n\n${rawText}`], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `gabriel_${agentName}_log_${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};

document.getElementById('btnAskKb').addEventListener('click', () => {
    const kbContent = document.getElementById('kbToastContent').innerText;
    const chatInput = document.getElementById('chatInput');
    chatInput.value = "Regarding this knowledge base recommendation:\n" + kbContent + "\n\nCan you explain how to apply this to the current issue?";
    chatInput.style.height = 'auto';
    chatInput.style.height = (chatInput.scrollHeight) + 'px';
    chatInput.focus();
    document.getElementById('kbToast').classList.add('hidden');
});
