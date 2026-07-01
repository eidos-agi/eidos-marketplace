#!/usr/bin/env python3
"""Eidos Medical School — reference prober.

The worked example, not the product. It takes REAL vitals for a list of
components and classifies each healthy/degraded/unhealthy/unchecked. Students
adapt the inventory to their own stack. stdlib only; parallel.

Rubric #1 (vitals that don't lie): a component with no probe method is reported
`unchecked`, never `ok`. Nothing here is ever hardcoded to a status.

Inventory formats:
  --checks FILE   JSON list of {"name","method","target"}
                  method ∈ http | tcp | launchctl | systemd | pid | command
  --asmp URL      pull an ASMP registry's /services and read each manifest's
                  health block (the founding case study's fleet)

Usage:
  python3 probe.py --checks inventory.json
  python3 probe.py --asmp http://127.0.0.1:7700
  python3 probe.py --selftest        # rubric-guard: prove we never fake a status
"""
import argparse, json, shlex, socket, subprocess, sys, urllib.request, urllib.error
import concurrent.futures as cf

TIMEOUT = 5

def probe(c):
    """c: {name, method, target} -> (name, status, detail). Pure of any default 'ok'."""
    name = c.get("name", "?")
    method = c.get("method")
    target = c.get("target", "")
    if not method:
        return name, "unchecked", "no probe method"
    try:
        if method == "http":
            try:
                with urllib.request.urlopen(urllib.request.Request(target, method="GET"), timeout=TIMEOUT) as r:
                    return name, "healthy", f"http {r.status}"
            except urllib.error.HTTPError as e:
                return name, "healthy", f"http {e.code} (server answered)"
        if method == "tcp":
            host, port = target.rsplit(":", 1)
            with socket.create_connection((host, int(port)), timeout=TIMEOUT):
                return name, "healthy", f"tcp {port} open"
        if method in ("launchctl", "systemd"):
            return _svc(name, method, target)
        if method == "pid":
            r = subprocess.run(["pgrep", "-f", target], capture_output=True, text=True, timeout=TIMEOUT)
            return (name, "healthy", f"pid {r.stdout.split()[0]}") if r.returncode == 0 else (name, "unhealthy", "no process")
        if method == "command":
            # ponytail: shlex.split, no shell — a health probe is a simple argv
            # (`redis-cli ping`). Need a pipe? put `sh -c "..."` in your inventory explicitly.
            r = subprocess.run(shlex.split(target), capture_output=True, text=True, timeout=TIMEOUT)
            return (name, "healthy", "exit 0") if r.returncode == 0 else (name, "unhealthy", f"exit {r.returncode}")
        return name, "unchecked", f"unknown method {method}"
    except Exception as e:
        return name, "unhealthy", f"{type(e).__name__}: {e}"

def _svc(name, method, target):
    if method == "launchctl":
        r = subprocess.run(["launchctl", "list", target], capture_output=True, text=True, timeout=TIMEOUT)
        if r.returncode != 0:
            return name, "unhealthy", "not loaded"
        pid = next((l.split("=")[1].strip().rstrip(";").strip()
                    for l in r.stdout.splitlines() if '"PID"' in l), None)
        return (name, "healthy", f"pid {pid}") if pid and pid != "0" else (name, "degraded", "loaded, no PID")
    # systemd
    r = subprocess.run(["systemctl", "is-active", target], capture_output=True, text=True, timeout=TIMEOUT)
    s = r.stdout.strip()
    return {"active": (name, "healthy", "active"),
            "activating": (name, "degraded", "activating")}.get(s, (name, "unhealthy", s or "inactive"))

def from_asmp(url):
    with urllib.request.urlopen(url.rstrip("/") + "/services", timeout=TIMEOUT) as r:
        services = json.load(r)
    checks = []
    for m in services:
        h = m.get("health") or {}
        checks.append({"name": m.get("name"), "method": h.get("method"), "target": h.get("target")})
    return checks

def run(checks):
    with cf.ThreadPoolExecutor(max_workers=16) as ex:
        results = list(ex.map(probe, checks))
    order = {"unhealthy": 0, "degraded": 1, "healthy": 2, "unchecked": 3}
    results.sort(key=lambda r: (order.get(r[1], 9), r[0]))
    return results

def report(results):
    from collections import Counter
    c = Counter(s for _, s, _ in results)
    print(f"total={len(results)}  " + "  ".join(f"{k}={c[k]}" for k in ("healthy", "degraded", "unhealthy", "unchecked") if c[k]))
    print("-" * 60)
    mark = {"healthy": "OK  ", "degraded": "WARN", "unhealthy": "DOWN", "unchecked": "--- "}
    for name, status, detail in results:
        print(f"{mark[status]} {name:26} {detail}")
    return c

def selftest():
    # Rubric-guard: an entry with no method must come back `unchecked`, never `ok`/`healthy`.
    _, s, _ = probe({"name": "x", "method": None})
    assert s == "unchecked", f"fabricated status for unprobeable component: {s}"
    # A refused tcp port must be unhealthy, not silently healthy.
    _, s, _ = probe({"name": "y", "method": "tcp", "target": "127.0.0.1:1"})
    assert s == "unhealthy", f"dead port reported as {s}"
    print("selftest ok: no fabricated statuses")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checks")
    ap.add_argument("--asmp")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.asmp:
        checks = from_asmp(a.asmp)
    elif a.checks:
        checks = json.load(open(a.checks))
    else:
        ap.error("need --checks FILE, --asmp URL, or --selftest")
    c = report(run(checks))
    # exit non-zero if anything is actually down — usable in a cron/rounds gate
    sys.exit(1 if c["unhealthy"] else 0)

if __name__ == "__main__":
    main()
