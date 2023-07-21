@echo off
pushd portal2
..\\bin\\captioncompiler -d 0 closecaption_russian.txt
..\\bin\\captioncompiler -d 0 subtitles_russian.txt
..\\bin\\captioncompiler -d 1 closecaption_russian.txt
..\\bin\\captioncompiler -d 1 subtitles_russian.txt
..\\bin\\captioncompiler -d 2 closecaption_russian.txt
..\\bin\\captioncompiler -d 2 subtitles_russian.txt
popd