# Your agent's tool returns 50,000 rows

A hands-on workshop on why MCP tools should return answers, not data.

You will give an AI agent access to 50,000 support tickets, watch a capable
model fail to answer a simple question about them, and then fix it by
changing where the work happens.

Everything runs locally. No API keys, nothing paid.

---

## Requirements

- Docker
- `rpk` with Redpanda Connect 4.56 or newer (`rpk connect --version`)
- Python 3
- `curl` and `jq`
- Claude Code, or any MCP client

## Setup

Three commands, about three minutes.

```bash
docker compose up -d
./seed.sh
./build-view.sh
```

You should see:

```
wrote 50000 tickets
GROUND TRUTH: Acme P1 last 7 days = 137, top cause = auth_timeout (61)
seeded 50000 tickets
```

```
building view, takes about 25s...
{"customer":"Acme","priority":"P1","ticket_count":137,...}
```

Check the data landed:

```bash
rpk topic describe support_tickets -p
```

`HIGH-WATERMARK` should read 50000.

Redpanda Console is at http://localhost:8090 if you want to browse the
tickets.

---

## The question

Everything in this workshop comes back to one question:

```
How many P1 tickets did Acme file in the last 7 days,
and what was the most common root cause?
```

The correct answer is **137 tickets**, most commonly caused by
**auth_timeout**, with 61.

You can check that yourself at any time:

```bash
jq -s '[.[] | select(.customer=="Acme" and .priority=="P1" and .created_at > "2026-09-08")] | length' tickets.jsonl
```

---

## Part one: the obvious tool

Point your MCP client at the first tool and start it:

```bash
cp mcp-naive.json .mcp.json
claude
```

Run `/mcp`. You should see one tool, `search-tickets`.

Open `repo/resources/inputs/search-tickets.yaml`. It is ten lines. It
reads tickets from the topic and hands them to the model. This is the tool
most people write first.

**Now ask the question.**

Let it run. Watch what it does and how long it takes.

Then ask the exact same question a second time, in the same session.

### What to look for

- How many tool calls does it make?
- What number does it settle on, and does it trust it?
- Does the second answer match the first?
- What does it say about the tool itself?

### Poke at the tool directly

In a second terminal:

```bash
rpk connect mcp-server --address localhost:4195 ./repo
```

In a third:

```bash
source ./mcp-init.sh
./call.sh search-tickets '{"count":1000}' | wc -c
```

Then run this twice and compare the first ticket ID each time:

```bash
./call.sh search-tickets '{"count":5}' | head -c 200
```

---

## Part two: the fixed tool

```bash
cp mcp-fixed.json .mcp.json
claude
```

Run `/mcp`. Now you have `get-views` and `set-views` instead of
`search-tickets`.

Ask the identical question.

### What changed

Nothing about the model or the prompt. The work moved.

`aggregate.yaml` is a pipeline that reads the topic, filters to the tickets
that matter, and reduces them to a single summary object stored under the key
`acme:p1:7d`:

```bash
ls -l ./cache
cat ./cache/*
```

`repo/resources/caches/views.yaml` exposes that as a tool. Eight lines.

Measure it:

```bash
./call.sh get-views '{"key":"acme:p1:7d"}' | wc -c
```

Compare with the number from part one.

---

## Things to try

- Change the tool description in `views.yaml` and see whether the model can
  still find the right key.
- Add a second view for a different customer or window, and see whether the
  model picks the right one.
- Add `root.generated_at = now()` to the final mapping in `aggregate.yaml`,
  rebuild, and see what the model does with it.
- Note that exposing a cache gives the agent `set-views` as well as
  `get-views`. Decide whether you want that.

---

## Reset

To start clean at any point:

```bash
docker compose down && docker compose up -d && ./seed.sh && ./build-view.sh
```

If the naive tool stops returning records from the beginning of the topic,
restart your MCP client. It keeps a read position in memory.

---

## Troubleshooting

**`rpk cluster info` asks you to log in to Redpanda Cloud.** Your active rpk
profile is a cloud one. Create a local profile:

```bash
rpk profile create local --set brokers=127.0.0.1:9092 --set admin.hosts=127.0.0.1:9644
```

**Port already in use.** Console is on 8090 and the broker on 9092. Change the
host side of the port mappings in `docker-compose.yml` if either is taken.

**`build-view.sh` prints no JSON.** It waits 25 seconds before the pipeline
flushes. Give it the full time.

**`call.sh` shows tools that aren't in `repo/`, or is missing one that is.**
`rpk connect mcp-server` reads `./repo` once at startup. Stop it and start it
again after changing anything in `repo/`. Restarting also resets its read
position.
