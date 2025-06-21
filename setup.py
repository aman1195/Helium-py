from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="helium-ai",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Helium AI - Multi-agent system for AI-powered research and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/helium-ai",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        # Core Dependencies
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        
        # LLM and AI
        "langchain>=0.1.0",
        "langgraph>=0.0.15",
        "google-generativeai>=0.3.2",
        
        # Web and API
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "httpx>=0.25.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    entry_points={
        "console_scripts": [
            "helium-ai=main:main",
        ],
    },
)
