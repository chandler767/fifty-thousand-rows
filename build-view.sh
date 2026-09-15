#!/usr/bin/env bash
mkdir -p ./cache
echo "building view, takes about 25s..."
rpk connect run aggregate.yaml &
PID=$!
sleep 25
kill $PID 2>/dev/null
wait $PID 2>/dev/null
cat ./cache/*
echo
