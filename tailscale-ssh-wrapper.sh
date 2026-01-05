#!/bin/bash
# Filter out SSH options that tailscale ssh doesn't support
args=()
skip_next=false
for arg in "$@"; do
    if [ "$skip_next" = true ]; then
        skip_next=false
        continue
    fi
    if [[ "$arg" == -o* ]] || [[ "$arg" == -F* ]] || [[ "$arg" == -S* ]]; then
        if [[ "$arg" == -o ]] || [[ "$arg" == -F ]] || [[ "$arg" == -S ]]; then
            skip_next=true
        fi
        continue
    fi
    args+=("$arg")
done
exec tailscale ssh "${args[@]}"
