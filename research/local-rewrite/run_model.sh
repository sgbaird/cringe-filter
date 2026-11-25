#!/bin/bash
# run_model.sh <label> <gguf> <extra-server-args> -- <drafts...>
set -u
cd "$(dirname "$0")"
mkdir -p logs
label=$1; gguf=$2; sargs=$3; shift 4
export LD_LIBRARY_PATH=$PWD/bin/llama-b11342
ps -eo pid,comm | awk '$2=="llama-server"{print $1}' | xargs -r kill; sleep 2
bin/llama-b11342/llama-server -m "models/$gguf" -t 4 -c 16384 --port 8080 --jinja $sargs > "logs/$label.server.log" 2>&1 &
for i in $(seq 1 120); do curl -s localhost:8080/health | grep -q ok && break; sleep 1; done
echo "server up for $label at $(date -u +%T)"
python3 bench.py "$label" "$@"
echo "done $label at $(date -u +%T)"
ps -eo pid,comm | awk '$2=="llama-server"{print $1}' | xargs -r kill; sleep 2
