#!/usr/bin/env bash
set -e
python3 seed.py
rpk topic create support_tickets -p 1 2>/dev/null || true
rpk topic produce support_tickets < tickets.jsonl > /dev/null
echo "seeded 50000 tickets"
