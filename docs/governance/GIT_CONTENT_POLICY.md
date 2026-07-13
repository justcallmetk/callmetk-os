# Git Content Policy

## Safe to keep in Git

- source code
- tests
- public documentation
- architecture standards
- sanitized examples
- empty or synthetic CSV templates
- database schemas and migrations
- non-secret configuration examples
- GitHub Actions workflows
- release notes and changelogs
- public brand guidance intended for collaborators

## Keep out of Git

- API keys, passwords, tokens, cookies, and `.env` files
- private customer, student, fan, or employee information
- unreleased masters, stems, vocals, raw video, and private photographs
- trained model weights containing likeness or proprietary data
- production databases and backups
- private contracts, financial records, legal documents, and internal negotiations
- raw chat exports containing personal or sensitive context
- copyrighted third-party media without redistribution rights
- generated caches, virtual environments, build artifacts, and local indexes

## Public versus private repository

A public repository should contain the platform code and a sanitized statement of philosophy. Detailed internal procedures, private strategy, proprietary prompts, and unreleased product plans may live in a separate private repository or encrypted document store.

Recommended split:

```text
callmetk-os                # public or collaborator-safe code and standards
callmetk-os-private        # private strategy, procedures, prompt library, internal decisions
callmetk-library           # local/cloud creative assets; not a normal Git repository
```

## Documentation rule
Do not commit raw historical chats. Extract stable principles into reviewed Markdown documents, then preserve the raw source privately.
