# Source Translater
<p align="center">
  <img width="179.92" height="190" src="_img/srctr_logo.svg">
</p>
Mangles your Source game's text by using Google Translate. Sometimes produces funny texts.

Planned:
- [X] VPK support (For l4d engine lineage)
- [X] Replace my awful unstable vdf parser with [this](https://pypi.org/project/vdf/) one
- [ ] Code cleanup, because this was written in a couple of days for Portal 2 GTE Russian mod. OOP rewrite perhaps.
- [ ] "ActorDB" of some sort (to keep actor's retranslated names in dialogues consistent)

### Usage

```bash
sourcetranslater.py [-h] --lang LANG --rounds ROUNDS --installdir INSTALLDIR --basedir BASEDIR [--files FILES] [--language-pipeline LANGUAGE_PIPELINE] [-N]
```
```
Horribly butchers Source games by means of Google Translate!

options:
  -h, --help            show this help message and exit
  --lang LANG           The full name of 'targeted' language (english, russian, spanish, german...)
  --rounds ROUNDS       How many times to retranslate
  --installdir INSTALLDIR
                        Path to game installation (dir which contains Source game launcher like hl2.exe)
  --basedir BASEDIR     name of game's basedir (hl2, episodic, portal, portal2)
  --files FILES         name(s) of files to translate, comma-separated (vgui,admin,hl2)
  --language-pipeline LANGUAGE_PIPELINE
                        ISO-639 name(s) of intermediate languages to retranslate to, comma-separated (uz,zh-TW,bs,la). For list see https://cloud.google.com/translate/docs/languages#neural_machine_translation_model. If  
                        set, The rounds parameter is ignored, but still required.
  -N, --non-interactive
                        Automatically answer 'no' to any prompts. Helpful in automation scripts (e.g tools/srctr_unattended.sh).
```
Example:
```
python3 sourcetranslater.py --lang russian --rounds 5 --installdir "/home/sergds/.local/share/Steam/steamapps/common/Half-Life 2" --basedir hl2
```

**Note that subtitles and/or closecaption files need to be compiled into vcd .dat files via captioncompiler.exe! Valve DevWiki has info about that**

### Installation
just
```bash
pip3 install -r requirements.txt
```
and you are ready to go!
