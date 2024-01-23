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

### How to use all of that (Typical usage)
That's how these tools can assist you in creating GTE mod for a source game.
1. Use sourcetranslater.py to create the translation for a source game (the newer the game, the less are chances to fully mod it, as newer source branches (e.g l4d-portal2-csgo branch lineage) tend to have stuff hardcoded in the basemodpanel and other parts of their custom gameui, as well as extensive use of vpks for gameui KVs)
2. Adjust it manually (Correct the kv file structure, make translations funnier manually, etc.)
3. (Optional, but highly recommended for a quality GTE mod) record a voiceover for all the translated dialogues.
4. (Optional, you can just zip it up like in old good days and tell users to overwrite files) Create a mod installer. There's two ways you can to that: the old nsis installer (requires a NSI and finalizer script rewriting for a particular game) or a new experimental UNInstaller (universal installer) which was designed for source game gte mods (Just requires you to edit 3 lines in uninstaller.json and build the installer with the build_uninstaller.py script)
5. Distribute on your platform of choice.

**Note that subtitles and/or closecaption files need to be compiled into vcd .dat files via captioncompiler.exe! Valve DevWiki has info about that**

### Installation
just
```bash
pip3 install -r requirements.txt
```
and you are ready to go!
