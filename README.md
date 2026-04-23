# StateTalk - A Dialogue Flow Language Compiler

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![PLY](https://img.shields.io/badge/PLY-3.11-green.svg)](https://github.com/dabeaz/ply)

A domain-specific language (DSL) compiler for creating text-based chatbots using state machines. Part of the **CS4031 - Compiler Construction** course project at FAST-NUCES. 

## Overview

**StateTalk** is a high-level language designed to simplify chatbot development through intuitive state-based dialogue flows. Write conversation logic in a clean, readable syntax, and the compiler generates executable Python code.

## Compile and run:

```bash
python compiler.py example.st
python example_bot.py
```
## Architecture
```
statetalk_compiler/
├── compiler.py          # Main compiler (Lexer, Parser, Code Generator)
├── example.st           # Sample StateTalk program
├── requirements.txt     # Dependencies
└── README.md           # Documentation
```

## Installation
### Prerequisites
- Python 3.6 or higher
- pip (Python package manager)

### Setup
1. Clone the repository:
```bash
git clone https://github.com/safiamussaratt/statetalk_compiler.git
cd statetalk
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Compile the example:
```bash
python compiler.py example.st
```
4. Run the chatbot:
```bash
python example_bot.py
```
