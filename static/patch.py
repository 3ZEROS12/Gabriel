import re

with open('script.js', 'r', encoding='utf-8') as f:
    js = f.read()

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update js dict
keys_en = '"radar_target": "Target Agent", "radar_scanning": "Scanning for agents...", "settings_about": "About Gabriel", "radar_empty": "No Active Agents Found", "radar_no_agents_hint": "Start an agent in your terminal to see it here", "agent_last_active": "Last Active:", "agent_volume": "Volume:", "agent_steps": "steps", "btn_lock": "Lock", "err_fetching_agents": "Error fetching agents.", "btn_edit": "✏️ Edit", "btn_preview": "👁 Preview", "status_connected": "Connected", "status_disconnected": "Disconnected", "gen_draft": "⏳ Generating solution draft...", "saving": "Saving...", "title_minimize": "Minimize", "title_close": "Close", "title_control_center": "Control Center", "title_agent_radar": "Agent Radar", "title_knowledge_base": "Knowledge Base", "title_settings": "Settings", "btn_preview_kb": "👁 Preview", "about_version": "Version 3.1.0 (Cyber-Dark Edition)", "about_created": "Created by", "about_subtitle": "\\"The Missing Visual Sidecar for Autonomous Agents\\"", "auto_track": "Auto-track Newest", "status_wait": "Wait...", "gabriel_logo": "👼 Gabriel"'

keys_zh = '"radar_target": "目标代理", "radar_scanning": "正在扫描代理...", "settings_about": "关于 Gabriel", "radar_empty": "未找到活跃的代理", "radar_no_agents_hint": "在终端中启动代理以在此处查看", "agent_last_active": "最后活跃:", "agent_volume": "对话体量:", "agent_steps": "步", "btn_lock": "锁定", "err_fetching_agents": "获取代理错误。", "btn_edit": "✏️ 编辑", "btn_preview": "👁 预览", "status_connected": "已连接", "status_disconnected": "已断开", "gen_draft": "⏳ 正在生成知识草稿...", "saving": "保存中...", "title_minimize": "最小化", "title_close": "关闭", "title_control_center": "控制中心", "title_agent_radar": "代理雷达", "title_knowledge_base": "知识库", "title_settings": "设置", "btn_preview_kb": "👁 预览", "about_version": "版本 3.1.0 (赛博黑暗版)", "about_created": "创建者", "about_subtitle": "\\"自主代理缺失的视觉副车\\"", "auto_track": "自动追踪最新", "status_wait": "等待...", "gabriel_logo": "👼 Gabriel"'

# simplistic inject for all langs, we'll just fall back to EN if not EN/ZH
def add_keys(match):
    lang = match.group(1)
    if lang in ['zh', 'zh-TW']:
        add = keys_zh
    else:
        add = keys_en
    return match.group(0) + add + ",\n        "

js = re.sub(r'("[a-zA-Z-]+": {\n.*?)(?=\n    },)', add_keys, js, flags=re.DOTALL)

# Now fix the hardcoded strings in script.js
js = js.replace('btn.innerText = "Saving...";', 'btn.innerText = dict[currentLang].saving || "Saving...";')
js = js.replace('<div style="font-size:0.75rem; color:var(--text-secondary); margin-top:8px; text-align:center;">Start an agent in your terminal to see it here</div>', '<div style="font-size:0.75rem; color:var(--text-secondary); margin-top:8px; text-align:center;" data-i18n="radar_no_agents_hint">Start an agent in your terminal to see it here</div>')
js = js.replace('<span class="agent-time">⏱ Last Active: ${date} &nbsp;|&nbsp; 📊 Volume: ${a.steps || 0} steps</span>', '<span class="agent-time">⏱ ${dict[currentLang].agent_last_active || "Last Active:"} ${date} &nbsp;|&nbsp; 📊 ${dict[currentLang].agent_volume || "Volume:"} ${a.steps || 0} ${dict[currentLang].agent_steps || "steps"}</span>')
js = js.replace(">Lock</button>", ">${dict[currentLang].btn_lock || 'Lock'}</button>")
js = js.replace('<div class="agent-item">Error fetching agents.</div>', '<div class="agent-item">${dict[currentLang].err_fetching_agents || "Error fetching agents."}</div>')
js = js.replace("btnPreviewKb.innerText = '✏️ Edit';", "btnPreviewKb.innerText = dict[currentLang].btn_edit || '✏️ Edit';")
js = js.replace("btnPreviewKb.innerText = '👁 Preview';", "btnPreviewKb.innerText = dict[currentLang].btn_preview || '👁 Preview';")
js = js.replace('document.getElementById(\'statusText\').innerText = "Connected";', 'document.getElementById(\'statusText\').innerText = dict[currentLang].status_connected || "Connected";')
js = js.replace('document.getElementById(\'statusText\').innerText = "Disconnected";', 'document.getElementById(\'statusText\').innerText = dict[currentLang].status_disconnected || "Disconnected";')
js = js.replace('appendMessage(currentLang === \'en\' ? "⏳ Generating solution draft..." : "⏳ 正在生成知识草稿...", "sys-message");', 'appendMessage(dict[currentLang].gen_draft || "⏳ Generating solution draft...", "sys-message");')

applyLang_old = """    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        el.placeholder = map[el.getAttribute('data-i18n-placeholder')];
    });"""
applyLang_new = """    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        el.placeholder = map[el.getAttribute('data-i18n-placeholder')];
    });
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
        if(map[el.getAttribute('data-i18n-title')]) {
            el.title = map[el.getAttribute('data-i18n-title')];
        }
    });"""
js = js.replace(applyLang_old, applyLang_new)

with open('script.js', 'w', encoding='utf-8') as f:
    f.write(js)

# Update HTML
html = html.replace('👼 Gabriel', '<span data-i18n="gabriel_logo">👼 Gabriel</span>')

html = html.replace('title="Minimize"', 'data-i18n-title="title_minimize" title="Minimize"')
html = html.replace('title="Close"', 'data-i18n-title="title_close" title="Close"')
html = html.replace('title="Control Center"', 'data-i18n-title="title_control_center" title="Control Center"')
html = html.replace('title="Agent Radar"', 'data-i18n-title="title_agent_radar" title="Agent Radar"')
html = html.replace('title="Knowledge Base"', 'data-i18n-title="title_knowledge_base" title="Knowledge Base"')
html = html.replace('title="Settings"', 'data-i18n-title="title_settings" title="Settings"')

html = html.replace('>Wait...<', ' data-i18n="status_wait">Wait...<')
html = html.replace('>Auto-track Newest<', ' data-i18n="auto_track">Auto-track Newest<')
html = html.replace('👁 Preview</button>', '<span data-i18n="btn_preview_kb">👁 Preview</span></button>')

about_html_old = '''Version 3.1.0 (Cyber-Dark Edition)<br>
                                Created by <strong>Li Ming</strong> & Gabriel AI<br>
                                <em>"The Missing Visual Sidecar for Autonomous Agents"</em>'''
about_html_new = '''<span data-i18n="about_version">Version 3.1.0 (Cyber-Dark Edition)</span><br>
                                <span data-i18n="about_created">Created by</span> <strong>Li Ming</strong> & Gabriel AI<br>
                                <em data-i18n="about_subtitle">"The Missing Visual Sidecar for Autonomous Agents"</em>'''
html = html.replace(about_html_old, about_html_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Patched!")
