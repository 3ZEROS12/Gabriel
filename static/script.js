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
        "chat_mode_title": "Side-brain Mode", "mode_light": "💨 Quick (Snapshot + Save)", "mode_private": "🔒 Private (Snapshot, no save)", "mode_audit": "🔬 Deep Audit (Full + Save)", "mode_onedive": "⚡ One-shot Deep (Full, no save)",
        "settings_ui": "UI Preferences", "settings_lang": "Language", "lang_en": "English", "lang_zh": "中文 (Chinese)",
        "copied": "Copied to Clipboard!", "saved": "Saved", "scanning": "Scanning...","radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 4.0.0 (Light Indigo)", "about_created": "Created by", "about_subtitle": "\"The Missing Visual Sidecar for Autonomous Agents\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel",
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
        "chat_mode_title": "副脑模式", "mode_light": "💨 轻量助手（快照+保存）", "mode_private": "🔒 私密问答（快照+不保存）", "mode_audit": "🔬 深潜审计（完整上下文+保存）", "mode_onedive": "⚡ 一次性深潜（完整+不保存）",
        "settings_ui": "界面偏好", "settings_lang": "显示语言",
        "copied": "已复制到剪贴板！", "saved": "已保存", "scanning": "正在扫描...", "radar_target": "目标 Agent", "radar_scanning": "正在扫描 Agent...", "settings_about": "关于 Gabriel", "radar_empty": "未发现活跃 Agent", "radar_no_agents_hint": "在终端启动 Agent 后会显示在这里", "agent_last_active": "最后活跃:", "agent_volume": "体量:", "agent_steps": "步", "btn_lock": "锁定", "err_fetching_agents": "获取 Agent 列表失败。", "btn_edit": "✏️ 编辑", "btn_preview": "👁 预览", "status_connected": "已连接", "status_disconnected": "已断开", "gen_draft": "⏳ 正在生成解决方案草稿...", "saving": "保存中...", "title_minimize": "最小化", "title_close": "关闭", "title_control_center": "控制中心", "title_agent_radar": "Agent 雷达", "title_knowledge_base": "知识库", "title_settings": "设置", "btn_preview_kb": "👁 预览", "about_version": "版本 4.0.0（Light Indigo）", "about_created": "作者", "about_subtitle": "\"自主智能体缺失的视觉副驾\"", "auto_track": "自动追踪最新", "status_wait": "等待中...", "gabriel_logo": "👼 Gabriel", "lang_en": "English", "lang_zh": "中文 (Chinese)", "chat_feedback": "反馈", "kb_recommendation": "知识库推荐",
        
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
        "chat_mode_title": "サイドブレインモード", "mode_light": "💨 クイック（スナップショット+保存）", "mode_private": "🔒 プライベート（スナップショット、保存なし）", "mode_audit": "🔬 ディープ監査（全文脈+保存）", "mode_onedive": "⚡ ワンショット（全文脈、保存なし）",
        "settings_ui": "UI 設定", "settings_lang": "表示言語",
        "copied": "コピーしました！", "saved": "保存しました", "scanning": "スキャン中...", "radar_target": "対象エージェント", "radar_scanning": "エージェントをスキャン中...", "settings_about": "Gabriel について", "radar_empty": "アクティブなエージェントなし", "radar_no_agents_hint": "ターミナルでエージェントを起動するとここに表示されます", "agent_last_active": "最終アクティブ:", "agent_volume": "ボリューム:", "agent_steps": "ステップ", "btn_lock": "ロック", "err_fetching_agents": "エージェントの取得に失敗", "btn_edit": "✏️ 編集", "btn_preview": "👁 プレビュー", "status_connected": "接続済み", "status_disconnected": "切断済み", "gen_draft": "⏳ ソリューション草案を生成中...", "saving": "保存中...", "title_minimize": "最小化", "title_close": "閉じる", "title_control_center": "コントロールセンター", "title_agent_radar": "エージェントレーダー", "title_knowledge_base": "ナレッジベース", "title_settings": "設定", "btn_preview_kb": "👁 プレビュー", "about_version": "バージョン 4.0.0（Light Indigo）", "about_created": "作成者", "about_subtitle": "\"自律エージェントに欠けたビジュアルサイドカー\"", "auto_track": "最新を自動追跡", "status_wait": "待機中...", "gabriel_logo": "👼 Gabriel", "lang_en": "English", "lang_zh": "中文 (Chinese)", "chat_feedback": "フィードバック", "kb_recommendation": "ナレッジベースのおすすめ",
        
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
        "chat_mode_title": "副腦模式", "mode_light": "💨 輕量助手（快照+保存）", "mode_private": "🔒 私密問答（快照+不保存）", "mode_audit": "🔬 深潛審計（完整上下文+保存）", "mode_onedive": "⚡ 一次性深潛（完整+不保存）",
        "settings_ui": "介面偏好", "settings_lang": "顯示語言",
        "copied": "已複製到剪貼簿！", "saved": "已保存", "scanning": "正在掃描...", "radar_target": "目標 Agent", "radar_scanning": "正在掃描 Agent...", "settings_about": "關於 Gabriel", "radar_empty": "未發現活躍 Agent", "radar_no_agents_hint": "在終端啟動 Agent 後會顯示在這裡", "agent_last_active": "最後活躍:", "agent_volume": "體量:", "agent_steps": "步", "btn_lock": "鎖定", "err_fetching_agents": "獲取 Agent 列表失敗。", "btn_edit": "✏️ 編輯", "btn_preview": "👁 預覽", "status_connected": "已連線", "status_disconnected": "已斷線", "gen_draft": "⏳ 正在生成解決方案草稿...", "saving": "儲存中...", "title_minimize": "最小化", "title_close": "關閉", "title_control_center": "控制中心", "title_agent_radar": "Agent 雷達", "title_knowledge_base": "知識庫", "title_settings": "設定", "btn_preview_kb": "👁 預覽", "about_version": "版本 4.0.0（Light Indigo）", "about_created": "作者", "about_subtitle": "\"自主智能體缺失的視覺副駕\"", "auto_track": "自動追蹤最新", "status_wait": "等待中...", "gabriel_logo": "👼 Gabriel", "lang_en": "English", "lang_zh": "中文 (Chinese)", "chat_feedback": "回饋", "kb_recommendation": "知識庫推薦",
        
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
        "chat_mode_title": "Mode second cerveau", "mode_light": "💨 Rapide (Snapshot + Sauvegarde)", "mode_private": "🔒 Privé (Snapshot, sans sauvegarde)", "mode_audit": "🔬 Audit profond (Contexte complet + Sauvegarde)", "mode_onedive": "⚡ Plongée unique (Complet, sans sauvegarde)",
        "settings_ui": "Préférences UI", "settings_lang": "Langue",
        "copied": "Copié !", "saved": "Enregistré", "scanning": "Analyse...", "radar_target": "Agent cible", "radar_scanning": "Analyse des agents...", "settings_about": "À propos de Gabriel", "radar_empty": "Aucun agent actif", "radar_no_agents_hint": "Démarrez un agent dans votre terminal pour le voir ici", "agent_last_active": "Dernière activité :", "agent_volume": "Volume :", "agent_steps": "étapes", "btn_lock": "Verrouiller", "err_fetching_agents": "Erreur lors du chargement des agents.", "btn_edit": "✏️ Éditer", "btn_preview": "👁 Aperçu", "status_connected": "Connecté", "status_disconnected": "Déconnecté", "gen_draft": "⏳ Génération du brouillon...", "saving": "Enregistrement...", "title_minimize": "Réduire", "title_close": "Fermer", "title_control_center": "Centre de contrôle", "title_agent_radar": "Radar d'agents", "title_knowledge_base": "Base de connaissances", "title_settings": "Paramètres", "btn_preview_kb": "👁 Aperçu", "about_version": "Version 4.0.0 (Light Indigo)", "about_created": "Créé par", "about_subtitle": "\"Le sidecar visuel manquant pour les agents autonomes\"", "auto_track": "Suivi auto du plus récent", "status_wait": "Attente...", "gabriel_logo": "👼 Gabriel", "lang_en": "English", "lang_zh": "中文 (Chinese)", "chat_feedback": "Commentaires", "kb_recommendation": "Recommandation de la base",
        
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
        "chat_mode_title": "Modo cerebro auxiliar", "mode_light": "💨 Rápido (Snapshot + Guardar)", "mode_private": "🔒 Privado (Snapshot, sin guardar)", "mode_audit": "🔬 Auditoría profunda (Contexto completo + Guardar)", "mode_onedive": "⚡ Inmersión única (Completo, sin guardar)",
        "settings_ui": "Preferencias de IU", "settings_lang": "Idioma",
        "copied": "¡Copiado!", "saved": "Guardado", "scanning": "Escaneando...", "radar_target": "Agente objetivo", "radar_scanning": "Escaneando agentes...", "settings_about": "Acerca de Gabriel", "radar_empty": "Sin agentes activos", "radar_no_agents_hint": "Inicia un agente en tu terminal para verlo aquí", "agent_last_active": "Última actividad:", "agent_volume": "Volumen:", "agent_steps": "pasos", "btn_lock": "Bloquear", "err_fetching_agents": "Error al cargar agentes.", "btn_edit": "✏️ Editar", "btn_preview": "👁 Vista previa", "status_connected": "Conectado", "status_disconnected": "Desconectado", "gen_draft": "⏳ Generando borrador...", "saving": "Guardando...", "title_minimize": "Minimizar", "title_close": "Cerrar", "title_control_center": "Centro de control", "title_agent_radar": "Radar de agentes", "title_knowledge_base": "Base de conocimientos", "title_settings": "Ajustes", "btn_preview_kb": "👁 Vista previa", "about_version": "Versión 3.1.0 (Cyber-Dark)", "about_created": "Creado por", "about_subtitle": "\"El sidecar visual que faltaba para agentes autónomos\"", "auto_track": "Seguir el más reciente", "status_wait": "Esperando...", "gabriel_logo": "👼 Gabriel", "lang_en": "English", "lang_zh": "中文 (Chinese)", "chat_feedback": "Comentarios", "kb_recommendation": "Recomendación de la base",
        
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
        "chat_mode_title": "보조 뇌 모드", "mode_light": "💨 빠른 (스냅샷+저장)", "mode_private": "🔒 비공개 (스냅샷, 저장 안 함)", "mode_audit": "🔬 딥 감사 (전체 컨텍스트+저장)", "mode_onedive": "⚡ 원샷 딥 (전체, 저장 안 함)",
        "settings_ui": "UI 환경설정", "settings_lang": "언어",
        "copied": "복사 완료!", "saved": "저장됨", "scanning": "스캔 중...", "radar_target": "대상 에이전트", "radar_scanning": "에이전트 검색 중...", "settings_about": "Gabriel 정보", "radar_empty": "활성 에이전트 없음", "radar_no_agents_hint": "터미널에서 에이전트를 시작하면 여기에 표시됩니다", "agent_last_active": "최근 활동:", "agent_volume": "볼륨:", "agent_steps": "단계", "btn_lock": "잠금", "err_fetching_agents": "에이전트를 불러오는 중 오류", "btn_edit": "✏️ 편집", "btn_preview": "👁 미리보기", "status_connected": "연결됨", "status_disconnected": "연결 끊김", "gen_draft": "⏳ 솔루션 초안 생성 중...", "saving": "저장 중...", "title_minimize": "최소화", "title_close": "닫기", "title_control_center": "컨트롤 센터", "title_agent_radar": "에이전트 레이더", "title_knowledge_base": "지식 베이스", "title_settings": "설정", "btn_preview_kb": "👁 미리보기", "about_version": "버전 4.0.0 (Light Indigo)", "about_created": "만든 사람", "about_subtitle": "\"자율 에이전트를 위한 시각 사이드카\"", "auto_track": "최신 자동 추적", "status_wait": "대기 중...", "gabriel_logo": "👼 Gabriel", "lang_en": "English", "lang_zh": "中文 (Chinese)", "chat_feedback": "피드백", "kb_recommendation": "지식 베이스 추천"
    }
};

let currentLang = localStorage.getItem('gabriel_lang') || "en";

if (window.marked && window.hljs) {
    const renderer = new marked.Renderer();
    renderer.code = function(code, language) {
        const validLang = hljs.getLanguage(language) ? language : 'plaintext';
        const highlighted = hljs.highlight(code, { language: validLang }).value;
        const encodedCode = encodeURIComponent(code);
        return `<div class="code-block-wrapper">
            <button class="code-copy-btn" onclick="navigator.clipboard.writeText(decodeURIComponent('${encodedCode}')); this.innerText='Copied!'; setTimeout(() => this.innerText='Copy', 2000);">Copy</button>
            <pre><code class="hljs ${validLang}">${highlighted}</code></pre>
        </div>`;
    };
    marked.setOptions({ renderer });
}

// [NOTE]: Using localStorage for token is acceptable for this local single-machine tool. 
// If Gabriel supports multi-user LAN access in the future, this must be re-evaluated.
const urlParams = new URLSearchParams(window.location.search);
let localToken = urlParams.get('token') || sessionStorage.getItem('gabriel_token') || localStorage.getItem('gabriel_token');
if (localToken) {
    sessionStorage.setItem('gabriel_token', localToken);
    localStorage.setItem('gabriel_token', localToken);
    window.history.replaceState({}, document.title, window.location.pathname);
} else {
    const loginModal = document.getElementById('loginModal');
    if (loginModal) loginModal.style.display = 'flex';
}

const btnLogin = document.getElementById('btnLogin');
if (btnLogin) {
    btnLogin.addEventListener('click', () => {
        const inputToken = document.getElementById('inputToken');
        const t = inputToken ? inputToken.value.trim() : "";
        if (t) {
            sessionStorage.setItem('gabriel_token', t);
            localStorage.setItem('gabriel_token', t);
            window.location.reload();
        }
    });
}

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
        
        if(item.dataset.tab === 'tab-radar') fetchAgents();
        if(item.dataset.tab === 'tab-kb') loadKb();
    });
});

// URL ?tab= 深链支持（截图验收/书签用）— 读顶部缓存的 urlParams（replaceState 已清 search）
(function() {
    const wanted = urlParams.get('tab');
    if (wanted && document.querySelector('.nav-item[data-tab="tab-' + wanted + '"]')) {
        document.querySelector('.nav-item[data-tab="tab-' + wanted + '"]').click();
    }
})();

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
const cfgPriceInput = document.getElementById('cfgPriceInput');
const cfgPriceOutput = document.getElementById('cfgPriceOutput');
let currentTargetAgent = "auto";

async function loadConfig() {
    try {
        const res = await fetch('/api/config', {
            headers: { 'X-Gabriel-Token': localToken }
        });
        const data = await res.json();
        if(data.base_url) cfgBaseUrl.value = data.base_url;
        if(data.api_key) cfgApiKey.value = data.api_key;
        if(data.model) cfgModel.value = data.model;
        if(cfgPriceInput) cfgPriceInput.value = data.price_input_per_m ?? 1.0;
        if(cfgPriceOutput) cfgPriceOutput.value = data.price_output_per_m ?? 3.0;
        currentTargetAgent = data.target_agent || "auto";
        const toggleEl = document.getElementById('toggleAutoCursor');
        if (toggleEl) toggleEl.checked = (currentTargetAgent === "auto");
        syncPricePreset();
    } catch(e) { console.error("Config load error", e); }
}

// Price presets fill the input/output price fields; manual edits reset to "Custom".
const PRICE_PRESETS = {
    gpt4o:   { input: 2.50,  output: 10.00 },
    deepseek:{ input: 0.50,  output: 1.50 },
    claude:  { input: 3.00,  output: 15.00 },
    gemini:  { input: 1.25,  output: 5.00 }
};
const pricePresetEl = document.getElementById('pricePreset');
function syncPricePreset() {
    if (!pricePresetEl) return;
    const inVal = parseFloat(cfgPriceInput ? cfgPriceInput.value : 0) || 0;
    const outVal = parseFloat(cfgPriceOutput ? cfgPriceOutput.value : 0) || 0;
    for (const [key, p] of Object.entries(PRICE_PRESETS)) {
        if (Math.abs(p.input - inVal) < 0.005 && Math.abs(p.output - outVal) < 0.005) {
            pricePresetEl.value = key;
            return;
        }
    }
    pricePresetEl.value = 'custom';
}
if (pricePresetEl) {
    pricePresetEl.addEventListener('change', () => {
        const p = PRICE_PRESETS[pricePresetEl.value];
        if (!p) return;
        if (cfgPriceInput) cfgPriceInput.value = p.input;
        if (cfgPriceOutput) cfgPriceOutput.value = p.output;
    });
}
if (cfgPriceInput) cfgPriceInput.addEventListener('input', syncPricePreset);
if (cfgPriceOutput) cfgPriceOutput.addEventListener('input', syncPricePreset);

async function saveConfig() {
    const toggleEl = document.getElementById('toggleAutoCursor');
    const isAuto = toggleEl ? toggleEl.checked : false;
    if(isAuto) currentTargetAgent = "auto";
    
    const payload = {
        base_url: cfgBaseUrl.value,
        api_key: cfgApiKey.value,
        model: cfgModel.value,
        target_agent: currentTargetAgent,
        price_input_per_m: parseFloat(cfgPriceInput ? cfgPriceInput.value : 1.0) || 1.0,
        price_output_per_m: parseFloat(cfgPriceOutput ? cfgPriceOutput.value : 3.0) || 3.0
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
const toggleAutoCursorEl = document.getElementById('toggleAutoCursor');
if (toggleAutoCursorEl) {
    toggleAutoCursorEl.addEventListener('change', async (e) => {
        if(e.target.checked) {
            currentTargetAgent = "auto";
            await saveConfig();
            fetchAgents();
        }
    });
}

// Token 失效统一处理：清凭据并重新弹登录（供 fetch/WS 401 调用）
function handleAuthFailure() {
    sessionStorage.removeItem('gabriel_token');
    localStorage.removeItem('gabriel_token');
    localToken = null;
    const loginModal = document.getElementById('loginModal');
    if (loginModal) loginModal.style.display = 'flex';
}

async function fetchAgents() {
    const list = document.getElementById('agentList');
    list.innerHTML = `<div class="agent-item">${dict[currentLang].scanning}</div>`;
    try {
        const res = await fetch('/api/agents', {
            headers: { 'X-Gabriel-Token': localToken }
        });
        if (!res.ok) {
            if (res.status === 401) { handleAuthFailure(); return; }
            throw new Error('HTTP ' + res.status);
        }
        const agents = await res.json();
        {
            // Sorting Logic
            const sortSelect = document.getElementById('agentSortSelect');
            const sortMode = sortSelect ? sortSelect.value : 'mtime_desc';
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
                    <div class="agent-item radar-empty-card">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"></circle><path d="M12 8v4m0 4h.01"></path></svg>
                        <div class="agent-name" data-i18n="radar_empty">No Active Agents Found</div>
                        <div class="radar-empty-hint" data-i18n="radar_no_agents_hint">Start an agent in your terminal to see it here</div>
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
                        <span class="agent-name">${a.name} ${isLocked ? ICONS.lock : ''}</span>
                        <span class="agent-time">${ICONS.clock} ${dict[currentLang].agent_last_active || "Last Active:"} ${date} &nbsp;|&nbsp; ${ICONS.activity} ${dict[currentLang].agent_volume || "Volume:"} ${a.steps || 0} ${dict[currentLang].agent_steps || "steps"}</span>
                    </div>
                    ${!isLocked ? `<button class="btn-outline btn-outline-sm" onclick="lockAgent('${a.path.replace(/\\/g, '\\\\')}')">${dict[currentLang].btn_lock || 'Lock'}</button>` : ''}
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
        }
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

const agentSortSelect = document.getElementById('agentSortSelect');
if (agentSortSelect) agentSortSelect.addEventListener('change', fetchAgents);
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
            ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'code', 'pre', 'span', 'br', 'div'],
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

async function connectWebSocket() {
    if (!localToken) return;
    let ticket = null;
    try {
        const ticketRes = await fetch('/api/auth/ticket', {
            method: 'POST',
            headers: { 'X-Gabriel-Token': localToken }
        });
        if (ticketRes.ok) {
            const data = await ticketRes.json();
            ticket = data.ticket;
        }
    } catch (e) {
        console.warn("Could not fetch WS auth ticket, falling back to token parameter.");
    }
    
    const host = window.location.host || '127.0.0.1:8080';
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = ticket ? `${wsProtocol}//${host}/ws?ticket=${ticket}` : `${wsProtocol}//${host}/ws?token=${localToken}`;
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

        // 1008 = token 被拒：停止重连，引导重新登录（网络断线仍走正常重连）
        if (e.code === 1008) {
            handleAuthFailure();
            const wsStatusEl = document.getElementById('wsStatus');
            if (wsStatusEl) wsStatusEl.innerHTML = 'Offline. Auth required.';
            return;
        }

        const wsStatus = document.getElementById('wsStatus');
        if (wsStatus) {
            wsStatus.classList.remove('connected');
            wsStatus.classList.add('disconnected');
        }
        
        const statusTextEl = document.getElementById('statusText');
        if (statusTextEl) statusTextEl.innerText = dict[currentLang].status_disconnected || "Disconnected";
        const statusDot = document.querySelector('.status-dot');
        if (statusDot) statusDot.classList.add('disconnected');
        
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
        if (msg.type === "context_update" || msg.type === "context_append") {
            
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
                    displayCard.style.cssText = 'height: 400px;';
                    displayCard.innerHTML = `
                        <div class="agent-card-header">
                            <div class="card-title-row">
                                <span class="agent-title-text">${msg.agent}</span>
                                <button class="card-export-btn" onclick="exportAgentLog('${msg.agent}', '${agentId}')">Export MD</button>
                            </div>
                        </div>
                        <pre class="agent-display-pane"><code class="agent-display-code"></code></pre>
                    `;
                    grid.appendChild(displayCard);
                }
                
                const codeEl = displayCard.querySelector('.agent-display-code');
                const parent = codeEl.parentElement;
                const isAtBottom = parent.scrollHeight - parent.scrollTop - parent.clientHeight < 50;
                
                if (msg.type === "context_append") {
                    if (window.DOMPurify && typeof DOMPurify.sanitize === 'function') {
                        codeEl.insertAdjacentHTML('beforeend', DOMPurify.sanitize(msg.content, {
                            ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'code', 'pre', 'span', 'br', 'div'],
                            ALLOWED_ATTR: ['class']
                        }));
                    } else {
                        const temp = document.createElement('div');
                        temp.textContent = msg.content;
                        codeEl.insertAdjacentHTML('beforeend', temp.innerHTML);
                    }
                    if (codeEl.children.length > 800) {
                        for (let i = 0; i < codeEl.children.length - 800; i++) {
                            codeEl.removeChild(codeEl.firstChild);
                        }
                    }
                } else {
                    renderAgentContent(codeEl, msg.content);
                }
                
                // Update context gauge
                if (typeof msg.context_percent !== 'undefined') {
                    let header = displayCard.querySelector('.agent-card-header');
                    let gauge = header.querySelector('.context-gauge');
                    if (!gauge) {
                        gauge = document.createElement('div');
                        gauge.className = 'context-gauge';
                        gauge.innerHTML = '<div class="context-gauge-bar"></div>';
                        header.appendChild(gauge);
                    }
                    let bar = gauge.querySelector('.context-gauge-bar');
                    bar.style.width = Math.min(100, msg.context_percent) + '%';

                    let warningMsg = header.querySelector('.context-warning');
                    if (msg.context_percent > 85) {
                        bar.style.background = 'var(--error)';
                        if (!warningMsg) {
                            header.insertAdjacentHTML('beforeend', '<div class="context-warning">' + ICONS['triangle-alert'] + ' 上下文剩余量低，建议重开或 /compact</div>');
                        }
                    } else {
                        bar.style.background = msg.context_percent > 70 ? 'var(--warn)' : 'var(--indigo)';
                        if (warningMsg) warningMsg.remove();
                    }
                }
                
                // Rounds 91-95: Auto-Scroll Lock with UI Feedback
                let headerStatus = displayCard.querySelector('.scroll-lock-status');
                if (!headerStatus) {
                    headerStatus = document.createElement('span');
                    headerStatus.className = 'scroll-lock-status';
                    headerStatus.innerHTML = ICONS.pause + ' Scroll Locked';
                    displayCard.querySelector('div').insertBefore(headerStatus, displayCard.querySelector('button'));
                }

                if (isAtBottom) {
                    parent.scrollTop = parent.scrollHeight;
                    headerStatus.style.display = 'none';
                    parent.classList.remove('scroll-detached');
                } else {
                    headerStatus.style.display = 'inline-block';
                    parent.classList.add('scroll-detached');
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
                setTimeout(() => {
                    pulse.style.background = '';
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
                        headerSpan.innerHTML = `${msg.agent}<span class="card-title-sub">(Touches: ${filesStr})</span>`;
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
                        <span class="agent-item-main">${msg.agent}</span>
                        <span class="agent-active-badge">ACTIVE</span>
                    `;
                    radarList.appendChild(el);
                }
            }
        } else if (msg.type === "agent_waiting") {
            if ('Notification' in window) {
                if (Notification.permission === 'granted') {
                    try {
                        new Notification('Gabriel — Agent 需要你', {
                            body: `Agent ${msg.agent || ''} 正在等待你的输入`
                        });
                    } catch(e) {}
                } else if (Notification.permission === 'default') {
                    try {
                        Notification.requestPermission();
                    } catch(e) {}
                }
            }
            let cardId = 'agent_' + msg.path.replace(/[^a-zA-Z0-9]/g, '_');
            let card = document.getElementById(cardId);
            if (card && !card.classList.contains('waiting-state')) {
                card.classList.add('waiting-state');
                let header = card.querySelector('.agent-card-header');
                if (header && !header.querySelector('.waiting-banner')) {
                    header.insertAdjacentHTML('beforeend', '<div class="waiting-banner">' + ICONS['triangle-alert'] + ' 需要你处理</div>');
                }
            }
        } else if (msg.type === "agent_unblocked") {
            let cardId = 'agent_' + msg.path.replace(/[^a-zA-Z0-9]/g, '_');
            let card = document.getElementById(cardId);
            if (card && card.classList.contains('waiting-state')) {
                card.classList.remove('waiting-state');
                card.style.borderColor = 'var(--border-color)';
                card.style.boxShadow = 'none';
                let banner = card.querySelector('.waiting-banner');
                if (banner) banner.remove();
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
                const insightId = msg.insight_id || 0;
                let localToken = document.getElementById("inputToken") ? document.getElementById("inputToken").value : "";
                
                toastContent.innerHTML = `
                    <div class="insight-card-header">
                        <span>${ICONS.zap} Agent Instruction / Insight</span>
                        <div>
                            <button class="btn-insight-copy vote-useful" onclick="fetch('/api/kb/feedback', {method:'POST', headers:{'Content-Type': 'application/json', 'X-Gabriel-Token': '${localToken}'}, body: JSON.stringify({insight_id: ${insightId}, action: 'useful'})}); this.innerHTML=ICONS.check; this.disabled=true;" title="Useful (用过)">${ICONS['thumbs-up']}</button>
                            <button class="btn-insight-copy vote-useless" onclick="fetch('/api/kb/feedback', {method:'POST', headers:{'Content-Type': 'application/json', 'X-Gabriel-Token': '${localToken}'}, body: JSON.stringify({insight_id: ${insightId}, action: 'useless'})}); this.innerHTML=ICONS.check; this.disabled=true;" title="Useless (没用)">${ICONS['thumbs-down']}</button>
                            <button class="btn-insight-copy vote-fav" onclick="fetch('/api/kb/feedback', {method:'POST', headers:{'Content-Type': 'application/json', 'X-Gabriel-Token': '${localToken}'}, body: JSON.stringify({insight_id: ${insightId}, action: 'favorite'})}); this.innerHTML=ICONS.check; this.disabled=true;" title="Favorite (收藏)">${ICONS.star}</button>
                            <button class="btn-insight-copy vote-inject" onclick="ws.send(JSON.stringify({type: 'inject_insight', content: decodeURIComponent('${encodedText}')})); this.classList.add('success-pulse'); this.innerText='Injected!'; setTimeout(() => { this.classList.remove('success-pulse'); this.innerHTML=ICONS.zap+' Inject'; }, 2000);">${ICONS.zap} Add to KB</button>
                            <button class="btn-insight-copy" onclick="navigator.clipboard.writeText(decodeURIComponent('${encodedText}')); this.classList.add('success-pulse'); this.innerText='Copied!'; setTimeout(() => { this.classList.remove('success-pulse'); this.innerText='Copy'; }, 2000);">Copy</button>
                        </div>
                    </div>
                    <div class="insight-content"></div>
                `;
                if (window.DOMPurify) {
                    toastContent.querySelector('.insight-content').innerHTML = DOMPurify.sanitize(parsed);
                } else {
                    toastContent.querySelector('.insight-content').textContent = parsed;
                }
                toast.classList.remove('hidden');
                
                // Round 32: Dynamic Toast Auto-hide logic (15s)
                if (window.kbToastTimeout) clearTimeout(window.kbToastTimeout);
                window.kbToastTimeout = setTimeout(() => {
                    toast.classList.add('hidden');
                }, 15000);
            }
        } else if (msg.type === "error_warning") {
            const warningDiv = document.createElement('div');
            warningDiv.className = 'message sys-message warning-message';

            const errId = 'err_' + Math.random().toString(36).substr(2, 9);
            const promptContent = encodeURIComponent(`检测到连续异常，请诊断：\n\n\`\`\`\n${msg.content}\n\`\`\``);

            warningDiv.innerHTML = `
                <div class="err-head">
                    <strong>${ICONS['triangle-alert']} 疑似卡点预警 (${msg.agent || 'Agent'})</strong>
                    <div>
                        <button onclick="document.getElementById('${errId}').style.display = document.getElementById('${errId}').style.display === 'none' ? 'block' : 'none'" class="err-toggle-btn">详情</button>
                        <button onclick="ws.send(JSON.stringify({type: 'chat', content: decodeURIComponent('${promptContent}'), mode: getChatMode()}))" class="err-diagnose-btn">⚡ 一键诊断</button>
                    </div>
                </div>
                <div id="${errId}" class="err-detail"></div>
            `;
            const contentDiv = warningDiv.querySelector('#' + errId);
            if (window.DOMPurify) contentDiv.innerHTML = DOMPurify.sanitize(msg.content);
            else contentDiv.textContent = msg.content;
            
            document.getElementById('chatHistory').appendChild(warningDiv);
            scrollToBottom();
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

// Per-message side-brain mode: controls context injection + persistence.
function getChatMode() {
    const el = document.getElementById('chatMode');
    const v = el ? el.value : 'light';
    switch (v) {
        case 'light':   return { context: 'snapshot', save: true };
        case 'private': return { context: 'snapshot', save: false };
        case 'audit':   return { context: 'full', save: true };
        case 'onedive': return { context: 'full', save: false };
        default:        return { context: 'snapshot', save: true };
    }
}

// Restore + persist the selected side-brain mode across reloads.
(function initChatMode() {
    const sel = document.getElementById('chatMode');
    if (!sel) return;
    const saved = localStorage.getItem('gabriel_chat_mode');
    if (saved && sel.querySelector(`option[value="${saved}"]`)) sel.value = saved;
    sel.addEventListener('change', () => localStorage.setItem('gabriel_chat_mode', sel.value));
})();

document.getElementById('btnSend').addEventListener('click', () => {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;
    
    if (text === '/help' || text === '/h') {
        const helpModal = document.getElementById('helpModal');
        if (helpModal) helpModal.style.display = 'flex';
        input.value = '';
        input.style.height = 'auto';
        return;
    }
    if (text === '/clear') {
        const btnClear = document.getElementById('btnClearChat');
        if (btnClear) btnClear.click();
        input.value = '';
        input.style.height = 'auto';
        return;
    }

    if (ws && ws.readyState === WebSocket.OPEN) {
        appendMessage(text, 'user-message');
        ws.send(JSON.stringify({type: "chat", content: text, mode: getChatMode()}));
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
            let text = msg.innerText; 
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

// (Dead code telemetryChart removed in T1)

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
let currentKbSubTab = 'all';

async function fetchKbRules() {
    const listEl = document.getElementById('kbRulesList');
    if (!listEl) return;
    
    try {
        listEl.innerHTML = '<div class="list-empty">Fetching...</div>';
        
        if (currentKbSubTab === 'fav') {
            const res = await fetch('/api/kb?filter=favorite', {
                headers: { 'X-Gabriel-Token': localToken }
            });
            const json = await res.json();
            const favs = json.favorites || [];
            
            if (favs.length === 0) {
                listEl.innerHTML = '<div class="list-empty">百宝箱为空，点击 ⭐ 可收藏常用 Insight。</div>';
                return;
            }

            listEl.innerHTML = '';
            favs.forEach(rule => {
                const div = document.createElement('div');
                div.className = 'kb-rule-card';

                const displayContent = rule.content.length > 150 ? rule.content.substring(0, 150) + '...' : rule.content;
                const parsed = window.DOMPurify && window.marked ? DOMPurify.sanitize(marked.parse(displayContent)) : displayContent;

                div.innerHTML = `
                    <div class="fav-item-head">
                        <span class="kb-rule-date">${ICONS.clock} ${rule.timestamp}</span>
                        <div class="btn-group">
                            <button class="btn-outline btn-unfav btn-danger-sm">取消收藏</button>
                        </div>
                    </div>
                    <div class="fav-content">${parsed}</div>
                `;
                
                const btnUnfav = div.querySelector('.btn-unfav');
                if (btnUnfav) {
                    btnUnfav.addEventListener('click', async (e) => {
                        e.stopPropagation();
                        await fetch('/api/kb/feedback', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json', 'X-Gabriel-Token': localToken },
                            body: JSON.stringify({ insight_id: rule.id, action: 'unfavorite' })
                        });
                        fetchKbRules();
                    });
                }
                
                div.addEventListener('click', () => {
                    const editor = document.getElementById('kbEditor');
                    if (editor) {
                        editor.value = rule.content;
                        editor.dispatchEvent(new Event('input'));
                    }
                });
                
                listEl.appendChild(div);
            });
            return;
        }
        
        const res = await fetch('/api/kb?filter=all', {
            headers: { 'X-Gabriel-Token': localToken }
        });
        const json = await res.json();
        const rules = json.items || json.rules || json.data || [];
        
        if (rules.length === 0) {
            listEl.innerHTML = '<div class="list-empty">No insights found yet.</div>';
            return;
        }

        listEl.innerHTML = '';
        rules.forEach(rule => {
            const date = rule.timestamp ? rule.timestamp : 'Just now';
            const div = document.createElement('div');
            div.className = 'kb-rule-card';

            // Format content: truncate if too long
            const displayContent = rule.content.length > 150 ? rule.content.substring(0, 150) + '...' : rule.content;
            const parsed = window.DOMPurify && window.marked ? DOMPurify.sanitize(marked.parse(displayContent)) : displayContent;

            let tagsHtml = '';
            if (rule.tags) {
                let parsedTags = [];
                try {
                    parsedTags = typeof rule.tags === 'string' ? JSON.parse(rule.tags) : rule.tags;
                } catch(e) {
                    if (typeof rule.tags === 'string') parsedTags = rule.tags.split(',');
                }
                if (Array.isArray(parsedTags) && parsedTags.length > 0) {
                    tagsHtml = '<div class="kb-tags-row">' +
                        parsedTags.map(t => {
                            const cleanT = String(t).trim().replace(/^#/, '');
                            const safeT = window.DOMPurify ? DOMPurify.sanitize(cleanT) : cleanT;
                            return `<span class="kb-tag-chip">#${safeT}</span>`;
                        }).join('') +
                        '</div>';
                }
            }

            div.innerHTML = `
                <span class="kb-rule-date">${ICONS.clock} ${date}</span>
                <div class="fav-content">${parsed}</div>
                ${tagsHtml}
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
        listEl.innerHTML = `<div class="list-error">Error loading KB: ${e.message}</div>`;
    }
}

const btnKbSubAll = document.getElementById('btnKbSubAll');
const btnKbSubFav = document.getElementById('btnKbSubFav');

if (btnKbSubAll && btnKbSubFav) {
    btnKbSubAll.addEventListener('click', () => {
        currentKbSubTab = 'all';
        btnKbSubAll.classList.add('active');
        btnKbSubFav.classList.remove('active');
        fetchKbRules();
    });
    btnKbSubFav.addEventListener('click', () => {
        currentKbSubTab = 'fav';
        btnKbSubFav.classList.add('active');
        btnKbSubAll.classList.remove('active');
        fetchKbRules();
    });
}

const btnRefreshKb = document.getElementById('btnRefreshKb');
if (btnRefreshKb) {
    btnRefreshKb.addEventListener('click', fetchKbRules);
}

// --- Session History Browser (Task T5) ---
let currentSessionReviewPath = null;

async function fetchSessionHistory() {
    const listEl = document.getElementById('sessionHistoryList');
    if (!listEl) return;
    try {
        listEl.innerHTML = '<div class="list-empty-pad">加载中...</div>';
        const res = await fetch('/api/sessions', {
            headers: { 'X-Gabriel-Token': localToken }
        });
        const sessions = await res.json();
        if (!sessions || sessions.length === 0) {
            listEl.innerHTML = '<div class="list-empty-pad">尚无历史会话记录。</div>';
            return;
        }
        listEl.innerHTML = '';
        sessions.forEach(sess => {
            const item = document.createElement('div');
            item.className = 'agent-item session-item';
            item.style.cursor = 'pointer';
            const existsBadge = sess.exists ? '<span class="exists-badge">(存在)</span>' : '<span class="gone-badge">(已删)</span>';
            const avgCost = (sess.turns && sess.turns > 0) ? (sess.est_cost / sess.turns).toFixed(4) : '--';
            item.innerHTML = `
                <div class="agent-info">
                    <span class="agent-name">${ICONS['file-text']} ${sess.agent} ${existsBadge}</span>
                    <span class="agent-path">${sess.path}</span>
                </div>
                <div class="session-meta-row">
                    <div>${ICONS.clock} ${sess.ts}</div>
                    <div class="session-meta-accent">Turns: ${sess.turns || '--'} | Cost: $${(sess.est_cost || 0).toFixed(4)} | Avg: $${avgCost}/turn</div>
                    <div class="session-meta-sub">⚡ ${fmtTokens(sess.input_tokens || 0)} in / ${fmtTokens(sess.output_tokens || 0)} out${(sess.cache_read_tokens || 0) ? ' | cache ' + fmtTokens(sess.cache_read_tokens) + 'r / ' + fmtTokens(sess.cache_creation_tokens || 0) + 'w' : ''}</div>
                </div>
            `;
            if (sess.exists) {
                item.addEventListener('click', () => openSessionReview(sess.id, sess.agent, sess.path));
            } else {
                item.classList.add('session-dead');
            }
            listEl.appendChild(item);
        });
    } catch (e) {
        listEl.innerHTML = `<div class="list-error-pad">加载历史失败: ${e.message}</div>`;
    }
}

let currentSessionReviewId = null;

async function openSessionReview(id, agent, path) {
    currentSessionReviewId = id;
    currentSessionReviewPath = path;
    const modal = document.getElementById('sessionReviewModal');
    const titleEl = document.getElementById('sessionReviewTitle');
    const bodyEl = document.getElementById('sessionReviewBody');
    if (!modal || !bodyEl) return;
    
    titleEl.innerHTML = `${ICONS['file-text']} 回看会话: ${agent}`;
    bodyEl.innerHTML = '<div class="list-empty-pad">加载日志文本中...</div>';
    modal.style.display = 'flex';

    try {
        const res = await fetch(`/api/sessions/${id}/transcript`, {
            headers: { 'X-Gabriel-Token': localToken }
        });
        const data = await res.json();
        if (data.status === 'success') {
            const sanitized = window.DOMPurify ? DOMPurify.sanitize(data.html) : data.html;
            bodyEl.innerHTML = sanitized;
        } else {
            bodyEl.innerHTML = `<div class="list-error-pad">${data.message || '无法获取会话内容'}</div>`;
        }
    } catch(e) {
        bodyEl.innerHTML = `<div class="list-error-pad">请求报错: ${e.message}</div>`;
    }
}

const btnRadarSubLive = document.getElementById('btnRadarSubLive');
const btnRadarSubHistory = document.getElementById('btnRadarSubHistory');
const btnRadarSubStuck = document.getElementById('btnRadarSubStuck');
if (btnRadarSubLive && btnRadarSubHistory && btnRadarSubStuck) {
    btnRadarSubLive.addEventListener('click', () => {
        btnRadarSubLive.classList.add('active');
        btnRadarSubHistory.classList.remove('active');
        btnRadarSubStuck.classList.remove('active');
        document.getElementById('radarSubViewLive').classList.remove('hidden');
        document.getElementById('radarSubViewHistory').classList.add('hidden');
        document.getElementById('radarSubViewStuck').classList.add('hidden');
    });
    btnRadarSubHistory.addEventListener('click', () => {
        btnRadarSubHistory.classList.add('active');
        btnRadarSubLive.classList.remove('active');
        btnRadarSubStuck.classList.remove('active');
        document.getElementById('radarSubViewLive').classList.add('hidden');
        document.getElementById('radarSubViewHistory').classList.remove('hidden');
        document.getElementById('radarSubViewStuck').classList.add('hidden');
        fetchSessionHistory();
    });
    btnRadarSubStuck.addEventListener('click', () => {
        btnRadarSubStuck.classList.add('active');
        btnRadarSubLive.classList.remove('active');
        btnRadarSubHistory.classList.remove('active');
        document.getElementById('radarSubViewLive').classList.add('hidden');
        document.getElementById('radarSubViewHistory').classList.add('hidden');
        document.getElementById('radarSubViewStuck').classList.remove('hidden');
        fetchStuckReports();
    });
}

async function fetchStuckReports() {
    const listEl = document.getElementById('stuckList');
    if (!listEl) return;
    try {
        const [resReports, resStats] = await Promise.all([
            fetch('/api/stuck?limit=50', { headers: { 'X-Gabriel-Token': localToken } }),
            fetch('/api/stuck/stats', { headers: { 'X-Gabriel-Token': localToken } })
        ]);
        const dataReports = await resReports.json();
        const dataStats = await resStats.json();

        if (dataStats.status === 'success') {
            document.getElementById('stuck24hCount').innerText = dataStats.total_24h || 0;
            document.getElementById('stuck7dCount').innerText = dataStats.total_7d || 0;
            const topAgent = Object.entries(dataStats.by_agent || {}).sort((a, b) => b[1] - a[1])[0];
            document.getElementById('stuckTopAgent').innerText = topAgent ? `${topAgent[0]} (${topAgent[1]})` : '--';
        }

        if (dataReports.status !== 'success' || !dataReports.reports || dataReports.reports.length === 0) {
            listEl.innerHTML = '<div class="list-empty-pad">暂无卡点报告</div>';
            return;
        }

        listEl.innerHTML = '';
        dataReports.reports.forEach(rpt => {
            const item = document.createElement('div');
            item.className = 'agent-item stuck-item';

            const header = document.createElement('div');
            header.className = 'stuck-head';

            const title = document.createElement('div');
            title.className = 'stuck-title';

            const badge = document.createElement('span');
            badge.className = 'stuck-agent-badge';
            badge.innerText = rpt.agent;

            const timeSpan = document.createElement('span');
            timeSpan.className = 'stuck-time';
            timeSpan.innerText = rpt.ts_human;

            title.appendChild(badge);
            title.appendChild(timeSpan);

            const searchBtn = document.createElement('button');
            searchBtn.className = 'btn-outline btn-outline-sm';
            searchBtn.innerHTML = ICONS.search + ' 检索历史方案';

            header.appendChild(title);
            header.appendChild(searchBtn);

            const ctxBox = document.createElement('div');
            ctxBox.className = 'stuck-context';
            ctxBox.innerText = rpt.context;

            const hitsContainer = document.createElement('div');
            hitsContainer.className = 'stuck-hits';

            searchBtn.addEventListener('click', async () => {
                searchBtn.innerHTML = ICONS['loader-circle'] + ' 检索中...';
                try {
                    const res = await fetch('/api/kb/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Gabriel-Token': localToken
                        },
                        body: JSON.stringify({ text: rpt.context })
                    });
                    const data = await res.json();
                    searchBtn.innerHTML = ICONS.search + ' 检索历史方案';
                    hitsContainer.style.display = 'flex';
                    hitsContainer.innerHTML = '';
                    if (data.hits && data.hits.length > 0) {
                        data.hits.forEach(hit => {
                            const hitCard = document.createElement('div');
                            hitCard.className = 'hit-card';

                            const textDiv = document.createElement('div');
                            textDiv.className = 'hit-text';
                            textDiv.innerText = hit.content;

                            const copyBtn = document.createElement('button');
                            copyBtn.className = 'btn-outline btn-outline-sm';
                            copyBtn.innerHTML = ICONS.copy + ' 复制';
                            copyBtn.addEventListener('click', () => {
                                navigator.clipboard.writeText(hit.content);
                                copyBtn.innerHTML = ICONS.check + ' 已复制';
                                setTimeout(() => copyBtn.innerHTML = ICONS.copy + ' 复制', 2000);
                            });

                            hitCard.appendChild(textDiv);
                            hitCard.appendChild(copyBtn);
                            hitsContainer.appendChild(hitCard);
                        });
                    } else {
                        hitsContainer.innerHTML = '<div class="hits-empty">未匹配到相关历史 KB 方案</div>';
                    }
                } catch(e) {
                    searchBtn.innerHTML = ICONS.search + ' 检索历史方案';
                    hitsContainer.style.display = 'flex';
                    hitsContainer.innerHTML = `<div class="hits-error">检索失败: ${e.message}</div>`;
                }
            });

            item.appendChild(header);
            item.appendChild(ctxBox);
            item.appendChild(hitsContainer);
            listEl.appendChild(item);
        });
    } catch(e) {
        listEl.innerHTML = `<div class="list-error-pad">加载卡点失败: ${e.message}</div>`;
    }
}

const btnCloseSessionReview = document.getElementById('btnCloseSessionReview');
if (btnCloseSessionReview) {
    btnCloseSessionReview.addEventListener('click', () => {
        document.getElementById('sessionReviewModal').style.display = 'none';
    });
}

const btnGenerateReport = document.getElementById('btnGenerateReport');
if (btnGenerateReport) {
    btnGenerateReport.addEventListener('click', async () => {
        if (!currentSessionReviewId) return;
        try {
            const res = await fetch(`/api/sessions/${currentSessionReviewId}/transcript?raw=1`, {
                headers: { 'X-Gabriel-Token': localToken }
            });
            const data = await res.json();
            if (data.status !== 'success') {
                alert("生成复盘报告失败: " + (data.message || "未知错误"));
                return;
            }

            const stats = data.stats || {};
            const touched = (data.touched_files || []).map(f => `- \`${f}\``).join('\n') || '- (无)';
            
            const rawLines = data.lines || [];
            const errLines = rawLines.filter(l => /(error|exception|timeout)/i.test(l)).slice(0, 10);
            const errBlock = errLines.length > 0
                ? errLines.map(l => l.trim()).join('\n')
                : "未检测到明显 Error/Exception 行。";

            const mdContent = [
                `# Gabriel AI Session Review Report (会话复盘报告)`,
                `**Agent**: ${data.agent || 'unknown'}`,
                `**Session ID**: #${data.id}`,
                `**Log Path**: \`${data.path}\``,
                `**Start Time**: ${data.ts}`,
                `**Generated At**: ${new Date().toLocaleString()}`,
                ``,
                `## 1. 会话统计与成本 (Telemetry & Cost)`,
                `- **Total Turns**: ${stats.turns || 0}`,
                `- **Total Characters**: ${stats.chars || 0}`,
                `- **Estimated Cost**: $${(stats.est_cost || 0).toFixed(6)}`,
                `- **Input Tokens**: ${stats.input_tokens || 0}`,
                `- **Output Tokens**: ${stats.output_tokens || 0}`,
                `- **Cache Read Tokens**: ${stats.cache_read_tokens || 0}`,
                `- **Cache Creation Tokens**: ${stats.cache_creation_tokens || 0}`,
                ``,
                `## 2. 触碰文件列表 (Touched Files)`,
                touched,
                ``,
                `## 3. 异常与错误摘要 (Error & Exception Summary)`,
                `\`\`\``,
                errBlock,
                `\`\`\``,
                ``,
                `---`,
                `*Report automatically generated by Gabriel AI Sidecar.*`
            ].join('\n');

            const blob = new Blob([mdContent], { type: 'text/markdown;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `gabriel_session_${currentSessionReviewId}_review_${Date.now()}.md`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (e) {
            alert("生成复盘报告出错: " + e.message);
        }
    });
}

const btnAdoptSession = document.getElementById('btnAdoptSession');
if (btnAdoptSession) {
    btnAdoptSession.addEventListener('click', () => {
        if (currentSessionReviewPath && ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'adopt_session', path: currentSessionReviewPath }));
            document.getElementById('sessionReviewModal').style.display = 'none';
            const chatNav = document.querySelector('.nav-item[data-tab="tab-chat"]');
            if (chatNav) chatNav.click();
        }
    });
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
const btnCloseHelpModal = document.getElementById('btnCloseHelpModal');
if (btnCloseHelpModal) {
    btnCloseHelpModal.addEventListener('click', () => {
        const helpModal = document.getElementById('helpModal');
        if (helpModal) helpModal.style.display = 'none';
    });
}

document.addEventListener('keydown', (e) => {
    // Cmd+K or Ctrl+K to focus AI chat
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
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

    // Number keys 1, 2, 3, 4 for tab switching when not in text input
    const isEditing = document.activeElement && ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName);
    if (!isEditing && !e.ctrlKey && !e.metaKey && !e.altKey) {
        if (e.key === '1') {
            const tab = document.querySelector('.nav-item[data-tab="tab-chat"]');
            if (tab) tab.click();
        } else if (e.key === '2') {
            const tab = document.querySelector('.nav-item[data-tab="tab-radar"]');
            if (tab) tab.click();
        } else if (e.key === '3') {
            const tab = document.querySelector('.nav-item[data-tab="tab-kb"]');
            if (tab) tab.click();
        } else if (e.key === '4') {
            const tab = document.querySelector('.nav-item[data-tab="tab-settings"]');
            if (tab) tab.click();
        }
    }
    
    // Escape to unfocus and close open modals
    if (e.key === 'Escape') {
        if (document.activeElement === document.getElementById('chatInput')) {
            document.activeElement.blur();
        }
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.style.display = 'none';
        });
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

// ==========================================
// C1 Stats Fetching
// ==========================================
function fmtTokens(n) {
    if (!n) return '0';
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'k';
    return String(n);
}

async function fetchStats() {
    try {
        const response = await fetch('/api/stats', {
            headers: { 'X-Gabriel-Token': localToken }
        });
        if (response.ok) {
            const stats = await response.json();
            const eTurns = document.getElementById('statTurns');
            const eErrs = document.getElementById('statErrors');
            const eTools = document.getElementById('statTools');
            const eCost = document.getElementById('statCost');
            const eTokens = document.getElementById('statTokens');
            if (eTurns) eTurns.innerText = stats.turns;
            if (eErrs) eErrs.innerText = stats.errors;
            if (eTools) eTools.innerText = stats.tools;
            if (eCost) eCost.innerText = '$' + stats.cost.toFixed(4);
            if (eTokens) eTokens.innerText = fmtTokens(stats.input_tokens) + ' / ' + fmtTokens(stats.output_tokens);
        }
    } catch (e) {}
}
setInterval(fetchStats, 5000);

// ==========================================
// C5 Onboarding & Ergonomics
// ==========================================
if (!localStorage.getItem('gb_has_run') && !urlParams.get('skip_onboard')) {
    const ob = document.getElementById('onboardingModal');
    if (ob) ob.style.display = 'flex';
}
const chatInputBox = document.getElementById('chatInput');
if (chatInputBox) {
    chatInputBox.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            document.getElementById('btnSend').click();
        }
    });
}

