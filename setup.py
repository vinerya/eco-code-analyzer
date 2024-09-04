from setuptools import setup, find_packages

setup(
    name="eco-code-analyzer",
    version="0.3.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "eco-code-analyzer=eco_code_analyzer.cli:main",
        ],
    },
    install_requires=[
        "astroid",
        "gitpython",
        "matplotlib",
    ],
    extras_require={
        "dev": ["pytest", "flake8", "black"],
    },
    author="Moudather Chelbi",
    author_email="moudather.chelbi@gmail.com",
    description="A Python library that analyzes code for ecological impact and provides optimization suggestions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vinerya/eco-code-analyzer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.7',
    keywords='code analysis, environmental impact, energy efficiency, eco-friendly coding',
)