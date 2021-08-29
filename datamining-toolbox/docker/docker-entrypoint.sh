#!/bin/bash
set -euo pipefail

LUIGI_CFG=/app/luigi.cfg

function check_lu_config_or_die {
    if test ! -f "$LUIGI_CFG"; then
        if test -d "$LUIGI_CFG"; then
            echo "luigi.cfg is directory instead of file. May be you forget crate local file?"
            echo "Remember! Down & up again your docker-compose after create luigi.cfg."
        else
            echo "luigi.cfg is absent or not file."
        fi

        exit 1
    fi
}


if [ "$1" = 'lu' ]; then
    shift
    check_lu_config_or_die
    exec luigi --module gpn_hack.luigi_tasks "$@"
elif [ "$1" = 'lud' ]; then
    shift
    check_lu_config_or_die
    exec luigid "$@"
fi

exec "$@"
