# Run sheet

For the presenter. Attendee steps are in `README.md`.

---

## Before you start

- [ ] `docker compose down && docker compose up -d && ./seed.sh && ./build-view.sh`
- [ ] Both images already in local Docker cache, nothing pulling
- [ ] `cp mcp-naive.json .mcp.json`
- [ ] Claude Code **fully exited**, so the read cursor starts at TKT-113056
- [ ] Console open at localhost:8090, on the `support_tickets` topic
- [ ] Second tab: `rpk connect mcp-server --address localhost:4195 ./repo`,
      freshly started so its cursor is at the start and its tools match `repo/`
- [ ] Third tab: `source ./mcp-init.sh`
- [ ] `transcripts/long-run.md` open in an editor, ready to show
- [ ] Terminal font large enough to read

**Ground truth: 137, auth_timeout with 61.**

---

## The shape

| | |
|---|---|
| Hook | Ask a question with a checkable answer. It cannot answer. |
| Tension | The tool works. The config is fine. It still cannot answer. |
| Turn | The model diagnoses your tool design for you, out loud. |
| Payoff | Move the work into the stream. One call, eight seconds, 137. |

One line to build toward: **an MCP tool's job is not to give the model
access, it's to give the model an answer.**

---

## Minute by minute

### 0:00 to 1:00 — the haystack

Console on screen, `support_tickets` topic, 50,000 messages. Click into one
record so they see the shape: customer, priority, root_cause, created_at,
and a description body.

Say what the question is and that the answer is checkable.

> "There are 50,000 support tickets in this topic. I want to know how many
> P1s Acme filed in the last week and what caused them. The answer is a
> specific number. I know what it is. Let's see if the agent does."

Do not say 137 yet.

### 1:00 to 2:00 — the tool

Show `repo/resources/inputs/search-tickets.yaml` on screen. Ten lines.

> "This is the tool. It reads tickets from the topic. There is nothing wrong
> with it, and it is the tool I would have written."

### 2:00 to 3:30 — ask it

`claude`, then the question.

Let it run until it answers. In the saved runs it stopped by itself and
refused to give a final number after 1m 8s (3 tool calls,
`transcripts/repeat.md`) and 1m 22s (13 tool calls, `transcripts/partial.md`).
If it asks whether to keep reading, say no.

When it produces the partial answer, read the model's own words aloud. This
is the turn and it needs no narration from you. From the 1m 8s run:

> "The ticket tool has no filters for customer, priority or date. All it
> takes is how many messages to read."

> "It looks like I'm sampling a very large or endless stream, not a fixed
> set of tickets."

**Cut point.** If you are behind, skip straight from here to 5:30.

### 3:30 to 4:30 — ask it again

Same question, same session, verbatim.

It will restate the same unreliable minimum and say running it again will
not change anything. So the agent is now stuck: the tool works, and it
cannot answer.

> "Same question, same session, nothing changed. It cannot get any further."

### 4:30 to 5:30 — what if we let it finish

Show `transcripts/long-run.md`.

4m 2s, 42,675 of 50,000 records read, running count: **116**. It still
called that partial, and a read was still running in the background.

> "The truth is 137. After four minutes it had read 85% of the topic and had
> 116. Close enough to be believable, and still wrong. And it knew that, so
> it wouldn't commit."

### 5:30 to 6:30 — the three failures

Switch to the curl tab. These are deterministic and need no model.

```bash
./call.sh search-tickets '{"count":1000}' | wc -c
```

**Volume.** About 627,000 bytes (it varies by a few hundred per call) for an
answer that is two facts. That is about 2% of the topic. The whole topic is
28.5 MB.

**Coverage.** The topic is shuffled, so 1,000 records is not 1,000 Acme
tickets. To find all 137 it must read all 50,000.

> "The tool offers the model a dial. There is no setting of that dial that
> is correct."

**Hidden state.** Run this twice, point at the first ticket ID:

```bash
./call.sh search-tickets '{"count":5}' | head -c 200
```

Different records, identical call, no error anywhere. The tool holds an open
consumer and every call advances it. Nothing in the schema says so.

### 6:30 to 8:00 — the fix

```bash
cp mcp-fixed.json .mcp.json
```

Show `aggregate.yaml`. Filter, batch, reduce to one object, write to a cache.

```bash
ls -l ./cache
```

The filename **is** the key. `acme:p1:7d`, 263 bytes.

Show `repo/resources/caches/views.yaml`. Eight lines.

> "The stream does the work. The tool returns an answer."

### 8:00 to 9:00 — ask the same question

`claude`, `/mcp` to show the tool swapped, then the identical question.

One call. Eight seconds. 137, auth_timeout at 61.

Nothing about the model changed. Nothing about the prompt changed.

### 9:00 to 10:00 — two things to draw out

**It found the key from the description.** The prompt never mentions
`acme:p1:7d`. The only place that key appears is the example at the end of
the description prose in `views.yaml`.

> "The description is the interface. It's prose, it ships in your config,
> and nobody reviews it."

**It flagged the tradeoff before you could.** Read its caveat aloud:

> "The numbers come from a pre-computed summary (acme:p1:7d) in the tickets
> tool, not from counting the tickets directly. The summary doesn't say when
> it was last updated, so it may be slightly behind."

Then agree with it. A materialized view means deciding the question in
advance. It answers one shape of question well and everything else not at
all. That is a real constraint. Do not pretend otherwise.

Bonus if there is time: the view carries no timestamp, and the fix is one
line. The model wrote your backlog item.

### 10:00 to 11:00 — generalize

| | naive | fixed |
|---|---|---|
| tool calls | 3 | 1 |
| time | 68s | 8s |
| bytes, one call | ~627,000 | 383 |
| answer | "at least 36" | 137 |
| repeatable | no | yes |

The naive column is the 1m 8s run in `transcripts/repeat.md`.

About 1,600x smaller than one partial call. The stored view is 263 bytes,
about 108,000x smaller than the 28.5 MB of data needed to actually be
correct.

Close on the reframe: stop asking "how do I give my agent access to X,"
start asking "what shape should this answer be."

---

## Fallbacks

**No network, or the model is down.** The whole before and after is provable
with curl. `mcp-init.sh` and `call.sh` need no LLM. The model is the
flavour; the byte count is the evidence. Run 5:30 to 6:30 as the spine and
show transcripts for the rest.

**The naive run answers correctly.** Should not happen, but if it does, go
straight to the repeat-question test at 3:30. The cursor drift is
deterministic.

**Cursor already advanced from rehearsal.** The first call will not start at
TKT-113056. Restart Claude Code, and restart the `rpk connect mcp-server` in
the second tab, since it keeps its own cursor. If that fails, full reset.

**Claude Code hangs or a background task is stuck.** `/exit` and restart.
Check no stray `rpk connect` processes are holding a consumer.

**Everything is broken.** Transcripts in `transcripts/`: `partial.md`,
`repeat.md`, `long-run.md`, `fixed.md`. Four saved runs covering the whole
arc.

---

## Traps

- **Do not ask for the top three causes.** Second place is a tie at 23.
- **Do not let the naive run keep reading.** If it offers to continue, say
  no. The saved long run was still reading after four minutes.
- **Do not say 137 before the naive run.** It kills the tension.
- **Do not defend the materialized view.** Agree with the model's caveat.

---

## Deliberately left out

No Bloblang tutorial. No Kafka explanation. No inputs-versus-processors
tour. No auth, no deployment, no comparison against hand-written MCP
servers. One question, two tools, one file each.

---

## Build notes, for the "how I built it" section

**The setup broke three times on my own machine.**

- `rpk container start` failed on its last step because it pulls
  `console:latest` against a v24.3.6 broker. Cluster fine, UI dead.
- Having failed, it never created an rpk profile, so `rpk cluster info` kept
  trying to reach Redpanda Cloud.
- `rpk container purge` then failed with "couldn't parse node ID."

Three failures in a documented one-command setup, on a machine that already
had Docker and rpk. That is the gap between a quickstart and five laptops in
a room, and it is why the attendee path is a pinned `docker-compose.yml`.

**I designed for the wrong failure.** I expected the model to answer wrongly.
It refused instead, tracked its own coverage, and explained what my tool was
missing. The refusal is more persuasive than a hallucination would have
been, because nobody can dismiss it as a bad model or a bad prompt.

**Lint caught a real bug before the demo did.** The `redpanda` input rejects
a config with neither a consumer group nor explicit partitions. Pinning to
`support_tickets:0` avoids committing offsets, which is what makes calls
repeatable after restart.

**Two dead ends in the aggregation.** The first attempt used Bloblang `fold`
and died on null handling. The second relied on whatever batch the fetcher
delivered, producing arrays of one and two records. The fix was an explicit
memory buffer with a 20 second batch policy.

**Details that only show up if you actually run it.** A cache becomes two
tools, so the agent can write to your view. Cache descriptions get wrapped
into "Obtain an item from X," so they have to be noun phrases. Declaring
`properties` removes the default `value` parameter entirely. Tool results
arrive as stringified JSON inside text blocks, so every byte is text
something has to parse. `count` is a floor, not a contract: ask for 500, get
504; ask for 3,000, get 3,024.
