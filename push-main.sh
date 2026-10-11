#!/bin/sh
set -u
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE" || exit 1

printf '%s\n' 'Pushing JCoin main to GitHub…'
if git push -u origin main; then
    printf '\n%s\n' 'Push completed.'
else
    result=$?
    printf '\n%s\n' 'Push failed. Check the message above for a network or GitHub sign-in issue.'
fi
printf '\n%s' 'Press Enter to close this window…'
read -r _
exit "${result:-0}"
