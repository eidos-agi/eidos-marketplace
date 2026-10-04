#!/usr/bin/env python3
"""Grok Canopy tree check. Parent pointer only. Does not score and does not enforce."""
import json
import sys
from pathlib import Path

AGENTS = Path("/home/box/agent-data/agents")
ROUTER = "Grok Bot"
MAX_DEPTH = 4

PARENT = {
    "GrokBotBot": ROUTER,
    "Reeves": ROUTER,
    "KaiEngineering": ROUTER,
    "EidosInfra": ROUTER,
    "EidosDocs": ROUTER,
    "EidosDNSAndCloudflare": ROUTER,
    "EidosFinance": ROUTER,
    "EidosEmail": ROUTER,
    "Prims": ROUTER,
    "KnoxDrive": ROUTER,
    "KidsBot": ROUTER,
    "Kai": ROUTER,
    "DanBoone": ROUTER,
    "AICEmail": ROUTER,
    "AISEE": ROUTER,
    "GrokTuah": "GrokBotBot",
    "Tokut": "GrokBotBot",
    "TokutOptimizer": "GrokBotBot",
    "MeridianBot": "GrokBotBot",
    "ReevesInfra": "Reeves",
    "ReevesEmailBot": "Reeves",
    "ReevesMacbook": "Reeves",
    "239Eagle": "Reeves",
    "HealthBot": "Reeves",
    "ApartmentBot": "Reeves",
    "Omni": "Reeves",
    "ReevesFinance": "Reeves",
    "ReevesFinanceMercuryBot": "ReevesFinance",
    "PlaidBot": "ReevesFinance",
    "SubscriptionsBooneVoyageBot": "ReevesFinance",
    "CrunchBot": "ReevesFinance",
    "ReevesCreekside": "ReevesFinance",
    "ExpenseBot": "ReevesFinance",
    "Volta": "KaiEngineering",
    "Eidos Browsing Grok Plugin": "KaiEngineering",
    "EidosFinanceMercuryBot": "EidosFinance",
    "SubscriptionsEidosBot": "EidosFinance",
    "PrimsBrowsers": "Prims",
    "PrimsDesktop": "Prims",
    "PrimsDrive": "Prims",
    "ProductBot": "Prims",
    "Fort Knox": "KnoxDrive",
    "GrokKnox": "KnoxDrive",
    "Hancock": "KnoxDrive",
    "1PasswordBot": "KnoxDrive",
    "WyattBot": "KidsBot",
    "ColleenBot": "KidsBot",
    "TaylorBot": "KidsBot",
    "BooneFinanceMercuryBot": "DanBoone",
    "CalendarAndTaskBot": "Reeves",
    "CorrespondenceBot": "Reeves",
    "EmailBot": "Reeves",
    "JevmailBot": "Reeves",
    "SpamBot": "Reeves",
    "PhotosBot": "Reeves",
    "Rolodex": "Reeves",
    "LinkedInBot": "Reeves",
    "Overheard": "Reeves",
    "TravelBot": "Reeves",
    "TahoeBot": "Reeves",
    "TVBot": "Reeves",
    "TVForEmilyBot": "Reeves",
    "BirthdayBot": "Reeves",
    "ScannerBot": "Reeves",
    "ShanklinFamilyTrustBot": "Reeves",
    "JoanneBot": "Reeves",
    "ZiggyBot": "Reeves",
    "EmilyRothrockBot": "Reeves",
    "SaraVinsonBot": "Reeves",
    "JoshBot": "Reeves",
    "TimOConnorBot": "Reeves",
    "AlhanaBot": "Reeves",
    "Colin Christian Bot": "Reeves",
    "EJ Bartolomei Bot": "Reeves",
    "JacobBarefootBot": "Reeves",
    "JeffBurrowsBot": "Reeves",
    "MichaelShanklinBot": "Reeves",
    "AdrienBot": "Reeves",
    "PotBellyBot": "Reeves",
    "WebinarBot": "Reeves",
    "HondaPilotBot": "KidsBot",
    "SubscriptionsBot": "ReevesFinance",
    "PavoBot": "Prims",
    "BrowserOSBot": "Prims",
    "Browsers": "Prims",
    "BackupBot": "Prims",
    "MFilesBot": "Prims",
    "IdentityBot": "KnoxDrive",
    "dr eggbot": "GrokBotBot",
    "GrokGoals": "GrokBotBot",
    "DeepSeekHarnessBot": "GrokBotBot",
    "DeepSeekResearch": "GrokBotBot",
    "DesignBot": "GrokBotBot",
    "ChatGPTBot": "GrokBotBot",
    "CockpitBot": "GrokBotBot",
    "New Agent": "GrokBotBot",
    "AAD": "KaiEngineering",
    "ASMPBot": "KaiEngineering",
    "AWSBot": "KaiEngineering",
    "Arparp": "KaiEngineering",
    "Cerebroski": "KaiEngineering",
    "DockerBot": "KaiEngineering",
    "EAM (Eidos Agent Manager)": "KaiEngineering",
    "EmuxBot": "KaiEngineering",
    "EmuxBot, ShowMeee": "KaiEngineering",
    "PaseoBot": "KaiEngineering",
    "JevBrowsing": "KaiEngineering",
    "JevDesktopBot": "KaiEngineering",
    "ManyHatsBot": "KaiEngineering",
    "MockupBot": "KaiEngineering",
    "QA bot": "KaiEngineering",
    "RentAMacBot": "KaiEngineering",
    "TestingBot": "KaiEngineering",
    "AICDirectorData": "KaiEngineering",
    "Eidos Brand": "KaiEngineering",
    "Eidos Company": "KaiEngineering",
    "Eidos3D": "KaiEngineering",
    "EidosDeck": "KaiEngineering",
    "FleetBot": "KaiEngineering",
    "Ollie": "KaiEngineering",
    "RheaAIIncorporatedBot": "KaiEngineering",
    "GrokBotBot, Fort Knox": "KnoxDrive",
    "ReevesClaw, Reeves, 239Eagle": "Reeves",
}

# Parents I will not defend. Still assigned so the count can close.
UNCLEAN = {
    "AICDirectorData": "no AIC chief; hung on KaiEngineering",
    "AISEE": "AIC plane, not Eidos engineering",
    "Eidos Brand": "brand, not engineering",
    "Eidos Company": "empty company bucket",
    "Eidos3D": "product, not engineering",
    "EidosDeck": "product, not engineering",
    "FleetBot": "product, not engineering",
    "Ollie": "OurOtters product, not engineering",
    "RheaAIIncorporatedBot": "empty company name",
    "SubscriptionsBot": "blurb says it teaches both subscription leaves; they stay on the money chiefs",
    "IdentityBot": "empty; secrets is a guess",
    "MFilesBot": "empty",
    "Browsers": "empty",
    "BackupBot": "empty",
    "New Agent": "empty placeholder",
    "GrokBotBot, Fort Knox": "room, not a bot",
    "ReevesClaw, Reeves, 239Eagle": "room, not a bot",
    "EmuxBot, ShowMeee": "room, not a bot",
    "AdrienBot": "empty person",
    "JacobBarefootBot": "empty person",
    "JeffBurrowsBot": "empty person",
    "PotBellyBot": "empty",
    "WebinarBot": "empty",
    "TravelBot": "empty",
    "BirthdayBot": "empty",
    "ScannerBot": "empty",
    "ChatGPTBot": "empty",
    "CockpitBot": "empty",
    "DockerBot": "empty",
    "AWSBot": "empty",
    "ASMPBot": "empty",
}


def load():
    by_name = {}
    for d in AGENTS.iterdir():
        p = d / "profile.json"
        if not p.exists():
            continue
        j = json.loads(p.read_text())
        name = j.get("name") or ""
        if not name or ", Daniel" in name:
            continue
        # Misnamed group, not a bot. Dropped from the tree; not deleted.
        if d.name == "a7c47812-d10f-4569-824d-7205d3dc4e8a":
            continue
        by_name[name] = d.name
    return by_name


def children(name):
    return [n for n, p in PARENT.items() if p == name]


def role(name):
    if name == ROUTER:
        return "router"
    if children(name):
        return "chief"
    if name in PARENT:
        return "leaf"
    return "unassigned"


def depth(name, seen=None):
    seen = seen or []
    if name in seen:
        raise SystemExit("cycle: " + " -> ".join(seen + [name]))
    parent = PARENT.get(name)
    if not parent:
        return 0
    return 1 + depth(parent, seen + [name])


def may_wake(src, dst):
    if src == dst:
        return False
    if src == ROUTER:
        return dst in PARENT
    if role(src) == "unassigned":
        return dst == ROUTER
    if dst == PARENT.get(src):
        return True
    if role(src) == "chief" and PARENT.get(dst) == src:
        return True
    return False


def main():
    by_name = load()
    missing = [n for n in list(PARENT) + [ROUTER] if n not in by_name]
    extra = sorted(n for n in by_name if n != ROUTER and n not in PARENT)
    if missing or extra:
        print("MISSING", missing)
        print("UNASSIGNED", extra)
        sys.exit(1)

    # (1) original wake cases
    cases = [
        ("WyattBot", "KidsBot", True),
        ("WyattBot", "ColleenBot", False),
        ("WyattBot", "Reeves", False),
        ("KidsBot", "WyattBot", True),
        ("KidsBot", ROUTER, True),
        ("Volta", "KaiEngineering", True),
        ("Volta", "Prims", False),
        ("ReevesFinanceMercuryBot", "Reeves", False),
        ("ReevesFinance", "ReevesFinanceMercuryBot", True),
        (ROUTER, "Reeves", True),
        ("Tokut", "CorrespondenceBot", False),
    ]
    wake_fail = [f"{a} -> {b} got {may_wake(a,b)} want {c}" for a, b, c in cases if may_wake(a, b) != c]

    # (2) exactly one parent except router
    parent_fail = []
    for name in by_name:
        if name == ROUTER:
            if name in PARENT:
                parent_fail.append("router has a parent")
            continue
        if name not in PARENT or not PARENT[name]:
            parent_fail.append(name)

    # (3) nested chiefs are allowed. Record them; do not fail.
    nested = []
    for name in list(by_name):
        if role(name) != "chief":
            continue
        parent = PARENT.get(name)
        if parent and parent != ROUTER and role(parent) == "chief":
            nested.append(f"{name} under {parent}")
    chief_fail = []

    depths = {n: depth(n) for n in by_name}
    too_deep = [f"{n} {d}" for n, d in depths.items() if d > MAX_DEPTH]

    chiefs = sorted(n for n in by_name if role(n) == "chief")
    leaves = sorted(n for n in by_name if role(n) == "leaf")
    print(f"bots {len(by_name)}")
    print(f"chiefs {len(chiefs)}: {', '.join(chiefs)}")
    print(f"leaves {len(leaves)}")
    print(f"max depth {max(depths.values())}")
    print("check1 wake", "PASS" if not wake_fail else "FAIL " + "; ".join(wake_fail))
    print("check2 one parent", "PASS" if not parent_fail else "FAIL")
    print("check3 nested chiefs allowed", "PASS", "; ".join(nested) or "none")
    print("depth", "PASS" if not too_deep else "FAIL " + "; ".join(too_deep))
    print(f"unclean {len(UNCLEAN)}")
    for n, why in sorted(UNCLEAN.items()):
        print(f"  {n}: {why} -> {PARENT.get(n)}")
    ok = not (wake_fail or parent_fail or chief_fail or too_deep)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
