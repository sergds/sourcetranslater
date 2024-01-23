import math
import valvelang2
import valvelang
import googletrans
import utils
import time
import random
import os
import argparse
import shutil
import httpx
from multiprocessing import  Pool
import multiplex
from filesystem import *

def mangletext_task(tag, val, rounds, finallang, langpipeline):
    global final_lang
    final_lang = finallang
    global lang_pipeline
    lang_pipeline = langpipeline
    ival = val
    time.sleep(random.uniform(0.3, 2.7))
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
    for target in lang_pipeline:
        #print(f"mangling: {i+1}/{rounds} using {target}")
        try:
            intermediate = t.translate(intermediate, dest=target).text
        except Exception as e:
            print("Error! Google rate limited us? Calming down... " + str(e))
            time.sleep(random.randint(1,3))
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


t = googletrans.Translator(service_urls=['translate.google.ru'], user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0", timeout=httpx.Timeout(15.0), raise_exception=True)

lang_pipeline = []
non_interactive = False

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Horribly butchers Source games by means of Google Translate!", add_help=True)
    ap.add_argument("--lang", type=str, help="The full name of 'targeted' language (english, russian, spanish, german...)", required=True)
    ap.add_argument("--rounds", type=int, help="How many times to retranslate", required=True)
    ap.add_argument("--installdir", type=str, help="Path to game installation (dir which contains Source game launcher like hl2.exe)", required=True)
    ap.add_argument("--basedir", type=str, help="name of game's basedir (hl2, episodic, portal, portal2)", required=True)
    ap.add_argument("--files", type=str, help="name(s) of files to translate, comma-separated (vgui,admin,hl2)", default="")
    ap.add_argument("--language-pipeline", type=str, help="ISO-639 name(s) of intermediate languages to retranslate to, comma-separated (uz,zh-TW,bs,la). For list see https://cloud.google.com/translate/docs/languages#neural_machine_translation_model. If set, The rounds parameter is ignored, but still required.", default="")
    ap.add_argument("-N", "--non-interactive", action='store_true', help="Automatically answer 'no' to any prompts. Helpful in automation scripts (e.g tools/srctr_unattended.sh).")

    args = ap.parse_args()
    print("SourceTranslater is starting...")
    try:
        final_lang = args.lang.lower()
        howmany = int(args.rounds)
        installdir = args.installdir
        basedir = args.basedir
        basedir_full = os.path.join(installdir, basedir)
        force_files = []
        if args.files != "":
            force_files = args.files.split(",")
        if args.non_interactive:
            print("NON-INTERACTIVE MODE!")
            non_interactive = True
        if args.language_pipeline != "":
            lang_pipeline = args.language_pipeline.split(',')
    except AttributeError as e:
        print(e)
        ap.print_help()
        exit()

    print("Finding files to translate!")

    fs = Filesystem(installdir)
    files = {}
    havegame = False

    # game langs
    for f in fs.find_file(f"_{final_lang}.txt", firstonly=False, globsearch=True, searchpaths=[basedir])[1]:
        if force_files != []:
            if not (utils.ftype_from_filepath(f) in force_files):
                continue
        files[utils.ftype_from_filepath(f)] = f
        havegame = True

    # platform langs
    for f in fs.find_file(f"_{final_lang}.txt", firstonly=False, globsearch=True, searchpaths=["platform"])[1]:
        if force_files != []:
            if not (utils.ftype_from_filepath(f) in force_files):
                continue
        if "addons" in f:
            continue
        if utils.ftype_from_filepath(f) in files: # Handle same ftypes in platform which is kind of impossible, but still let's avoid having overwritten ftypes in dict, just in case.
            files["platform_"+utils.ftype_from_filepath(f)] = f
            continue
        files[utils.ftype_from_filepath(f)] = f

    print()
    print("......")
    print("Found: ")
    if len(files) == 0:
        print("... nothing >:[. make sure lang files are there and the the game install path is correct.")
        exit(1)
    for k in files:
        if files[k] != None:
            print(k, files[k])
    if not havegame:
        print("There are only platform files. make sure your game/sourcemod is installed.")
        exit(1)
    #exit()

    try:
        os.mkdir("output")
        for file in files:
            for comp in files[file].split(os.path.sep):
                if files[file].split(os.path.sep).index(comp) == len(files[file].split(os.path.sep)) - 1:
                    continue
                prev_comps = []
                currdir = ""
                if comp == "":
                    continue
                if files[file].split(os.path.sep).index(comp) > 0:
                    for prevp in files[file].split(os.path.sep)[files[file].split(os.path.sep).index(comp)-1::-1][::-1]:
                        if prevp != "":
                            prev_comps.append(prevp)
                currdir = os.path.join(os.path.normpath("/".join(prev_comps)))
                if not os.path.exists(os.path.join("output", currdir, comp)):
                    os.mkdir(os.path.join("output", currdir, comp))
    except FileExistsError:
        response = False
        if not non_interactive:
            response = input("output already exists. remove? [y/n] ").lower() == "y"
        else:
            print("output already exists. remove? N [NON-INTERACTIVE MODE]")
        if response:
            shutil.rmtree('output')
            os.mkdir("output")
        for file in files:
            for comp in files[file].split(os.path.sep):
                if files[file].split(os.path.sep).index(comp) == len(files[file].split(os.path.sep)) - 1:
                    continue
                prev_comps = []
                currdir = ""
                if comp == "":
                    continue
                if files[file].split(os.path.sep).index(comp) > 0:
                    for prevp in files[file].split(os.path.sep)[files[file].split(os.path.sep).index(comp)-1::-1][::-1]:
                        if prevp != "":
                            prev_comps.append(prevp)
                currdir = os.path.join(os.path.normpath("/".join(prev_comps)))
                if not os.path.exists(os.path.join("output", currdir, comp)):
                    os.mkdir(os.path.join("output", currdir, comp))
        else:
            if not os.path.isdir(os.path.join("output", basedir)):
                os.mkdir(os.path.join("output", basedir))
            if not os.path.isdir(os.path.join("output", basedir, "resource")):
                os.mkdir(os.path.join("output", basedir, "resource"))

    skip_ftypes = []
    for ftype in files:
        if os.path.isfile(os.path.join("output", os.path.normpath(files[ftype]))):
            skip_ftypes.append(ftype)

    if len(lang_pipeline) == 0:
        for _ in range(howmany):
            lang_pipeline.append(random.choice(list(googletrans.LANGUAGES.keys())))
    print(f"Language pipeline for this run: {lang_pipeline}")
    for ftype in files:
        fpath = '/'.join(files[ftype].split(os.path.sep)[1::])
        fbasedir = files[ftype].split(os.path.sep)[0]
        if ftype in skip_ftypes:
            print("skipping " + ftype)
            continue
        print("[New Victim] Translating " + ftype)
        if ftype == "closecaption" or ftype == "subtitles":
            print("NOTE: parsing cmds in closecaption to save them from google translate")
            print("WARNING: strings with cmds will be translated in parts!")
            lang = valvelang2.parse_as_dict(fs.read_file_text(fpath, fbasedir), True)
        else:
            print("NOTE: Not parsing cmds in non-closecaption file, as it will cause problems!")
            lang = valvelang2.parse_as_dict(fs.read_file_text(fpath, fbasedir), False)
        pcount = len(list(lang.values()))
        curcount = 0
        print(f"parsed valvelang: {pcount} pairs")

        pool = Pool(processes=6)
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
            if "$S" in lang[tag] or "$D" in lang[tag] or "$M" in lang[tag] or "$T" in lang[tag]: # Don't break datetime formats!
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
            args = [(lang_tags_needed[i], lang_vals_needed[i], howmany, final_lang, lang_pipeline) for i in range(len(lang_tags_needed))]
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
        print("Writing to " + files[ftype])
        valvelang2.write_lang(os.path.join("output", files[ftype]), final_lang, lang)