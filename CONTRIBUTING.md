# Contributing

Thanks for considering a contribution. This repository is meant to stay useful, portable, and understandable for people with basic computer skills.

## Good contributions

Helpful contributions include:

- Fixing unclear setup instructions.
- Improving examples, screenshots, or walkthroughs.
- Adding a focused skill that solves one clear job.
- Making scripts more portable across Windows, macOS, and Linux.
- Reporting broken links, missing files, or confusing wording.

## Before you contribute

Please do not include:

- API keys, tokens, passwords, private keys, or `.env` files.
- Real client, customer, employee, patient, student, or legal matter data.
- Private contracts, emails, screenshots, logs, exports, or transcripts.
- Machine-specific home-folder paths from your own computer.
- Generated cache folders such as `__pycache__`.

If you use example data, make it synthetic.

## Skill format

Each skill should be its own folder and should include a `SKILL.md` file. Keep the folder name short and readable.

A good `SKILL.md` should include:

- A clear `name`.
- A clear `description` that says when the AI assistant should use the skill.
- Plain-language instructions.
- Any required setup steps.
- Safe example inputs and outputs when useful.

If the skill includes scripts, document what they do and how to run them. Avoid hardcoded local paths and secrets.

If the skill grew out of your own setup, run the [skill normalization playbook](./SKILL-NORMALIZATION.md) before submitting. It walks through scrubbing personal data, secrets, and local paths, and confirms the skill works as a standalone copy.

## Pull request checklist

Before opening a pull request:

- Read the changed files yourself.
- Confirm no private data or secrets are included.
- Confirm links and image paths work.
- Update `README.md` if you add, remove, or rename a skill.
- Explain what changed and how you tested it.

By contributing, you agree that your contribution is licensed under the MIT License for this repository.

