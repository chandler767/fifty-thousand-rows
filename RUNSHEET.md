# Run sheet

Setup is at the bottom. Do it 15 minutes before you go live.

## PROMPT (paste the same one every time)

```text
How many P1 tickets did Acme file in the last 7 days, and what was the most common root cause? Use only the tickets MCP tool.
```

## ANSWER

**137 · auth_timeout 61**

Then oom_kill 23 · rate_limit 23 · cert_expiry 16 · bad_deploy 14

## TABS

| Tab | Name | Runs |
|---|---|---|
| A | `claude` | Claude Code, which you screen-share |
| B | `server` | MCP server for curl, left running |
| C | `curl` | `./call.sh` |

Claude Code starts its own MCP server, so tab B is only for curl.

---

## AT A GLANCE

| # | Time | Where | Do |
|---|---|---|---|
| 1 | 0:00 | Console | Show 50,000 tickets, ask the question out loud |
| 2 | 1:00 | Editor | `search-tickets.yaml` |
| 3 | 2:00 | Tab A | Naive run, paste prompt |
| 4 | 3:30 | Tab A | Paste prompt again |
| 5 | 4:30 | Editor | `transcripts/long-run.md` |
| 6 | 5:30 | Tab C | Three curl calls |
| 7 | 6:30 | Editor | `/exit`, `aggregate.yaml`, `views.yaml` |
| 8 | 8:00 | Tab A | Fixed run, paste prompt |
| 9 | 9:00 | Talk | Description is the interface, agree with its caveat |
| 10 | 10:00 | Talk | Numbers table, close |

Behind schedule? Go from 3 straight to 6.

---

## 1 · THE HAYSTACK · 0:00

**WHERE** Console → `support_tickets` → click one record

**SAY**
> "50,000 tickets. How many P1s did Acme file in the last seven days, and
> what's the most common cause? There's one right answer, and I know it."

❌ Don't say 137.

---

## 2 · THE TOOL · 1:00

**WHERE** Editor → `repo/resources/inputs/search-tickets.yaml`

**SAY**
> "Ten lines. Nothing wrong with it. It's the tool I would have written."

---

## 3 · ASK IT · 2:00

**TAB A**
```bash
claude --strict-mcp-config --mcp-config mcp-naive.json
```

**PASTE** the prompt

**EXPECT** about 1 minute, a few tool calls, no final number, "at least N"

**SAY** nothing. Read its words about the tool aloud.

**IF** it asks to keep reading → type `no`

**IF** it's still going at 2 min → `Esc`, "it has no way to finish", go to 5

---

## 4 · ASK AGAIN · 3:30

**TAB A** same session

**PASTE** the prompt

**EXPECT** the same minimum, and "re-running won't change it"

**SAY**
> "Same question, nothing changed. It can't get any further."

---

## 5 · LET IT FINISH? · 4:30

**WHERE** Editor → `transcripts/long-run.md`

**POINT AT** `4m 2s` · `42,675` read · `116`

**SAY**
> "The truth is 137. After four minutes and 85% of the topic it had 116.
> Believable, and wrong. It knew that, so it wouldn't commit."

---

## 6 · THREE FAILURES · 5:30

**TAB C** · Volume

```bash
./call.sh search-tickets '{"count":1000}' | wc -c
```

**EXPECT** about 627,000

**SAY**
> "627 KB for two facts, and that's 2% of the topic."

**SAY** · Coverage
> "It's shuffled. Finding all 137 means reading all 50,000. No setting of
> that dial is correct."

**TAB C** · Hidden state (run it TWICE)

```bash
./call.sh search-tickets '{"count":5}' | head -c 200
```

**POINT AT** the first ticket ID, which differs between the two runs

**SAY**
> "Same call, different records, no error. Every call moves a hidden
> cursor."

---

## 7 · THE FIX · 6:30

**TAB A** `/exit`

**WHERE** Editor → `aggregate.yaml`

**SAY**
> "Filter, reduce to one object, write it to a cache. The stream does the
> work."

**TAB C**
```bash
ls -l ./cache
```

**POINT AT** `acme:p1:7d` · 263 bytes

**SAY**
> "The filename is the key."

**WHERE** Editor → `repo/resources/caches/views.yaml`

**SAY**
> "Eight lines. The tool returns an answer."

---

## 8 · ASK AGAIN, FIXED · 8:00

**TAB A**
```bash
claude --strict-mcp-config --mcp-config mcp-fixed.json
```

**DO** `/mcp` → show `get-views` → `Esc`

**PASTE** the prompt

**EXPECT** 1 call · about 8s · **137 · auth_timeout 61**

**SAY**
> "Same model. Same prompt. One call, eight seconds, right answer."

**IF** it can't find the view → `./build-view.sh` in tab C, then ask again

---

## 9 · TWO POINTS · 9:00

**Key from the description.** The prompt never says `acme:p1:7d`. The key
only appears in the `views.yaml` description.
> "The description is the interface. It's prose, and nobody reviews it."

**Its caveat.** Read it aloud: it's a pre-computed summary with no
timestamp, so it may be behind.
> "It's right. A view means deciding the question in advance."

Extra, if there's time: adding a timestamp is a one-line fix. "The model
wrote your backlog item."

---

## 10 · CLOSE · 10:00

| | naive | fixed |
|---|---|---|
| tool calls | 3 | 1 |
| time | 68s | 8s |
| bytes | ~627,000 | 383 |
| answer | "at least 36" | 137 |
| repeatable | no | yes |

**SAY**
> "Don't ask how to give your agent access to X. Ask what shape the answer
> should be."

---

## ❌ DON'T

- Change the prompt. Top three causes means a tie at 23.
- Let the naive run keep reading.
- Say 137 before step 8.
- Defend the view. Agree with the caveat.

---

## IF IT BREAKS

| Symptom | Fix |
|---|---|
| Naive run gets 137 | "It read the repo, which is its own lesson." Go to 4. |
| Naive run hangs | `Esc` → go to 5 |
| `call.sh` prints nothing | Tab B is down. Restart it, then `source ./mcp-init.sh` in tab C. |
| Curl cursor already moved | `Ctrl-C` tab B, restart it, re-source tab C |
| `/mcp` shows Gmail or Drive | You forgot `--strict-mcp-config`. `/exit` and relaunch. |
| Fixed run can't find the view | `./build-view.sh`, then ask again |
| Model is down | Run step 6 live, and show `transcripts/` for the rest |
| Everything is broken | Full reset below (30s), restart tab B, re-source tab C |

---

## BEFORE YOU GO LIVE (T-15 min)

**1. Reset** in tab C, then expect `"ticket_count":137`

```bash
docker compose down && docker compose up -d && ./seed.sh && ./build-view.sh
```

**2. Check the view**, then expect `acme:p1:7d` at 263 bytes

```bash
ls -l ./cache
```

**3. Start the server** in tab B and leave it running

```bash
rpk connect mcp-server --address localhost:4195 ./repo
```

**4. Open a curl session** in tab C, then expect `session: <id>`

```bash
source ./mcp-init.sh
```

**5. Rehearse the launch** in tab A. `/mcp` should show only `tickets`.
Then `/exit`.

```bash
claude --strict-mcp-config --mcp-config mcp-naive.json
```

**6. Quit every Claude Code session** in this repo, so step 3 starts at the
beginning of the topic.

**7. Get the screen ready**

- [ ] Share only the terminal and editor windows, never this sheet
- [ ] Notifications off
- [ ] Terminal font large
- [ ] Console open at http://localhost:8090 on `support_tickets`
- [ ] Editor tabs: `search-tickets.yaml`, `long-run.md`, `aggregate.yaml`,
      `views.yaml`
- [ ] Prompt in clipboard

---

## Q&A: how I built it

**Setup broke three times on my machine.** `rpk container start` pulled
`console:latest` against a v24.3.6 broker, so the UI was dead. It never made
an rpk profile, so `rpk cluster info` kept trying to reach Redpanda Cloud.
Then `rpk container purge` failed with "couldn't parse node ID." That's why
attendees get a pinned `docker-compose.yml`.

**I designed for the wrong failure.** I expected a wrong answer. Instead it
refused, tracked how much it had read, and explained what the tool was
missing. That's more persuasive, because nobody can blame a bad model or a
bad prompt.

**Lint caught a real bug.** The `redpanda` input needs a consumer group or
explicit partitions. Pinning `support_tickets:0` means no offsets get
committed, so calls repeat after a restart.

**Two dead ends in the aggregation.** Bloblang `fold` failed on nulls. Then
the fetcher's own batches produced arrays of one or two records. The fix was
a memory buffer with a 20-second batch policy.

**Details you only find by running it.**

- A cache becomes two tools, so the agent can write to your view.
- Cache descriptions get wrapped into "Obtain an item from X," so write them
  as noun phrases.
- Declaring `properties` removes the default `value` parameter.
- Tool results are stringified JSON inside text blocks.
- `count` is a minimum: ask for 500 and you get 504; ask for 3,000 and you
  get 3,024.
