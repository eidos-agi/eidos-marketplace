# Security

Converge is a local plugin and adapter framework. It should not call remote
models, services, or package registries unless an adapter explicitly documents
that behavior and the user opts in.

## Reporting

Report security issues to `hello@eidosagi.com`.

Please include:

- affected version or commit
- adapter or schema involved
- reproduction steps
- expected impact
- whether secrets, proprietary data, or generated evidence files are involved

## Threat Model

Converge handles evidence about software correctness. That evidence can include
paths, command output, test names, API results, and business-rule summaries.

Primary risks:

- leaking sensitive evidence in rows or reports
- false green scores caused by stale or malformed adapter rows
- adapters silently calling external systems
- schema drift between spec inputs and adapter outputs
- repair summaries hiding conflicting evidence

Mitigations:

- adapter rows are validated against `schemas/converge-row.schema.json`
- full starter specs are validated against `schemas/converge-spec.schema.json`
- aggregators preserve conflicts instead of overwriting them silently
- adapters should emit `blocked`, `missing`, `drift`, or `regression` rather than guessing
- adapters in this plugin are local and deterministic

Do not put secrets in Converge rows. Use evidence paths or redacted snippets
when raw output contains credentials, personal data, or customer-sensitive data.
