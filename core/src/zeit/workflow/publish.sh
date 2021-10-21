#!/bin/bash

set -e
echo "${publish_action} script"

if [[ -n "$publish_ssh_persist" ]]; then
   persist="-o ControlMaster=auto -o ControlPath=/tmp/ssh_mux_%u_%h_%p_%r -o ControlPersist=4h"
fi

case $publish_action in
    publish)
        cmd="$publish_command_publish"
    ;;
    retract)
        cmd="$publish_command_retract"
    ;;
    *)
        echo "Unrecognized action $publish_action"
        exit 1
    ;;
esac

cat $1 | ssh -o BatchMode=yes $persist "${publish_user}@${publish_host}" $cmd

echo
echo done.
