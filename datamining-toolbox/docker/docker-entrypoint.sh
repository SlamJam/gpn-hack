#!/bin/bash
set -euo pipefail

if [ "$1" = 'lu' ]; then
    shift
    exec luigi --module gpn_hack.luigi_tasks "$@"
elif [ "$1" = 'lud' ]; then
    shift
    exec luigid "$@"
fi

exec "$@"
