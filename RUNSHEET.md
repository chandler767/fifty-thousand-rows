# Run sheet

## TABS

| Tab | Name | Runs |
|---|---|---|
| A | `claude` | Claude Code, which you screen-share |
| B | `server` | MCP server for curl, left running |
| C | `curl` | `./call.sh` |

Claude Code starts its own MCP server, so tab B is only for curl.

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

**6. Quit every Claude Code session** in this repo, so show step 3 starts at
the beginning of the topic.

**7. Get the screen ready**

- [ ] Share only the terminal and editor windows, never this sheet
- [ ] Notifications off
- [ ] Terminal font large
- [ ] Console open at http://localhost:8090 on `support_tickets`
- [ ] Editor tabs: `search-tickets.yaml`, `long-run.md`, `aggregate.yaml`,
      `views.yaml`
- [ ] Prompt in clipboard

---

## PROMPT (paste the same one every time)

```text
How many P1 tickets did Acme file in the last 7 days, and what was the most common root cause? Use only the tickets MCP tool.
```

## ANSWER

**137 · auth_timeout 61**

Then oom_kill 23 · rate_limit 23 · cert_expiry 16 · bad_deploy 14

---

## AT A GLANCE

| # | Time | Where | Do | Land this |
|---|---|---|---|---|
| 1 | 0:00 | Console | Show 50,000 tickets, ask the question | One simple question, one right answer |
| 2 | 1:00 | Editor | What Redpanda Connect is, `search-tickets.yaml` | This is the reasonable default |
| 3 | 2:00 | Tab A | Naive run, paste prompt | It can't answer, and it says why |
| 4 | 3:30 | Tab A | Paste prompt again | The limit is the tool, not the model |
| 5 | 4:30 | Editor | `transcripts/long-run.md` | More time doesn't fix it |
| 6 | 5:30 | Tab C | Three curl calls | Too big, never complete, not repeatable |
| 7 | 6:30 | Editor | `/exit`, `aggregate.yaml`, `views.yaml` | Move the work to the data |
| 8 | 8:00 | Tab A | Fixed run, paste prompt | Same model, right answer |
| 9 | 9:00 | Talk | Description is the interface, agree with its caveat | Views are a trade-off you own |
| 10 | 10:00 | Talk | Numbers table, close | Ask what shape the answer should be |

Behind schedule? Go from 3 straight to 6.

**Lost your place?** Say the "Land this" line for the step you're on, then
move to the next one.

---

## 1 · THE HAYSTACK · 0:00

**WHERE** Console → `support_tickets` → click one record

**SAY**
> "I'm starting in Redpanda Console, on a topic called `support_tickets`. It
> holds 50,000 support tickets. I'll open one: each ticket has a customer, a
> priority, a root cause and a timestamp.
>
> Here's my question: how many P1 tickets did Acme file in the last seven
> days, and what was the most common root cause? I generated this data, so
> there's one right answer and I know it. Let's see if an agent can find it."

❌ Don't say 137.

---

## 2 · THE TOOL · 1:00

**SAY** before switching
> "To connect an agent to these tickets, I'm using Redpanda Connect. It's a
> stream processor: you write a YAML file that says where data comes from,
> what to do with it, and where it goes. It can also run as an MCP server, so
> any component you mark for MCP becomes a tool. So the same thing that hands
> the agent data can also process that data first, and that matters later."

**WHERE** Editor → `repo/resources/inputs/search-tickets.yaml`

**SAY**
> "I'm opening the tool. This is all of it: an input that reads the topic,
> plus a `meta` block that makes it an MCP tool with a description. The only
> thing the model can choose is how many tickets to read. It can't filter.
> There's nothing wrong with it, and it's the tool I'd write first."

---

## 3 · ASK IT · 2:00

**TAB A**
```bash
claude --strict-mcp-config --mcp-config mcp-naive.json
```

**SAY**
> "I'm starting Claude Code with only this tool, and pasting the question."

**PASTE** the prompt

**EXPECT** about 1 minute, a few tool calls, no final number, "at least N"

**SAY** while it runs
> "It's reading a batch and counting Acme P1s. Now it's asking for a bigger
> batch, and the count keeps going up."

**WHEN IT ANSWERS** read its words about the tool aloud, then:
> "It didn't guess. It says the tool can't filter and it can't tell when it
> has reached the end."

**IF** it asks to keep reading → type `no`

**IF** it's still going at 2 min → `Esc`, "It has no way to finish," go to 5

---

## 4 · ASK AGAIN · 3:30

**TAB A** same session

**SAY**
> "I'm asking the exact same question again, in the same session."

**PASTE** the prompt

**EXPECT** the same minimum, and "re-running won't change it"

**SAY**
> "Same answer, and it says reading again won't help. The model is fine. The
> tool is the problem."

---

## 5 · LET IT FINISH? · 4:30

**WHERE** Editor → `transcripts/long-run.md`

**POINT AT** `4m 2s` · `42,675` read · `116`

**SAY**
> "You might think I stopped it too early. This is a run where I let it keep
> going. It took four minutes and read 42,675 tickets, about 85% of the
> topic. It found 116. That's wrong, and because the count was still
> climbing, it wouldn't commit to it."

❌ Don't say 137.

---

## 6 · THREE FAILURES · 5:30

**TAB C** · Volume

**SAY**
> "Now I'm calling the tool straight from the terminal, with no model
> involved. I'm asking for 1,000 tickets and counting the bytes."

```bash
./call.sh search-tickets '{"count":1000}' | wc -c
```

**EXPECT** about 627,000

**SAY**
> "That's 627 KB going into the model's context to get two facts, and it's
> only 2% of the topic."

**SAY** · Coverage
> "The tickets are shuffled, so the only batch size that catches every
> ticket is all 50,000, and that won't fit."

**TAB C** · Hidden state (run it TWICE)

**SAY**
> "I'm running the same five-ticket call twice."

```bash
./call.sh search-tickets '{"count":5}' | head -c 200
```

**POINT AT** the first ticket ID, which differs between the two runs

**SAY**
> "The first ID is different each time, and there's no error. Every call
> moves a hidden read position, so a retry reads new data. So the tool
> returns too much, can never be complete, and can't be repeated."

---

## 7 · THE FIX · 6:30

**TAB A** `/exit`

**WHERE** Editor → `aggregate.yaml`

**SAY**
> "I'm closing that session. The fix is to do the counting in Redpanda
> Connect before the model gets involved. This pipeline reads the same topic
> and keeps only Acme P1s from the last seven days. It counts them by root
> cause and writes one small summary to a cache."

**TAB C**
```bash
ls -l ./cache
```

**POINT AT** `acme:p1:7d` · 263 bytes

**SAY**
> "I'm listing the cache folder. It has one file of 263 bytes, and the
> filename is the key."

**WHERE** Editor → `repo/resources/caches/views.yaml`

**SAY**
> "This is the new tool: that cache with MCP turned on, in eight lines. It
> returns the answer, not the data."

---

## 8 · ASK AGAIN, FIXED · 8:00

**TAB A**
```bash
claude --strict-mcp-config --mcp-config mcp-fixed.json
```

**DO** `/mcp` → show `get-views` → `Esc`

**SAY**
> "I'm starting Claude Code again with the new tool and the same model. In
> `/mcp` you can see it has `get-views` now. I'm pasting the same question."

**PASTE** the prompt

**EXPECT** 1 call · about 8s · **137 · auth_timeout 61**

**SAY**
> "It made one call and took about eight seconds: 137 tickets, and
> auth_timeout with 61. That's the right answer."

**IF** it can't find the view → `./build-view.sh` in tab C, then ask again

---

## 9 · TWO POINTS · 9:00

**WHERE** Editor → `views.yaml`, point at the description

**SAY**
> "The prompt never mentioned the key `acme:p1:7d`. The model got it from
> this description. That sentence is the interface, and nobody reviews it,
> so treat it like API docs."

**DO** point at the last line of the fixed answer

**SAY**
> "It also warns that the summary has no timestamp, so it may be out of date.
> That's fair. A view means you decide the question ahead of time and keep
> it fresh."

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
> "Both runs used the same model. The first tool took three calls and over a
> minute, sent 627 KB, and got to 'at least 36'. The second took one call and
> eight seconds, sent 383 bytes, and got 137.
>
> So don't ask how to give your agent access to your data. Ask what shape
> the answer should be, and build that. It's all in the repo. Questions?"

---

## ❌ DON'T

- Change the prompt. Asking for the top three causes creates a tie at 23.
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
| Everything is broken | Rerun setup steps 1, 3 and 4 (about 30s) |

---

## Q&A: how I built it

**"Isn't the date hardcoded?"** Yes. `aggregate.yaml` filters on a fixed date
so the demo is repeatable. In production you'd run it continuously with a
windowed aggregation, so the view keeps updating as tickets arrive.

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
