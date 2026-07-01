# Founding case study — ASMP, the registry that never took a pulse

The first patient, and the reason this school exists. A real session, lightly
edited. Read it before the curriculum; it is the failure the method prevents.

## The setup

ASMP (Agent Service Manifest Protocol) runs a local registry on `127.0.0.1:7700`.
Its `/health` endpoint answered:

```json
{ "status": "ok", "total": 51, "healthy": 0, "unhealthy": 0, "unchecked": 51 }
```

Looks diligent — 51 services, all "unchecked," honest about not knowing. Except the
server source (`asmp-serve.py`) *hardcodes* those numbers:

```python
if path == "/health":
    self._json({ "status": "ok", "total": len(services),
                 "healthy": 0, "unhealthy": 0, "unchecked": len(services) })
```

There is no probe anywhere in the process. `"unchecked": 51` is a literal. The
registry had never taken a pulse in its life and reported `"status": "ok"`. **This
is rubric #1's cardinal sin: a fabricated status.**

## Taking real vitals

Every manifest already carried a real `health` block (`http` / `tcp` /
`launchctl`). Nobody was running them. So we did — 51 probes, parallel, stdlib.
The truth:

```
total=51  healthy=8  degraded=2  unhealthy=27  unchecked=14
```

Not "ok." **8 up, 27 down.**

## The chart that didn't exist

Then the operator asked the right question: *which of these does anyone actually
use, and when last?* The registry stores no usage. We tried to reconstruct it and
found the trap:

- **zsh history** → only catches services typed by name; everything reached over
  HTTP/MCP read `0`. And no timestamps at all (EXTENDED_HISTORY off, no atuin).
- **log mtime** → measures *daemon activity*, not *user usage*. A sync job writing a
  heartbeat every 30s is not "the user used this."

Both proxies lied in opposite directions. The honest answer — **the data does not
exist yet; build a usage ledger going forward** — is rubric #2 and #4 in one breath.

## Triage — 27 down was really ~5 causes

The scary number collapsed under clustering:

- **`:8787` — one dead server.** 12 Reeves services (kernel, email, finance,
  health, home, lens, messages, mechanic, relationships, router, tax, wealth) +
  `caddy` all probe `localhost:8787`. One process down, thirteen red rows.
- **`launchd` jobs not loaded:** the `reeves-*` sync/embedding jobs, `tosh-tunnel`,
  `mac-bridge-tunnel`, and — worth a look — **`tailscale`**.
- **Other single processes:** `postgresql`, `docker`, `discern`, `claude-resume-duet`.
- **`example-service`** — the ASMP template. Down by design; not a finding.

Headline: *"One dead server on :8787 took 13 services with it. Postgres and Docker
are down. Several dormant-by-design daemons are unloaded. That's the diagnosis —
not 27 alarms."*

## The five lessons this patient taught

1. **Vitals that don't lie** — a check that never probes and says "ok" is malpractice.
2. **A chart, not just vitals** — without usage, "27 down" is a false alarm; most were dormant.
3. **Triage to root cause** — 27 symptoms, ~5 causes, 1 that matters (the DB).
4. **Honest blind spots** — say "usage data doesn't exist yet," never launder a proxy.
5. **Cheap and repeatable** — the whole checkup was stdlib and parallel; it runs in seconds.

The prober that came out of this session is `scripts/probe.py`. Run it against this
same fleet with `--asmp http://127.0.0.1:7700` and you will reproduce the numbers
above. That reproduction *is* lesson one: the vitals were always available; the
registry just never looked.
