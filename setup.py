from setuptools import setup, find_packages

setup(
    name="cortex",
    version="0.1.0",
    description="Consciousness Orchestration & Reasoning Through Experimental eXchange",
    packages=find_packages(),
    install_requires=[
        "anthropic>=0.25.1",
        "openai>=1.30.2",
        "python-dotenv>=1.0.1",
        "rich>=13.7.1"
    ],
    entry_points={
        "console_scripts": ["cortex=cortex.cli:main"]
    }
)