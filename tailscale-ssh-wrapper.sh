#!/bin/bash
# Filter out SSH options that tailscale ssh doesn't support

host=""
args=()
skip_next=false

for arg in "$@"; do
    if [ "$skip_next" = true ]; then
        skip_next=false
        continue
    fi

    # Skip all -o, -F, -S, -v options
    if [[ "$arg" == -o* ]] || [[ "$arg" == -F* ]] || [[ "$arg" == -S* ]] || [[ "$arg" =~ ^-v+$ ]]; then
        if [[ "$arg" == -o ]] || [[ "$arg" == -F ]] || [[ "$arg" == -S ]]; then
            skip_next=true
        fi
        continue
    fi

    # First non-option arg is the host
    if [ -z "$host" ] && [[ ! "$arg" =~ ^- ]]; then
        host="$arg"
        continue
    fi

    args+=("$arg")
done

exec tailscale ssh "sam@${host}" "${args[@]}"
