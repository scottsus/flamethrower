<h1 align='center'>🔥 flamethrower</h1>

No bugs can survive the test of <span style='color: orange'>fire</span>; not even the ones you wrote into your codebase 🪲.

[![GitHub Repo](https://img.shields.io/badge/scottsus-flamethrower-red?&logo=github)](https://github.com/scottsus/flamethrower)
![PyPI](https://img.shields.io/pypi/v/flamethrower.svg)
![Code Size](https://img.shields.io/github/languages/code-size/scottsus/flamethrower.svg)
[![Discord](https://img.shields.io/discord/XP4vVUQKPf.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/XP4vVUQKPf)
![License](https://img.shields.io/github/license/scottsus/flamethrower.svg)
[![Twitter](https://img.shields.io/twitter/follow/susantoscott.svg)](https://twitter.com/susantoscott)

## What is this?

🔥 flamethrower is an open source, multi-agent, context-intelligent, debugger that utilizes AI superpowers to automate the painful task of debugging. Think a combination of GitHub Copilot's context-awareness in [KillianLucas' Open Interpreter](https://github.com/KillianLucas/open-interpreter) packed into a beautiful shell that works out of the box with any existing repo.

    Automate: [ Write Code → Run Action → Check Logs → Repeat ] 🚀🚀

**Main Differentiators**

- 🔥 Automate the most painful part of writing code: print statements & error logs
- ☘️ Specialized context agent for operating within existing repo
- 🤖 Debugging agent optimized to iteratively brute-force locate and fix bugs
- 📦 Out of the box support for any unix machine (no VS Code or VS Code alternatives)
- 🎨 Seamless integration into any existing repo; just type `flamethrower`

## Demo

https://github.com/scottsus/flamethrower/assets/88414565/e3c979c0-40ff-4976-aa30-2503a2827742

## Quick Start

<img src='https://github.com/scottsus/flamethrower/assets/88414565/4be238a7-642a-4149-a1ed-98ff7c61f9b8' alt='Quick Start' width='500px'/>

### Install 🔥 flamethrower

```
pip install flamethrower
```

Or, if you have an existing version and are looking to upgrade to the latest version

```
pip install --upgrade flamethrower
```

### Terminal

Navigate to your current workspace, and simply run `flamethrower`, or `ft` for the pros.

```
cd ./unbelievably/complicated/workspace
flamethrower
```

### Example Usage

Use lowercase letters for commands you run in the shell, like `python main.py` or `node server.ts`

```
🔥 flamethrower: Debugging on Autopilot

Instructions:
- ⌨️  Regular shell        Use commands like ls, cd, python hello.py
- 🤖 LLM assistance       Start command with a Capital letter, try Who are you?
- 📚 Context              Intelligent context-awareness from command, files, and stdout logs
- 🪵 Terminal logs        All conversation & code output inside flamethrower is logged

...

$ python main.py -> SOME_ERROR
$ Wtf???? # Literally type this in the terminal
```

An implementation run is initiated with a natural language query that begins with an `uppercase letter`.

## Features

### 💤 AFK Debugging

If you say 'Yes', 🔥 flamethrower will debug in the background while you focus on other tasks at hand. It acts similarly to any other human engineer: adding `print` statements to find the root cause of the issue (which, as we know is the most annoying part). We find this pattern strikingly effective, and is where we believe LAMs have the strongest use case.

If it looks like 🔥 flamethrower is obviously headed in the direction of doom, simply press `CTRL+C` and give it more suggestions or context.

<img src='https://github.com/scottsus/flamethrower/assets/88414565/11886370-1da4-478e-8fac-853fd305621a' alt='AFK' width='500px'/>

### 🎙️ Conversation History

As long as any shell command or natural language query happens within the context of 🔥 flamethrower, then it is by default captured in the conversation history. That means you can:

- ask about an error that just happened, or happened 2 dialogues ago
- follow up on a previous response provided by 🔥 flamethrower

### 🔍 Prompt Transparency

Prompts sent to LLM are transparent and easy to observe. All 🔥 flamethrower metadata are neatly kept in a `.flamethrower` subdirectory, including prompts, conversations, logs, directory info, summaries, and other metadata.

<img src='https://github.com/scottsus/flamethrower/assets/88414565/8905018d-41f5-48e8-92f5-da2b0512af3d' alt='Transparency' width='500px'/>

### 🏄‍♀️ Real Time File Tracking

Everytime you send a query, the latest version of your files are sent over, meaning 🔥 flamethrower understands that you changed your files, and are ready to process those changes.

<img src='https://github.com/scottsus/flamethrower/assets/88414565/f3f49b91-1cc8-452c-8625-54d88dcb2a42' alt='Context' width='500px'/>

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

- [x] 🧪 Better testing
- [ ] 🔭 Telemetry and the ability to opt in/out
- [ ] 🥽 LLM Vision to debug visual elements
- [ ] 🦙 Running CodeLlama locally
- [ ] 🤖 Other models besides OpenAI
- [ ] 🦾 Default model finetuned on telemetry data
- [ ] 🎗️ VS Code integration
- [ ] 💻 Browser interface
