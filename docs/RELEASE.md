# Gabriel (加百列) 发布与分发指南 (Release & Distribution Guide)

本文档说明 Gabriel 项目的标准发布流程，包括 **PyPI (sdist + wheel) 包构建** 与 **Windows 桌面可执行文件 (PyInstaller) 打包**。

---

## 1. 预备工作 (Prerequisites)

在独立干净的环境中安装构建工具：

```bash
python -m pip install --upgrade pip
pip install build twine pyinstaller
```

---

## 2. 路径 A：PyPI 发布 (sdist + wheel)

### 2.1 构建源码包与 Wheel 包

```bash
# 清理旧产物
rm -rf build/ dist/ *.egg-info/

# 构建 sdist (.tar.gz) 与 wheel (.whl)
python -m build
```

预期产物位于 `dist/` 目录：
- `dist/gabriel_ui-3.1.0-py3-none-any.whl`
- `dist/gabriel_ui-3.1.0.tar.gz`

### 2.2 包元数据合规检查

```bash
twine check dist/*
```
预期输出：`PASSED`

### 2.3 全新虚拟环境安装与 CLI 冒烟验证

在全新独立 venv 中验证包可正常安装与命令行入口工作：

```bash
# 创建临时干净环境
python -m venv venv_test_release
venv_test_release\Scripts\pip install dist\gabriel_ui-3.1.0-py3-none-any.whl

# 验证 CLI 命令帮助输出
venv_test_release\Scripts\gabriel --help
```

### 2.4 上传至 PyPI (需要发布凭据)

> ⚠️ **注意**：PyPI 上传命令需要用户 API Token 凭据，必须由维护者人工确认后在终端执行。

```bash
# 上传至 PyPI
twine upload dist/*
```

---

## 3. 路径 B：Windows 独立应用打包 (PyInstaller onedir)

> v4.0.0 起：onedir 解压即用 + 数据/代码分离。`Gabriel.spec` 是构建配置（已被 `.gitignore` 忽略，不提交），构建与参数策略见 `docs/OPTIMIZATION_ROADMAP_2026.md`「双击即用」一节。

### 3.1 构建

```bash
venv\Scripts\python.exe -m PyInstaller Gabriel.spec --noconfirm --clean
```

产物目录：`dist/Gabriel/`（`Gabriel.exe` + `_internal/`）。发行包：

```bash
# 清掉冒烟产生的数据文件后打包
rm -rf dist/Gabriel/knowledge.db dist/Gabriel/config.json dist/Gabriel/logs dist/Gabriel/.gabriel.lock
cd dist && Compress-Archive -Path Gabriel -DestinationPath Gabriel-v4.0.0-win64.zip
```

### 3.2 双击即用行为（v4.0.0）

1. 双击 `Gabriel.exe`：控制台显示 token 与日志（关窗即停）；就绪后自动打开默认浏览器（带一次性 token 直达）。
2. 端口自动避让：8080 被占 → 8081/8082…（最多 20 次）；`--port` 可指定。
3. 单实例：重复双击 → 打开已有实例页面并退出；`--no-browser` 可关闭自动开浏览器。
4. **数据分离**：`knowledge.db` / `config.json` / `logs/` 写 exe 旁（`%cd%` 即数据目录），static 只读区在 `_internal/`——升级替换 exe 文件夹不会丢库。

### 3.3 冒烟验证

1. 进入 `dist/Gabriel/`，运行 `Gabriel.exe --no-browser`。
2. `curl -H "X-Gabriel-Token: <控制台 token>" http://127.0.0.1:8080/api/stats` → 200。
3. `curl -X POST http://127.0.0.1:8080/api/kb -H "X-Gabriel-Token: <token>" -H "Content-Type: application/json" -d '{"content":"冒烟测试"}'` → 写入成功。
4. 重复运行 `Gabriel.exe` → 第二实例秒退，浏览器指向已有实例。

---

## 4. 自动化 CI/CD 流程 (GitHub Actions)

项目仓库已接入 `.github/workflows/ci.yml` 自动化流水线：
1. **test**: 在 `windows-latest` 跑 `ruff check src tests` 与 `pytest` 全量单测。
2. **stability-smoke**: 触发 `scripts/stability_run.py --hours 0.25` 15 分钟稳定性冒烟。
3. **build-windows**: 自动生成 `Gabriel-Windows-Build` 构建产物并上传为 GitHub Actions Artifacts。
