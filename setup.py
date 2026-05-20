from setuptools import setup, find_packages

setup(
    name="operator-cli",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "typer[all]",
        "rich",
        "ollama",
        "pydantic-settings",
    ],
    entry_points={
        "console_scripts": [
            "operator=operator_cli.main:app",
        ],
    },
    python_requires=">=3.10",
    author="Gemini CLI",
    description="A lightweight agentic command line interface for context-aware AI operations.",
)
