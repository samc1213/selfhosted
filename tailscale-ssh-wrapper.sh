#!/bin/bash
# Filter out SSH options that tailscale ssh doesn't support and extract user/host

user=""
host=""
args=()
skip_next=false

for arg in "$@"; do
    if [ "$skip_next" = true ]; then
        skip_next=false
        continue
    fi

    # Extract user from -o User=xxx
    if [[ "$arg" =~ ^-oUser=(.+)$ ]] || [[ "$arg" =~ ^-o[[:space:]]*User=\"?([^\"]+)\"?$ ]]; then
        user="${BASH_REMATCH[1]}"
        continue
    fi

    # Skip -o, -F, -S options
    if [[ "$arg" == -o* ]] || [[ "$arg" == -F* ]] || [[ "$arg" == -S* ]]; then
        if [[ "$arg" == -o ]] || [[ "$arg" == -F ]] || [[ "$arg" == -S ]]; then
            skip_next=true
        fi
        continue
    fi

    # Skip verbose flags
    if [[ "$arg" =~ ^-v+$ ]]; then
        continue
    fi

    # First non-option arg is the host
    if [ -z "$host" ] && [[ ! "$arg" =~ ^- ]]; then
        host="$arg"
        continue
    fi

    args+=("$arg")
done

# Build the target (user@host or just host)
if [ -n "$user" ]; then
    target="${user}@${host}"
else
    target="${host}"
fi

exec tailscale ssh "$target" "${args[@]}"
