import json, random, datetime as dt

random.seed(42)

CUSTOMERS = ["Acme", "Globex", "Initech", "Umbrella", "Soylent", "Hooli"]
CAUSES = ["auth_timeout", "rate_limit", "disk_full", "cert_expiry",
          "bad_deploy", "network_partition", "oom_kill"]
NOW = dt.datetime(2026, 9, 15, 12, 0, 0)

def body(cause):
    return (f"Customer reports intermittent failures traced to {cause}. "
            "Support collected logs from the affected region and confirmed the "
            "pattern reproduces under load. Escalated to the platform team for "
            "triage. Customer impact is limited to a subset of API clients but "
            "has been ongoing across multiple sessions. Awaiting root cause "
            "confirmation before closing this issue out.")

def ticket(i, customer, priority, cause, days_ago):
    created = NOW - dt.timedelta(days=days_ago, hours=random.randint(0, 23))
    return {
        "id": f"TKT-{100000+i}",
        "customer": customer,
        "priority": priority,
        "root_cause": cause,
        "created_at": created.isoformat() + "Z",
        "subject": f"{cause} affecting {customer} API clients",
        "description": body(cause),
    }

rows, i = [], 0

# Ground truth: exactly 137 Acme P1s in the last 7 days
for n in range(137):
    cause = "auth_timeout" if n < 61 else random.choice(
        ["rate_limit", "cert_expiry", "bad_deploy", "oom_kill"])
    rows.append(ticket(i, "Acme", "P1", cause, random.randint(0, 6))); i += 1

# Decoy: Acme P2s in window, mostly auth_timeout
for n in range(900):
    rows.append(ticket(i, "Acme", "P2", random.choice(
        ["auth_timeout"]*5 + CAUSES), random.randint(0, 6))); i += 1

# Decoy: Acme P1s outside the window
for n in range(700):
    rows.append(ticket(i, "Acme", "P1", random.choice(CAUSES),
                       random.randint(8, 120))); i += 1

# Decoy: other customers, including heavy P1 volume
while i < 50000:
    rows.append(ticket(i, random.choice(CUSTOMERS[1:]),
                       random.choice(["P1", "P2", "P3"]),
                       random.choice(CAUSES), random.randint(0, 120))); i += 1

random.shuffle(rows)
with open("tickets.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")

print(f"wrote {len(rows)} tickets")
print("GROUND TRUTH: Acme P1 last 7 days = 137, top cause = auth_timeout (61)")
