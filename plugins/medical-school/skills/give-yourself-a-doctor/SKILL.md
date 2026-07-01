---
name: give-yourself-a-doctor
description: Use when an AI needs to build itself a self-diagnostic that actually works — health checks, service/component monitoring, "is my system up", "why is everything red", observability that isn't decoration, or when an existing health check is suspected of lying. Teaches the method (inventory → probe → chart → triage → report) stack-agnostically; the graduate installs a doctor on its own stack. Pairs with the-rounds-rubric for grading.
---

# Give Yourself a Doctor

You are going to build a self-diagnostic for **your own stack** — a doctor that
meets the bar in [`the-rounds-rubric`](../the-rounds-rubric/SKILL.md). The stack
could be services, containers, daemons, cron jobs, a SaaS backend, or one laptop.
The method is the same. The reference prober is `scripts/probe.py`; the founding
lecture is `case-studies/asmp.md`. Read the case study once — it shows the exact
failure this method prevents.

Do the five steps in order. Do not skip step 3 because it is the one everyone
skips, and skipping it is why health checks cry wolf.

## 1. Inventory — what are the patients?

List every component that can be up or down, with **how to reach it** and **how to
know it's alive**. Prefer a source that already exists (a service registry, a
Procfile, `docker ps`, `systemctl list-units`, `launchctl list`). If none exists,
write a flat list. Each entry needs a probe method:

| method | alive means | example target |
|---|---|---|
| `http` | GET returns any response (even 4xx = the server answered) | `http://localhost:8080/healthz` |
| `tcp` | port accepts a connection | `localhost:5432` |
| `launchctl` / `systemd` | job loaded **and** has a running PID | `com.foo.bar` / `foo.service` |
| `pid` | a matching process exists | `postgres` |
| `command` | a command exits 0 | `redis-cli ping` |

**Trap:** "the config file exists" is not a probe. "The port is open" is. A doctor
checks the pulse, not the paperwork.

## 2. Probe — take real vitals, in parallel

Run every probe. Concurrency matters: a serial sweep of 50 components with 5s
timeouts is a 4-minute checkup nobody runs twice. `scripts/probe.py` fans out with
a thread pool and classifies each as `healthy` / `degraded` / `unhealthy` /
`unchecked`.

**The cardinal sin (rubric #1):** never let a status come from anywhere but the
probe. If you can't probe it, its status is `unchecked` — not `ok`. The case study
is a registry that returned `"unchecked": 51` as a hardcoded literal; it had never
probed once. That is malpractice. Adapt the reference prober to your inventory:

```bash
python3 scripts/probe.py --checks my-inventory.json
# or, for the ASMP fleet the case study runs on:
python3 scripts/probe.py --asmp http://127.0.0.1:7700
```

## 3. Chart — usage context (the step everyone skips)

Vitals alone lie by omission. "27 DOWN" is a panic; "26 of those are dormant-by-
design, last used 33 days ago, and the 27th is your database" is a diagnosis. The
difference is the **chart**: per component, *last used* and *how often*.

You almost certainly do not have this data yet, and **you cannot mine it
retroactively from log mtimes** — a daemon writing a heartbeat is activity, not
*usage by a user or caller*. Conflating them is exactly the dishonesty rubric #4
forbids. So build the instrument going forward:

- **Usage ledger.** At each access point (an API gateway, a CLI dispatcher, a job
  runner, an MCP wrapper), append one line: `{component, ts, actor}` to a ledger
  (`usage.jsonl`). The doctor aggregates `last_used` and `used_7d` / `used_30d`.
- **Put it where access happens, not in the prober.** The prober measures
  liveness; the ledger measures use. Different instruments, different locations.
- Until the ledger has data, the chart honestly reads *unknown* — which is correct,
  and better than a proxy that looks precise and is wrong.

**Wiring the feeder — the lesson that costs everyone a day:** you will look for a
single chokepoint to auto-record usage, and on a decentralized stack **there isn't
one.** Services are reached directly by their own clients (HTTP, MCP, other
processes), not through one proxy. A "fleet CLI" that runs remote *commands* is not
a service-*request* proxy — wiring it records almost nothing. So feed the ledger
from the access points that actually exist, cheapest-first:

1. **User-typed CLI usage** — a shell `preexec` hook that fires a fire-and-forget
   `touch` when a known component name is run. This is the *cleanest* signal: a
   human running `knox` unambiguously *used* knox. Start here.
2. **Each service's own inbound middleware** — the service records a `touch` on
   requests it serves. Distributed, but it's the ground truth of use.
3. **MCP / agent wrappers** — record a `touch` when an agent calls the component.

Reference: the ASMP registry grew `POST /services/{name}/touch` → `usage.jsonl`
and `GET /usage` (see `case-studies/asmp.md`). The endpoint is the easy half; the
feeders are the real work, and they only accrue going forward. Say so.

This is the lesson that turns a smoke alarm into a physician.

## 4. Triage — collapse symptoms to root cause

Do not report N failures. Report the *causes*. Cluster the unhealthy set by what
they share:

- **Same host:port** → one dead server, not twelve dead services. (Case study: 12
  Reeves services + caddy all on `:8787` = *one* outage.)
- **Same dependency** → if the DB is down, everything that needs it is a symptom.
- **Same supervisor** → a launchd/systemd target that failed to load takes its
  children with it.

Rank by blast radius and by the chart: a down component that nothing has used in a
month is a footnote; a down component in daily use is the headline.

## 5. Report — say what's true, including what you can't see

Output, in this order:

1. **Headline:** the root causes, fewest words. "One dead server on :8787 took 12
   services with it. Your database is down. Everything else is dormant-by-design."
2. **Roster:** healthy / degraded / unhealthy / unchecked counts, then the roster,
   sorted worst-first.
3. **Blind spots:** what you could not measure and why. If the usage chart is empty
   because the ledger is new, say so. Never launder a guess as a fact.

## Graduation

You have a doctor that works well when, run cold on your stack, it: probes
everything for real (nothing hardcoded), tells dormant from dying using a usage
chart, names root causes instead of symptoms, and states its own blind spots. Grade
yourself with [`the-rounds-rubric`](../the-rounds-rubric/SKILL.md) or `/medschool checkup`.

**Anti-patterns** (each is a real health check that shipped and lied):
- Hardcoded status, or "assume up if I can't reach it."
- Liveness with no usage context → chronic false alarms → alert fatigue → the
  doctor gets muted → the one real outage is missed.
- Reporting 27 red boxes instead of 1 root cause.
- Inferring "last used" from log mtime and presenting it as user activity.
