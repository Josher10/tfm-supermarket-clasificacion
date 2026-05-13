---
name: awesome-copilot
description: >-
  Navigates and applies patterns from the community collection github/awesome-copilot
  (agents, skills, instructions, hooks, workflows, plugins, cookbook). Use when the
  user mentions awesome-copilot, Awesome Copilot, Copilot plugins from
  github/awesome-copilot, porting a Copilot skill or instruction to Cursor, finding
  MCP servers or agentic workflows from that collection, or wants to browse or
  install resources from awesome-copilot.github.com.
---

# Awesome Copilot (github/awesome-copilot)

## What it is

[github/awesome-copilot](https://github.com/github/awesome-copilot) is a curated community collection of GitHub Copilot customizations: agents, file-scoped instructions, skills (Agent Skills layout with `SKILL.md`), plugins, hooks, agentic workflows, and a cookbook. Treat content as **third-party**; read `SKILL.md` and any scripts before relying on them.

## Discovery (fastest first)

1. **Website** — [awesome-copilot.github.com](https://awesome-copilot.github.com): full-text search, filters, [Tools](https://awesome-copilot.github.com/tools) (MCP and tooling), [Learning Hub](https://awesome-copilot.github.com/learning-hub).
2. **Machine index** — [awesome-copilot.github.com/llms.txt](https://awesome-copilot.github.com/llms.txt): structured listings for agents, instructions, and skills (good for agents parsing the catalog).
3. **Repo** — Browse `docs/README.*.md` tables: [agents](https://github.com/github/awesome-copilot/blob/main/docs/README.agents.md), [instructions](https://github.com/github/awesome-copilot/blob/main/docs/README.instructions.md), [skills](https://github.com/github/awesome-copilot/blob/main/docs/README.skills.md), [plugins](https://github.com/github/awesome-copilot/blob/main/docs/README.plugins.md), [hooks](https://github.com/github/awesome-copilot/blob/main/docs/README.hooks.md), [workflows](https://github.com/github/awesome-copilot/blob/main/docs/README.workflows.md).

## Map collection types to Cursor

| Awesome Copilot | In Cursor |
|-----------------|-----------|
| Skill folder (`SKILL.md` + assets) | Same shape works: project `.cursor/skills/<name>/` or personal `~/.cursor/skills/<name>/` (not `skills-cursor`, which is reserved). Adapt frontmatter/triggers to Cursor’s skill rules. |
| Instructions (globs, coding standards) | `.cursor/rules/`, `AGENTS.md`, or project docs the agent reads. |
| Custom agents | Cursor Rules + skills + MCP; no 1:1 “agent pack” — port behavior into rules/skills. |
| Hooks | Cursor [hooks](https://cursor.com/docs/hooks.md) (`hooks.json` + scripts); patterns may translate with different events/APIs. |
| Agentic workflows (markdown Actions) | GitHub Actions / automation; reuse ideas, not file paths. |
| Plugins (`@awesome-copilot`) | **GitHub Copilot CLI / VS Code** marketplace: `copilot plugin marketplace add github/awesome-copilot` then `copilot plugin install <name>@awesome-copilot`. Not a Cursor plugin format. |

## Bring a skill into Cursor

1. Open the skill path in the repo, e.g. `skills/<skill-id>/SKILL.md` (see [README.skills.md](https://github.com/github/awesome-copilot/blob/main/docs/README.skills.md)).
2. Copy the **folder** (not only `SKILL.md`) if it references `scripts/`, `references/`, or `assets/`.
3. Paste under `.cursor/skills/<skill-id>/` (repo) or `~/.cursor/skills/<skill-id>/` (personal).
4. Edit YAML `description` for Cursor discovery (third person, WHAT + WHEN, trigger terms). Remove or replace Copilot-only assumptions (CLI tools, Joyride-only steps, etc.).
5. If the upstream skill documents `gh skills install github/awesome-copilot <skill-id>`, that targets **Copilot’s** skill install path; for Cursor, manual copy (or script) is the portable approach.

## Copilot-only install commands (reference)

For users who also use GitHub Copilot:

```bash
copilot plugin marketplace add github/awesome-copilot
copilot plugin install <plugin-name>@awesome-copilot
```

Skills via GitHub CLI (Copilot): `gh skills install github/awesome-copilot <skill-id>` (requires a recent `gh` with skills support — see upstream docs).

## Agent behavior

- Prefer **fetching** the specific upstream `SKILL.md` (raw GitHub or local clone) over guessing bundled script behavior.
- When porting, preserve **licenses** and attribution files bundled with the skill.
- If the user only needs an idea (e.g. prompt structure), summarize from the doc without copying large proprietary-looking blocks unless license allows.
