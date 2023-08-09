import math
import valvelang
import googletrans
import utils
import time
import random
import os
import argparse
import shutil
import httpx
from multiprocessing.pool import ThreadPool
import multiplex

cooldownN = 0
cooldown = False

def complain_ratelimit(e):
    if cooldown:
        cooldownN -= 1
        if cooldownN <= 0:
            cooldown = False
        return
    cooldown = True
    cooldownN = 100
    print("Error! Google rate limited us? Calming down... " + e)


t = googletrans.Translator(service_urls=['translate.google.ru'], user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0", timeout=httpx.Timeout(10.0), raise_exception=True)

if __name__ == '__main__':

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

    def mangletext_task(tag, val, rounds):
        ival = val
        time.sleep(random.randint(1,5))
        if type(val).__name__ == 'str':
            ival = mangletext(ival, rounds)
        elif type(val).__name__ == 'list':
            ival = val.copy()
            ival = mangletext_withcmds(ival, rounds)
        return [tag, ival]

    # translate!
    def mangletext_withcmds(cmdstrlist, rounds):
        res = cmdstrlist.copy()
        for sb in cmdstrlist[1]:
            if len(sb) > 0:
                res[1][res[1].index(sb)] = mangletext(sb, rounds)
        return res

    def mangletext(sourcetext, rounds):
        if sourcetext.count("\n") > 1:
            print(f'mangling: new multiplex/multiliner')
        else:
            print(f'mangling: new single victim ' + sourcetext)
        intermediate = sourcetext
        for i in range(rounds):
            target = random.choice(list(googletrans.LANGUAGES.keys()))
            #print(f"mangling: {i+1}/{rounds} using {target}")
            try:
                intermediate = t.translate(intermediate, dest=target).text
            except Exception as e:
                print("Error! Google rate limited us? Calming down... " + str(e))
                time.sleep(random.randint(2,10))
            #time.sleep(random.randint(1, 3))
        try:
            intermediate = t.translate(intermediate, dest=utils.get_key(googletrans.LANGUAGES, final_lang)).text
        except Exception as e:
            print("Error! Google rate limited us? Calming down... " + str(e))
        finally:
            pass
        if sourcetext.count("\n") > 1:
            print(f'mangled: multiplex/multiline string')
        else:
            print(f"mangled: {sourcetext} --> {intermediate}")
        return intermediate.replace('"', "'") # Replace double quotes with quotes. Beacause this will break vlang file!

    print("Finding files to translate!")

    files = {}

    # platform langs
    for ftype in ["platform", "vgui"]:
        f =  utils.open_platform_lang_by_name(installdir, final_lang, ftype)
        if f != None:
            files[ftype] = f

    # game langs
    ftypes_known = ["chat", "gameui" , "basemodui", basedir, "valve", "closecaption", "subtitles"]
    # Handle basegame files in DLCs
    if len(basedir.split("_")) > 1:
        ftypes_known.append(basedir.split("_")[0])

    for ftype in ftypes_known:
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
        os.mkdir(os.path.join("output", basedir, "resource"))
        os.mkdir(os.path.join("output", "platform", "resource"))
    except FileExistsError:
        if input("output already exists. remove? [y/n] ") == "y":
            shutil.rmtree('output')
            os.mkdir("output")
            os.mkdir(os.path.join("output", basedir))
            os.mkdir(os.path.join("output", "platform"))
            os.mkdir(os.path.join("output", basedir, "resource"))
            os.mkdir(os.path.join("output", "platform", "resource"))
        else:
            if not os.path.isdir(os.path.join("output", basedir)):
                os.mkdir(os.path.join("output", basedir))
            if not os.path.isdir(os.path.join("output", basedir, "resource")):
                os.mkdir(os.path.join("output", basedir, "resource"))

    skip_ftypes = []
    for ftype in ftypes_known:
        if os.path.isfile(f"output/{basedir}/resource/{ftype}_{final_lang}.txt"):
            skip_ftypes.append(ftype)

    for ftype in ["platform", "vgui"]:
        if os.path.isfile(f"output/platform/resource/{ftype}_{final_lang}.txt"):
            skip_ftypes.append(ftype)

    for ftype in files:
        if ftype in skip_ftypes:
            print("skipping " + ftype)
            continue
        print("[New Victim] Translating " + ftype)
        if ftype == "closecaption" or ftype == "subtitles":
            print("NOTE: parsing cmds in closecaption to save them from google translate")
            print("WARNING: strings with cmds will be translated in parts!")
            lang = valvelang.parse_as_dict(files[ftype].read(), True)
        else:
            print("NOTE: Not parsing cmds in non-closecaption file, as it will cause problems!")
            lang = valvelang.parse_as_dict(files[ftype].read(), False)
        pcount = len(list(lang.values()))
        curcount = 0
        print(f"parsed valvelang: {pcount} pairs")

        pool = ThreadPool(processes=6)
        lang_tags_needed = []
        lang_vals_needed = []
        multiplex_size = 10
        for tag in lang:
            if "[english]" in tag: # skip reference tags
                if type(lang[tag]).__name__ != 'list':
                    lang[tag] = lang[tag].replace("\n", "")
                continue
            if lang[tag] == " " or lang[tag] == "": # don't waste time on empty strings
                continue
            curcount += 1
            if ftype == "closecaption" or ftype == "subtitles":
                lang_tags_needed.append(tag)
                lang_vals_needed.append(lang[tag])
                continue
            if final_lang != "english":
                print(f"Tag {curcount}/{math.floor(pcount/2)}") # There's about half of reference strings for translators
            else:
                print(f"Tag {curcount}/{pcount}")
            if type(lang[tag]).__name__ == 'list':
                lang[tag] = mangletext_withcmds(lang[tag], howmany)
                continue
            if lang[tag].count("\n") > 1 or lang[tag].count("[") > 0 or lang[tag].count("$") > 0 or lang[tag].count("]") > 0: # Don't multiplex multiline or formatted stuff.
                print("Translating A MULTILINER!!")
                lang[tag] = mangletext(lang[tag], howmany)
                print("Translated MULTILINER!\n " + tag + " = " + lang[tag])
                continue
            lang_tags_needed.append(tag)
            lang_vals_needed.append(lang[tag])
            if len(lang_tags_needed) >= multiplex_size:
                print("Assembled multiplex of " + str(multiplex_size))
                mux = multiplex.multiplex_requests(lang_vals_needed)
                mux_res = mangletext(mux, howmany)
                res = multiplex.demultiplex_requests(mux_res)
                if len(lang_tags_needed) != len(res):
                    print("Borked multiplex!")
                    print(len(lang_vals_needed), len(res))
                    print(lang_vals_needed, res)
                    exit(1)
                for i in range(len(lang_tags_needed)):
                    lang[lang_tags_needed[i]] = res[i]
                    print(f"{lang_tags_needed[i]} = {res[i]}")
                lang_tags_needed = []
                lang_vals_needed = []
                continue
            else:
                continue
#            if type(lang[tag]).__name__ == 'str':
#                lang[tag] = mangletext(lang[tag], howmany)
#            elif type(lang[tag]).__name__ == 'list':
#                lang[tag] = mangletext_withcmds(lang[tag], howmany)
        if ftype == "closecaption" or ftype == "subtitles":
            args = [(lang_tags_needed[i], lang_vals_needed[i], howmany) for i in range(len(lang_tags_needed))]
            print(f"NOTE: Using a thread pool instead of multiplexing for subtitle stuff!")
            print(f"Submitting a job of {len(lang_tags_needed)} pairs to a thread pool")
            for result in pool.starmap(mangletext_task, args):
                res = result.copy()
                if type(lang[tag]).__name__ == 'list':
                    if utils.has_cmd("<sfx>", res[1]):
                        print(f"Before correction: {res[0]} = {res[1]}")
                        res[1] = utils.restore_subtitles_formatting(res[1])
                lang[res[0]] = res[1]
                print(f"{res[0]} = {res[1]}")
            lang_tags_needed = []
            lang_vals_needed = []
        if len(lang_tags_needed) != 0:
            print("translating what's left...")
            print("Assembled multiplex of " + str(lang_tags_needed))
            mux = multiplex.multiplex_requests(lang_vals_needed)
            mux_res = mangletext(mux, howmany)
            res = multiplex.demultiplex_requests(mux_res)
            if len(lang_tags_needed) != len(res):
                print("Borked multiplex!")
                print(len(lang_vals_needed), len(res))
                print(lang_vals_needed, res)
                exit(1)
            for i in range(len(lang_tags_needed)):
                lang[lang_tags_needed[i]] = res[i]
                print(f"{lang_tags_needed[i]} = {res[i]}")
            lang_tags_needed = []
            lang_vals_needed = []
        if ftype == "vgui" or ftype == "platform":
            valvelang.write_lang(f"output/platform/resource/{ftype}_{final_lang}.txt", final_lang, lang)
        else:
            valvelang.write_lang(f"output/{basedir}/resource/{ftype}_{final_lang}.txt", final_lang, lang)