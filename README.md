<h1 align='center'>🔥 flamethrower</h1>

No bugs can survive the test of <span style='color: orange'>fire</span>; not even the ones you wrote into your codebase 🪲.

[![GitHub Repo](https://img.shields.io/badge/scottsus-flamethrower-red?&logo=github)](https://github.com/scottsus/flamethrower)
![PyPI](https://img.shields.io/pypi/v/flamethrower.svg)
![Code Size](https://img.shields.io/github/languages/code-size/scottsus/flamethrower.svg)
[![Discord](https://img.shields.io/discord/XP4vVUQKPf.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/XP4vVUQKPf)
![License](https://img.shields.io/github/license/scottsus/flamethrower.svg)
[![Twitter](https://img.shields.io/twitter/follow/susantoscott.svg)](https://twitter.com/susantoscott)

## What is this?

🔥 flamethrower is an open source, high level, debugger that utilizes <span style='color: orange'>AI superpowers</span> to <span style='color: orange'>draw context</span>, offer suggestions, and <span style='color: orange'>iterate on those suggestions</span> to accomplish a given task. Think a combination of GitHub Copilot's context-awareness in [KillianLucas' Open Source Open Interpreter](https://github.com/KillianLucas/open-interpreter) shell.

## Demo

https://github.com/scottsus/flamethrower/assets/88414565/2b8a71e6-a36c-4d1c-9bfc-3c487d1540f2

## Usecases

### Understanding error logs

TODO

### Debugging the previous error

TODO

## Quick Start

```
pip install flamethrower
```

Or, if you're looking to upgrade to the latest version

```
pip install --upgrade flamethrower
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

## Features

### 💤 AFK Debugging

If you say 'Yes', 🔥 flamethrower will debug in the background while you focus on other tasks at hand. It acts similarly to any other human engineer: adding `print` statements to find the root cause of the issue (which, as we know is the most annoying part). We find this pattern strikingly effective, and is where we believe LAMs have the strongest use case.

If it looks like 🔥 flamethrower is obviously headed in the direction of doom, simply press `CTRL+C` and give it more suggestions or context.

### 🎙️ Conversation History

As long as any shell command or natural language query happens within the context of 🔥 flamethrower, then it is by default captured in the conversation history. That means you can:

- ask about an error that just happened, or happened 2 dialogues ago
- follow up on a previous response provided by 🔥 flamethrower

### 🔍 Prompt Transparency

Prompts sent to LLM are transparent and easy to observe. All 🔥 flamethrower metadata are neatly kept in a `.flamethrower` subdirectory, including prompts, conversations, logs, directory info, summaries, and other metadata.

### 🏄‍♀️ Real Time File Tracking

Everytime you send a query, the latest version of your files are sent over, meaning 🔥 flamethrower understands that you changed your files, and are ready to process those changes.

## Motivation for 🔥 flamethrower

### 👩‍✈️ GitHub Copilot

Closed source GitHub Copilot draws context very effectively, and `Quick Fix` is a neat feature that explains error from stdout logs if the last command returned a non-zero return code.

### 🤖 Open Interpreter

The Open Interpreter, an open-source gem, specializes in crafting new code from the ground up. It's a favorite among data scientists and those needing sophisticated chart plotting, thanks to its iterative approach to achieving desired results.

### 🔬 Research

🔥 flamethrower combines the agency afforded by Large Action Models (LAM) with the workspace awareness of Copilot, allowing it to take context-specific suggestions and continue iteration until a successful outcome. 🔥 flamethrower is workspace-first, and aims to serve software engineers in complex tasks that need a lot of context management.

## 🥂 Contributing

🔥 flamethrower is everyone's debugger. Fork it for your own use case, and, one PR at a time we can make the world a more bug-free place ✨ just ping me at scottsus@usc.edu and I'll help you get started.

## 🛫 Project Roadmap

- [ ] 🔭 Telemetry and the ability to opt in/out
- [ ] 🥽 LLM Vision to debug visual elements
- [ ] 🦙 Running CodeLlama locally
- [ ] 🤖 Other models besides OpenAI
- [ ] 🦾 Default model finetuned on telemetry data
- [ ] 🎗️ VS Code integration
- [ ] 💻 Browser interface
- [ ] 🧪 Better testing
