# Source Translater
Mangles your Source game's text by using Google Translate. Sometimes produces funny texts.

Planned (For winter holidays):
- [ ] Code cleanup, because this was written in a couple of days for Portal 2 GTE Russian mod. OOP rewrite perhaps.
- [ ] "ActorDB" of some sort (to keep actor's retranslated names in dialogues constant)
- [ ] VPK support (For l4d engine lineage)

### Usage

```bash
sourcetranslater.py [-h] [--lang LANG] [--rounds ROUNDS] [--installdir INSTALLDIR] [--basedir BASEDIR]
```
```
  --lang LANG           The full name of 'targeted' language (english, russian, spanish, german...)
  --rounds ROUNDS       How many times to retranslate
  --installdir INSTALLDIR
                        Path to game installation (dir which contains Source game launcher like hl2.exe)
  --basedir BASEDIR     name of game's basedir (hl2, episodic, portal, portal2)
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
