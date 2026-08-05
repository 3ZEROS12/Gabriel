from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gabriel-ui",
    version="3.1.0",
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
        "openai"
    ],
    entry_points={
        "console_scripts": [
            "gabriel=src.main:main",
        ],
    },
)
