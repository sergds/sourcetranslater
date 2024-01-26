#!/bin/bash

# Translate on a server without needing an interactive ssh session. Also get a notification on finish.
# Just run this script with a path to the game, basedir and a ntfy.sh topic name and disown it.

if [ -z "$PYTHON" ]; then # on a multiserver i actually use pypy3.
PYTHON="python3"
fi

# An example for l4d2:
# PYTHON=pypy3 bash tools/srctr_unattended.sh "/home/sergds/Left 4 Dead 2" left4dead2 mycoolntfytopic & disown
# Can also be launched from a custom systemd unit, init script, ci/cd pipeline, etc. for convinience.

curl \
  -d "tools/srctr_unattended.sh: Started translating $2 on `hostname`" \
  -H "Title: SourceTranslater unattended translation" \
  -H "Priority: high" \
  -H "Tags: carrot,arrows_counterclockwise,wheelchair,srctr" \
  https://ntfy.sh/$3

$PYTHON sourcetranslater.py --lang russian --rounds 5 --installdir "`echo $1`" --basedir "`echo $2`" -N &> srctr_unattended.log
curl \
  -d "tools/srctr_unattended.sh: Finished translating $2 on `hostname`" \
  -H "Title: SourceTranslater unattended translation" \
  -H "Priority: high" \
  -H "Tags: carrot,arrows_counterclockwise,white_check_mark,srctr" \
  https://ntfy.sh/$3
