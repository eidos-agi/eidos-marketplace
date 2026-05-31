# Security

Eidos Storemetheus helps create plugin stores that may route agents toward sensitive company systems. Treat store design as a security boundary.

## Reporting

Report security issues to `hello@eidosagi.com`.

## Threat Model

- Private client facts accidentally published into a public marketplace.
- Plugins granted broader operating authority than their documented scope.
- Agents mistaking a marketplace entry for an installed and visible runtime plugin.
- External-effect plugins without approval gates or fail-closed behavior.
- Cache/config drift causing agents to use stale skills.

## Expected Controls

- Private company stores default to private repositories.
- High-risk plugins document approval and proof requirements.
- Store updates include manifest validation, Felix doctor output, and marketplace tests.
- Final status reports distinguish source, store, cache, config, and active-session visibility.
