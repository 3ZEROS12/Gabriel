from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gabriel-ui",
    version="4.0.0",
    description="A lightweight, non-intrusive GUI sidecar for CLI-based AI agents.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gabriel Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "websockets",
        "openai",
        "python-dotenv",
        "pywebview",
        "mcp>=1.28",
        "jieba>=0.42.1",
        "tenacity>=9.0.0",
        "sqlite-vec>=0.1.9",
        "fastembed>=0.8.0",
    ],
    entry_points={
        "console_scripts": [
            "gabriel=src.main:main",
        ],
    },
)
