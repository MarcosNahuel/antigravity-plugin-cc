# Security Policy

## Reporting a vulnerability

If you find a security issue in this plugin (the plugin source — not in `agy` itself or in Claude Code), please report it privately:

- **Email**: contact@traidai.com with the subject line `[security] antigravity-plugin-cc`.
- Or open a [private security advisory](https://github.com/MarcosNahuel/antigravity-plugin-cc/security/advisories/new) on GitHub.

I'll respond within 7 days.

## Credentials

This plugin never asks for, stores, or proxies your Anthropic/Claude Pro or Max credentials, nor any API key. It shells out to your locally installed `agy` CLI and inherits **your own Google OAuth session** (the one you set up the first time you ran `agy` interactively) — bring-your-own-key / bring-your-own-login. No account tokens pass through this plugin's code.

## Scope

In scope:
- Prompt injection vectors specific to how this plugin constructs `agy` invocations.
- Command injection through unescaped slash-command arguments.
- Paths the plugin writes to (`docs/agy/research/`) — directory traversal, accidental overwrites of unrelated files.

Out of scope:
- Vulnerabilities in `agy` itself → report to Google.
- Vulnerabilities in Claude Code → report to Anthropic.
- Issues that require the attacker to already have shell access to the user's machine.

## Supported versions

Only the latest release on `main` is supported. Pin to a tag if you need stability guarantees in CI.
