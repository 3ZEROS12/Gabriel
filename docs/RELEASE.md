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

## 3. 路径 B：Windows 桌面独立应用打包 (PyInstaller)

### 3.1 运行 PyInstaller 打包命令

使用根目录下的 `Gabriel.spec` 或命令行一键构建：

```bash
pyinstaller --noconfirm --onedir --windowed --add-data "static;static" --add-data "src;src" src/main.py --name "Gabriel_Agent_OS"
```

产物生成目录：`dist/Gabriel_Agent_OS/`

### 3.2 桌面二进制冒烟验证

1. 进入 `dist/Gabriel_Agent_OS/` 目录。
2. 双击运行 `Gabriel_Agent_OS.exe`。
3. 观察控制台/通知栏输出，在浏览器打开 `http://127.0.0.1:8080`。
4. 确认 Web UI 正常加载，样式与静态资源无 404，控制台打印 Security Token 登录成功。

---

## 4. 自动化 CI/CD 流程 (GitHub Actions)

项目仓库已接入 `.github/workflows/ci.yml` 自动化流水线：
1. **test**: 在 `windows-latest` 跑 `ruff check src tests` 与 `pytest` 全量单测。
2. **stability-smoke**: 触发 `scripts/stability_run.py --hours 0.25` 15 分钟稳定性冒烟。
3. **build-windows**: 自动生成 `Gabriel-Windows-Build` 构建产物并上传为 GitHub Actions Artifacts。
