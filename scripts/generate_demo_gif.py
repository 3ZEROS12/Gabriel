import os
from PIL import Image, ImageDraw, ImageFont

def create_demo_gif(output_path="docs/demo.gif"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    width, height = 900, 500
    frames = []

    # Try loading default fonts
    try:
        font_main = ImageFont.truetype("arial.ttf", 13)
        font_bold = ImageFont.truetype("arialbd.ttf", 14)
        font_title = ImageFont.truetype("arialbd.ttf", 16)
        font_mono = ImageFont.truetype("consola.ttf", 12)
        font_mono_bold = ImageFont.truetype("consolab.ttf", 12)
    except Exception:
        font_main = font_bold = font_title = font_mono = font_mono_bold = ImageFont.load_default()

    stages = [
        {"desc": "Running Agent Task", "step": 1},
        {"desc": "Running Agent Task", "step": 2},
        {"desc": "Running Agent Task", "step": 3},
        {"desc": "Error Encountered", "step": 4},
        {"desc": "Error Encountered", "step": 5},
        {"desc": "Pin Last Error Clicked", "step": 6},
        {"desc": "Sidecar Reasoning", "step": 7},
        {"desc": "Sidecar Reasoning", "step": 8},
        {"desc": "Typing /digest", "step": 9},
        {"desc": "Session Digest War Report", "step": 10},
        {"desc": "Session Digest War Report", "step": 11},
        {"desc": "Session Digest War Report", "step": 12},
    ]

    for stage_idx, stage in enumerate(stages):
        step = stage["step"]
        img = Image.new("RGB", (width, height), "#0f172a")
        draw = ImageDraw.Draw(img)

        # Background gradient / split
        draw.rectangle([0, 0, width, height], fill="#0b0f19")
        
        # --- LEFT PANE: Terminal (width: 440) ---
        term_x, term_y, term_w, term_h = 20, 20, 410, 460
        draw.rounded_rectangle([term_x, term_y, term_x + term_w, term_y + term_h], radius=10, fill="#1e1e2e", outline="#313244", width=1)
        
        # Terminal Title Bar
        draw.rectangle([term_x, term_y, term_x + term_w, term_y + 36], fill="#181825")
        draw.ellipse([term_x + 12, term_y + 12, term_x + 24, term_y + 24], fill="#f38ba8")
        draw.ellipse([term_x + 30, term_y + 12, term_x + 42, term_y + 24], fill="#f9e2af")
        draw.ellipse([term_x + 48, term_y + 12, term_x + 60, term_y + 24], fill="#a6e3a1")
        draw.text((term_x + 140, term_y + 10), "ZSH: antigravity-cli (Primary)", fill="#a6adc8", font=font_mono)

        # Terminal Content
        term_lines = [
            ("user@dev:~/project$ antigravity --task 'Refactor auth'", "#89b4fa"),
            ("🤖 [Antigravity] Scanning repository files...", "#cdd6f4"),
            ("⚡ Call: view_file(path='src/auth.py')", "#fab387"),
            ("🛠️ [TOOL OUTPUT]: auth.py (2.4 KB loaded)", "#a6adc8"),
        ]
        
        if step >= 4:
            term_lines.extend([
                ("⚡ Call: run_command('pytest tests/test_auth.py')", "#fab387"),
                ("💥 ConnectionResetError: [WinError 10054] Remote host closed", "#f38ba8"),
                ("🔴 Agent state: WAITING_ON_ERROR (Turn 6)", "#f38ba8")
            ])
        if step >= 10:
            term_lines.extend([
                ("✅ Applied fix: retry backoff enabled", "#a6e3a1"),
                ("🎉 39 tests passed in 9.45s", "#a6e3a1")
            ])

        ty = term_y + 48
        for t_text, t_color in term_lines[-10:]:
            draw.text((term_x + 16, ty), t_text, fill=t_color, font=font_mono)
            ty += 22

        # --- RIGHT PANE: Gabriel Sidecar (width: 420) ---
        gab_x, gab_y, gab_w, gab_h = 450, 20, 430, 460
        draw.rounded_rectangle([gab_x, gab_y, gab_x + gab_w, gab_y + gab_h], radius=10, fill="#faf8f5", outline="#e6e1da", width=1)

        # Gabriel Header
        draw.rectangle([gab_x, gab_y, gab_x + gab_w, gab_y + 42], fill="#f4efe6")
        draw.text((gab_x + 16, gab_y + 12), "👼 Gabriel Sidecar (1/4 Screen)", fill="#1e293b", font=font_title)
        draw.rounded_rectangle([gab_x + gab_w - 90, gab_y + 8, gab_x + gab_w - 14, gab_y + 32], radius=6, fill="#6366f1")
        draw.text((gab_x + gab_w - 78, gab_y + 12), "Ctrl + M", fill="#ffffff", font=font_mono)

        # Fleet Tab Bar
        draw.rectangle([gab_x, gab_y + 42, gab_x + gab_w, gab_y + 72], fill="#f0ebe1")
        draw.rounded_rectangle([gab_x + 10, gab_y + 46, gab_x + 110, gab_y + 68], radius=4, fill="#ffffff")
        draw.text((gab_x + 16, gab_y + 50), "⚡ Auto-Follow", fill="#4f46e5", font=font_mono_bold)
        draw.text((gab_x + 125, gab_y + 50), "🟢 Antigravity", fill="#64748b", font=font_mono)
        draw.text((gab_x + 235, gab_y + 50), "🟣 ClaudeCode", fill="#64748b", font=font_mono)

        # Mini Status Banner
        if step < 4:
            b_bg, b_dot, b_text = "#ecfdf5", "#10b981", "🟢 [Antigravity] Running · Tool: view_file"
        elif step < 10:
            b_bg, b_dot, b_text = "#fef2f2", "#ef4444", "🔴 [Antigravity] ConnectionResetError (Turn 6)"
        else:
            b_bg, b_dot, b_text = "#ecfdf5", "#10b981", "🟢 [Antigravity] Standing by (Done)"

        draw.rounded_rectangle([gab_x + 12, gab_y + 80, gab_x + gab_w - 12, gab_y + 112], radius=6, fill=b_bg, outline="#cbd5e1", width=1)
        draw.ellipse([gab_x + 22, gab_y + 92, gab_x + 30, gab_y + 100], fill=b_dot)
        draw.text((gab_x + 36, gab_y + 88), b_text, fill="#0f172a", font=font_bold)

        if step >= 4 and step < 9:
            draw.rounded_rectangle([gab_x + gab_w - 100, gab_y + 84, gab_x + gab_w - 18, gab_y + 108], radius=4, fill="#fee2e2", outline="#ef4444", width=1)
            draw.text((gab_x + gab_w - 94, gab_y + 88), "📌 引用报错", fill="#b91c1c", font=font_mono_bold)

        # Gabriel Body / Chat History
        cy = gab_y + 124
        if step < 6:
            draw.text((gab_x + 16, cy), "Gabriel 智能副屏已就绪。主终端日志静默监听中...", fill="#64748b", font=font_main)
        elif step < 9:
            draw.rounded_rectangle([gab_x + 12, cy, gab_x + gab_w - 12, cy + 40], radius=4, fill="#f1f5f9")
            draw.text((gab_x + 18, cy + 6), "📌 [已挂载最新报错快照]:", fill="#475569", font=font_mono_bold)
            draw.text((gab_x + 18, cy + 22), "ConnectionResetError: Remote host closed connection", fill="#e11d48", font=font_mono)
            cy += 48
            draw.rounded_rectangle([gab_x + 12, cy, gab_x + gab_w - 12, cy + 90], radius=6, fill="#ffffff", outline="#e2e8f0")
            draw.text((gab_x + 18, cy + 8), "💡 Gabriel 战术副脑建议:", fill="#4338ca", font=font_bold)
            draw.text((gab_x + 18, cy + 28), "1. 连接被远端重置，建议在客户端加入指数退避重试 (Backoff)", fill="#334155", font=font_main)
            draw.text((gab_x + 18, cy + 48), "2. 该排查全程在副脑沙盒运行，主终端未受到任何打扰与污染", fill="#059669", font=font_main)
            draw.text((gab_x + 18, cy + 68), "3. 点击下方【沉淀至知识库】可永久保存此经验", fill="#64748b", font=font_main)
        elif step >= 9:
            # Show War Report Modal
            draw.rounded_rectangle([gab_x + 12, cy, gab_x + gab_w - 12, cy + 200], radius=8, fill="#ffffff", outline="#6366f1", width=2)
            draw.rectangle([gab_x + 14, cy + 2, gab_x + gab_w - 14, cy + 32], fill="#e0e7ff")
            draw.text((gab_x + 22, cy + 8), "📊 会话复盘战报 · Session Digest", fill="#312e81", font=font_bold)
            
            draw.text((gab_x + 22, cy + 40), "• 智能体: Antigravity | 步数: 14 步 | Token: ~32.4k", fill="#1e293b", font=font_mono_bold)
            draw.text((gab_x + 22, cy + 62), "• 任务目标: 修复鉴权管线连接重置异常并全通单测", fill="#334155", font=font_main)
            draw.text((gab_x + 22, cy + 84), "• 避坑经验: Windows 端口复用需启用 keep-alive 心跳", fill="#059669", font=font_main)
            
            draw.rounded_rectangle([gab_x + 22, cy + 120, gab_x + 150, cy + 150], radius=4, fill="#4f46e5")
            draw.text((gab_x + 36, cy + 128), "📋 复制战报", fill="#ffffff", font=font_bold)

            draw.rounded_rectangle([gab_x + 160, cy + 120, gab_x + 310, cy + 150], radius=4, fill="#10b981")
            draw.text((gab_x + 172, cy + 128), "💾 经验沉淀至知识库", fill="#ffffff", font=font_bold)

        # Bottom Prompt Input Bar
        draw.rounded_rectangle([gab_x + 12, gab_y + gab_h - 48, gab_x + gab_w - 12, gab_y + gab_h - 10], radius=6, fill="#ffffff", outline="#cbd5e1", width=1)
        if step == 9:
            input_txt = "/digest"
        elif step >= 6 and step < 9:
            input_txt = "请分析刚才报错并给出修复步骤..."
        else:
            input_txt = "Ask Gabriel (零干扰副脑推演)..."
        draw.text((gab_x + 22, gab_y + gab_h - 36), input_txt, fill="#475569" if step >= 6 else "#94a3b8", font=font_mono)

        # Watermark/Footer
        draw.text((width // 2 - 160, height - 16), "Gabriel: Zero-Intrusion Desktop GUI Sidecar for CLI AI Agents", fill="#64748b", font=font_mono)

        # Hold longer on final frames
        duration = 1200 if step in (3, 5, 8, 12) else 600
        frames.append((img, duration))

    # Save animated GIF
    images = [f[0] for f in frames]
    durations = [f[1] for f in frames]
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"✅ Demo GIF successfully generated at: {output_path} ({os.path.getsize(output_path) / 1024:.1f} KB)")

if __name__ == "__main__":
    create_demo_gif()
