import valvelang
import googletrans
import utils
import time
import random
import os
import argparse
import shutil
import httpx

t = googletrans.Translator(service_urls=['translate.google.ru'], user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0", timeout=httpx.Timeout(10.0))

ap = argparse.ArgumentParser(description="Horribly butchers Source games by means of Google Translate!", add_help=True)
ap.add_argument("--lang", type=str, help="The full name of 'targeted' language (english, russian, spanish, german...)")
ap.add_argument("--rounds", type=int, help="How many times to retranslate")
ap.add_argument("--installdir", type=str, help="Path to game installation (dir which contains Source game launcher like hl2.exe)")
ap.add_argument("--basedir", type=str, help="name of game's basedir (hl2, episodic, portal, portal2)")

args = ap.parse_args()
try:
    final_lang = args.lang.lower()
    howmany = int(args.rounds)
    installdir = args.installdir
    basedir = args.basedir
    basedir_full = os.path.join(installdir, basedir)
except AttributeError:
    ap.print_help()
    exit()
# translate!
def mangletext(sourcetext, rounds):
    print(f'mangling: new victim "{sourcetext}"')
    intermediate = sourcetext
    for i in range(rounds):
        target = random.choice(list(googletrans.LANGUAGES.keys()))
        print(f"mangling: {i+1}/{rounds} using {target}")
        try:
            intermediate = t.translate(intermediate, dest=target).text
        except Exception:
            print("Error! Google rate limited us? Calming down...")
            time.sleep(2)
        #time.sleep(random.randint(1, 3))
    try:
        intermediate = t.translate(intermediate, dest=utils.get_key(googletrans.LANGUAGES, final_lang)).text
    except Exception:
        print("Error! Google rate limited us? Calming down...")
        time.sleep(5)
    print(f"mangled: {sourcetext} --> {intermediate}")
    return intermediate

print("Finding files to translate!")

files = {}

# platform langs
for ftype in ["platform", "vgui"]:
    f =  utils.open_platform_lang_by_name(installdir, final_lang, ftype)
    if f != None:
        files[ftype] = f

# game langs
for ftype in ["chat", "gameui", basedir, "closecaption"]:
    f = utils.open_game_lang_by_name(basedir_full, final_lang, ftype)
    if f != None:
        files[ftype] = f

print()
print("......")
print("Found: ")
if len(files) == 0:
    print("... nothing >:[. make sure lang files are there and not packed into VPK.")
    exit(1)
for k in files:
    if files[k] != None:
        print(k, files[k].name)
if list(files.keys()) == ["platform", "vgui"]:
    print("There are only platform files. make sure your game/sourcemod is installed and it's lang files are not packed into VPK.")
    exit(1)
#exit()

try:
    os.mkdir("output")
    os.mkdir(os.path.join("output", basedir))
    os.mkdir(os.path.join("output", "platform"))
    os.mkdir(os.path.join("output", basedir, "resources"))
    os.mkdir(os.path.join("output", "platform", "resources"))
except FileExistsError:
    if input("output already exists. remove? [y/n] ") == "y":
        shutil.rmtree('output')
        os.mkdir("output")
        os.mkdir(os.path.join("output", basedir))
        os.mkdir(os.path.join("output", "platform"))
        os.mkdir(os.path.join("output", basedir, "resources"))
        os.mkdir(os.path.join("output", "platform", "resources"))

skip_ftypes = []
for ftype in ["chat", "closecaption", "gameui", basedir]:
    if os.path.isfile(f"output/hl2/resources/{ftype}_{final_lang}.txt"):
        skip_ftypes.append(ftype)

for ftype in ["platform", "vgui"]:
    if os.path.isfile(f"output/platform/resources/{ftype}_{final_lang}.txt"):
        skip_ftypes.append(ftype)

for ftype in files:
    if ftype in skip_ftypes:
        print("skipping " + ftype)
        continue
    print("[New Victim] Translating " + ftype)
    lang = valvelang.parse_as_dict(files[ftype].read())
    print(f"parsed valvelang: {len(list(lang.values()))} pairs")

    for tag in lang:
        if "[english]" in tag: # skip refere--nce tags
            continue
        if lang[tag] == " " or lang[tag] == "": # don't waste time on empty strings
            continue
        lang[tag] = mangletext(lang[tag], howmany)
    if ftype == "vgui" or ftype == "platform":
        valvelang.write_lang(f"output/platform/resources/{ftype}_{final_lang}.txt", final_lang, lang)
    else:
        valvelang.write_lang(f"output/{basedir}/resources/{ftype}_{final_lang}.txt", final_lang, lang)