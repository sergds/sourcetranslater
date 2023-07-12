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