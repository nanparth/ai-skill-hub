# Security Policy

## Supported content

This repository shares AI assistant skill folders. Some skills may include scripts or helper files. Treat every third-party skill as code: read it before you run it or give it access to private files.

## Reporting a security issue

Please report security issues privately when possible. Use GitHub private vulnerability reporting if it is enabled for the repository, or contact the maintainer through a private channel listed on the maintainer profile.

Do not include secrets, private documents, customer data, or exploit details in a public issue.

## What to report

Please report:

- Hardcoded credentials, tokens, private keys, or secrets.
- Scripts that access files, networks, or shell commands in an unexpected way.
- Prompt injection risks that could expose private data or run unsafe commands.
- Real personal, customer, legal, or confidential data committed by mistake.
- Dependency or setup instructions that install from an untrusted source.

## What to expect

This is a small personal project, so response time is best effort. If a real secret was committed, revoke or rotate it immediately. Removing the file from the current branch is not enough if it was ever committed to history.
