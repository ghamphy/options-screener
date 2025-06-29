#!/usr/bin/env python3
"""
Setup script for Options Screener package
"""

from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read long description from README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='options-screener',
    version='1.0.0',
    author='Options Screener Team',
    author_email='',
    description='A modular Python library for screening options using Interactive Brokers API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/options_screener',
    py_modules=[
        'options_base',
        'put_screener', 
        'put_option_screener',
        'put_option_test'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
        ],
    },
    entry_points={
        'console_scripts': [
            'options-screener=put_option_screener:main',
            'put-screener=put_option_test:main',
        ],
    },
    keywords='options trading finance interactive-brokers screening puts calls',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/options_screener/issues',
        'Source': 'https://github.com/yourusername/options_screener',
        'Documentation': 'https://github.com/yourusername/options_screener#readme',
    },
) 