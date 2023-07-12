# Source Translater
Mangles your Source game's text by using Google Translate. Sometimes produces funny texts.

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
### Installation
just
```bash
pip3 install -r requirements.txt
```
and you are ready to go!