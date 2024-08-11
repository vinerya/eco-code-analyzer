from setuptools import setup, find_packages

setup(
    name="eco-code-analyzer",
    version="0.2.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "eco-code-analyzer=eco_code_analyzer.cli:main",
        ],
    },
    install_requires=[
        "astroid",
        "gitpython",
    ],
    extras_require={
        "dev": ["pytest", "flake8"],
    },
    author="Moudather Chelbi",
    author_email="moudather.chelbi@gmail.com",
    description="A Python library that analyzes code for ecological impact",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vinerya/eco-code-analyzer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)