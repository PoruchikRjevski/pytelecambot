#!/bin/bash

SRC_D="/src/"
MAIN_F="main.py"

CUR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

LINK_P="/usr/local/bin/"

PYTELECAMBOT="pytelecambot"


# MAIN FUNCS
main() {
    chmod +x $CUR_DIR$SRC_D*

    create_link

    exit 0
}

create_link() {
    check_and_rem_f "$LINK_P$PYTELECAMBOT"

    unlink $LINK_P$PYTELECAMBOT

    ln -sv $CUR_DIR$SRC_D$MAIN_F $LINK_P$PYTELECAMBOT

    echo "Link to \"$PYTELECAMBOT\" was created"
}

check_and_rem_f() {
    if [ -f "$1" ]
    then
        rm -f "$1"
    fi
}

main