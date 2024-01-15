#!/bin/bash

# Translate on a server without needing an interactive ssh session. Also get a notification on finish.
# Just run this script with a path to the game, basedir and a ntfy.sh topic name and disown it.

# An example for l4d2:
# bash tools/srctr_unattended.sh ~/l4d2 left4dead2 yourntfytopic & disown
# Can also be launched from a custom systemd unit, init script, ci/cd pipeline, etc. for convinience.

curl \
  -d "tools/srctr_unattended.sh: Started translating $2 on `hostname`" \
  -H "Title: SourceTranslater unattended translation" \
  -H "Priority: high" \
  -H "Tags: carrot,arrows_counterclockwise,wheelchair,srctr" \
  https://ntfy.sh/$3

python3 sourcetranslater.py --lang russian --rounds 5 --installdir $1 --basedir $2 -N &> srctr_unattended.log
curl \
  -d "tools/srctr_unattended.sh: Finished translating $2 on `hostname`" \
  -H "Title: SourceTranslater unattended translation" \
  -H "Priority: high" \
  -H "Tags: carrot,arrows_counterclockwise,white_check_mark,srctr" \
  https://ntfy.sh/$3
