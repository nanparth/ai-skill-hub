# AI Skills Share

Reusable AI assistant instructions called skills, collected from my own workflows and cleaned up enough to share.

You do not need to install everything here. Start by choosing one skill folder and one AI tool. If you are not sure where to start, watch guide 00 below.

---

## Start here

A skill is a folder that tells an AI assistant how to handle a specific kind of work. Each skill has a `SKILL.md` file, and it may also include helper files like examples, scripts, templates, or references.

Several AI tools support this general format. The shared format is called the [Agent Skills specification](https://agentskills.io/specification).

These skills were not built to a single standard. Some have detailed examples and edge case handling. Some are mostly a `SKILL.md` file and a few notes.

I am releasing them because they are useful to me and I personally deem them to be stable and generalizable enough. They are not finished, polished products. Read through, experiment with, and customize each one before relying on it for serious work.

---

## What's in here

| Skill                                       | What it does                                                                                                                                                |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`legal-diagram`](./legal-diagram/)         | Generates Mermaid diagrams for legal documents, matters, timelines, corporate structures, compliance obligations, funds flows, and related legal workflows. |
| [`biz-interview`](./biz-interview/)         | Creates and analyzes customer discovery interview scripts, transcript notes, coding matrices, hypothesis verdicts, and qualitative reports.                 |
| [`tech-blueprinting`](./tech-blueprinting/) | An interactive session for more rigorous drafting of technical specs, PRDs, RFCs, implementation plans, READMEs, and reader testing.                        |
| [`tech-implement`](./tech-implement/)       | Runs a TDD-oriented implementation or bug-fix pipeline with worktree safety, reviews, and verification gates.                                               |
| [`tech-refactor`](./tech-refactor/)         | Audits structural code problems and produces execution-ready refactor roadmaps with migration and test plans.                                               |

---

## Install your AI tool first

If you do not have an AI coding or agent tool installed yet, start with the official setup docs for the tool you want to use.

- [Claude Code first-day setup](https://support.claude.com/en/articles/14552382-your-first-day-in-claude-code)
- [Claude Cowork setup](https://support.claude.com/en/articles/13345190-get-started-with-cowork)
- [OpenAI Codex CLI](https://developers.openai.com/codex/cli)
- [Cursor CLI installation](https://docs.cursor.com/en/cli/installation)
- [Cursor CLI overview](https://docs.cursor.com/en/cli/overview)
- [GitHub Copilot CLI install](https://docs.github.com/copilot/how-tos/set-up/installing-github-copilot-in-the-cli)

---

## How to install - for those who aren't familiar with GitHub

All install methods start the same way:

1. Download this repository as a ZIP.
2. Unzip it.
3. Pick the skill folder you want.
4. Put that folder where your AI tool expects skills to be located, with the exact place depending on the tool you use.

Confused? Check out the animated guides below.

### 00 - Start Here: Pick The Right Install Type

![Start here: pick the right install type](./walkthroughs/00_opener.gif)

Use this first if you are not sure which install method applies to you. It gives the big picture before you copy, upload, or install anything.

Official docs:

- [Agent Skills specification](https://agentskills.io/specification)

### 01 - Terminal AI Tools: Copy To A Local Skills Folder

![Terminal AI tools: copy to a local skills folder](./walkthroughs/01_cli_agent.gif)

Use this if you run an AI assistant from a terminal, such as Claude Code, Codex, or GitHub Copilot CLI. In this method, you copy the skill folder into a hidden skills folder on your computer.

Official docs:

- [Claude Code Agent Skills](https://docs.claude.com/en/docs/claude-code/skills)
- [OpenAI Codex Skills](https://developers.openai.com/codex/skills)
- [GitHub Copilot agent skills](https://docs.github.com/copilot/concepts/agents/about-agent-skills)

### 02 - Claude In The Browser: Upload A ZIP

![Claude in the browser: upload a ZIP](./walkthroughs/02_claude_web.gif)

Use this if you use Claude in your web browser and want to add a skill to your personal Claude account. You zip one skill folder, upload it in Claude settings, and turn it on.

Official docs:

- [Use Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)

### 03 - VS Code / GitHub Copilot: Add Skills To A Project

![VS Code or GitHub Copilot: add skills to a project](./walkthroughs/03_vscode.gif)

Use this if the skill should travel with a project folder. This is useful when you want the same skill available to everyone working on that project.

Official docs:

- [About agent skills for GitHub Copilot](https://docs.github.com/copilot/concepts/agents/about-agent-skills)
- [Adding agent skills for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-skills)

### 04 - Installer-Based Setup

![Installer-based setup](./walkthroughs/04_installer.gif)

Use this if your AI tool has a built-in installer or command that places skills for you. For Codex, current docs point to local skill folders, plugins for sharing, and `$skill-installer` for curated or repository-based installs.

Official docs:

- [OpenAI Codex Skills](https://developers.openai.com/codex/skills)
- [Adding agent skills for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-skills)

### 05 - Team Or Organization Setup

![Team or organization setup](./walkthroughs/05_org_enterprise.gif)

Use this only if you manage skills for a team, company, school, or shared workspace. This usually means uploading a ZIP or using an admin setting so other people can enable the skill later.

Official docs:

- [Use Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [GitHub Copilot agent skills](https://docs.github.com/copilot/concepts/agents/about-agent-skills)

---

## How to install - for the GitHub pros

### Claude Code on your computer

Personal skill, available across your projects:

```bash
cp -r ./SKILLNAME/ ~/.claude/skills/SKILLNAME/
```

Project skill, available inside one project:

```bash
cp -r ./SKILLNAME/ .claude/skills/SKILLNAME/
```

Final folder layout:

```text
~/.claude/skills/SKILLNAME/SKILL.md
.claude/skills/SKILLNAME/SKILL.md
```

### Claude in the browser

Zip the skill folder, then upload it in Claude:

```text
Claude.ai -> Settings -> Skills -> Add Skill -> Upload ZIP -> Turn on
```

### Codex

User skill, available across your Codex projects:

```bash
cp -r ./SKILLNAME/ "$HOME/.agents/skills/SKILLNAME/"
```

Project skill, available inside one project:

```bash
cp -r ./SKILLNAME/ .agents/skills/SKILLNAME/
```

Final folder layout:

```text
$HOME/.agents/skills/SKILLNAME/SKILL.md
.agents/skills/SKILLNAME/SKILL.md
```

For curated or repository-based installs, Codex also has `$skill-installer`. Do not use `codex skill install ./SKILLNAME/`; that is not the current documented path for these local skill folders.

### VS Code / GitHub Copilot project

Copy the skill folder into one of the project skill folders Copilot supports:

```text
.github/skills/SKILLNAME/SKILL.md
.claude/skills/SKILLNAME/SKILL.md
.agents/skills/SKILLNAME/SKILL.md
```

Then commit and push the project change if you want others to receive it.

### Team or organization account

Zip the skill folder, upload it in your team's skill settings, set visibility for the team, and tell teammates how to enable it.

---

## Using these in your own work

Take them, modify them, and use them as starting points. Attribution is appreciated but not required.

If you build something better on top of one of these, I would be curious to hear about it.

---

## Contributing

Contributions are welcome when they keep the skills clear, safe, and portable. Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before opening an issue or pull request.

Please do not share private documents, real client data, secrets, or local machine paths in examples.

Preparing a personal skill for release? Follow the [skill normalization playbook](./SKILL-NORMALIZATION.md) — the scan, fix, and verify pass that makes a skill private-safe and plug-and-play.

---

## License

This repository is released under the [MIT License](./LICENSE).
