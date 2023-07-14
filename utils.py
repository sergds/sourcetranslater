# Take a subtitle broken by GTranslate and fix it's square brackets, or remove excessive bracketing
# Use only on strings with <sfx> command
def restore_subtitles_formatting(cmdsublist: list):
    ll = cmdsublist.copy()
    prevchar = ''
    idx = 0
    for c in ll[1]:
        s = "".join(ll[1])
        if s.count("[") == 1 and s.count("]") == 1 and s[0] == "[" and s[-1] == "]": # Needs fixing at all?
            return ll
        else:
            if c != '':
                im = c.replace('[', '')
                im = im.replace(']', '')
                if im[0] != "[":
                    im = "[" + im
                if im[-1] != "]":
                    im = im + "]"
                ll[1][idx] = im
        idx += 1
    return ll
                    
# Do we have this cmd in cmdsublist?
def has_cmd(cmd: str, cmdsublist: list):
    for c in cmdsublist[0]:
        if cmd in c:
            return True
    return False

def get_key(mdict ,val):
    for key, value in mdict.items():
        if val == value:
            return key
    return "No Such Key!"

def open_game_lang_by_name(basedir_full, final_lang, ftype):
    try:
        print(f"probing {basedir_full}/resource/{ftype}_{final_lang}.txt...")
        return open(f"{basedir_full}/resource/{ftype}_{final_lang}.txt", "r", errors='ignore', encoding="utf16")
    except Exception as e:
        return None
        print(f"failed opening {ftype}")

def open_platform_lang_by_name(installdir, final_lang, ftype):
    try:
        print(f"probing {installdir}/platform/resource/{ftype}_{final_lang}.txt...")
        return open(f"{installdir}/platform/resource/{ftype}_{final_lang}.txt", "r", errors='ignore', encoding="utf16")
    except Exception as e:
        print(f"failed opening {ftype}")