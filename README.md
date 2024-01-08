<h1 align='center'>🔥 flamethrower</h1>

LLM agents in your local machine → the ultimate debugging experience

[![GitHub Repo](https://img.shields.io/badge/scottsus-flamethrower-red?&logo=github)](https://github.com/scottsus/flamethrower)
![PyPI](https://img.shields.io/pypi/v/flamethrower.svg)
![Code Size](https://img.shields.io/github/languages/code-size/scottsus/flamethrower.svg)
[![Discord](https://img.shields.io/discord/XP4vVUQKPf.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.XP4vVUQKPf)
![License](https://img.shields.io/github/license/scottsus/flamethrower.svg)
[![Twitter](https://img.shields.io/twitter/follow/susantoscott.svg)](https://twitter.com/susantoscott)

## What is this?

🔥 flamethrower is an open source, high level, debugger that utilizes AI superpowers to draw context, offer suggestions, and iterate on those suggestions to accomplish a given task. Think a combination of GitHub Copilot's context-awareness in [KillianLucas' Open Source Open Interpreter](https://github.com/KillianLucas/open-interpreter) shell.

## Demo

https://github.com/scottsus/flamethrower/assets/88414565/93195176-c124-4528-b3c2-500ce87cd494

## Quick Start

```
pip install flamethrower
```

### API Keys

There's no getting around the friction of configuring API keys

```
export OPENAI_API_KEY=sk-xxxx
```

### Terminal

Navigate to your current workspace, and simply run `flamethrower`, or `ft` for the pros.

```
cd {UNBELIEVABLY_COMPLICATED_WORKSPACE}
flamethrower
```

### Example Usage

Use lowercase letters for commands you run in the shell, like `python main.py` or `node server.ts`

```
python main.py -> SOME_ERROR
Wtf???? 🤬 # Literally type this in the terminal
```

An implementation run is initiated with a natural language query that begins with an `uppercase letter`.

## Motivation for 🔥 flamethrower

### GitHub Copilot

Closed source GitHub Copilot draws context very effectively, and `Quick Fix` is a neat feature that explains error from stdout logs if the last command returned a non-zero return code.

### Open Interpreter

The Open Interpreter, an open-source gem, specializes in crafting new code from the ground up. It's a favorite among data scientists and those needing sophisticated chart plotting, thanks to its iterative approach to achieving desired results.

### A Research Project?

🔥 flamethrower combines the agency afforded by Large Action Models (LAM) with the workspace awareness of Copilot, allowing it to take context-specific suggestions and continue iteration until a successful outcome. 🔥 is workspace-first, and aims to serve software engineers in complex tasks that need a lot of context management.
