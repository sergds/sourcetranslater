# Utils for valve lang vdf files. V2 using vdf library instead of custom parser
from io import StringIO
import vdf
import valvelang # for cmd strings funcs

def parse_as_dict(vlang: str, parsecmds: bool):
    """
    input --- vlang file contents as string with newlines. parsecmds --- parse commands in lang file
    retval --- vlang dict[str, str/list]. There may be lists as values in case string contained commands (<clr:r,g,b>, <sfx>, <norepeat:N>). \
    In that case list[0] --- list that contains commands in their original order. list[1] --- list that contains substrings and empty strings where cmds were
    """
    d = vdf.parse(StringIO(vlang), escaped=False)
    try: # in some cases Tokens may be lowercase... gotta love valve
        dtags = d["lang"]["Tokens"]
    except Exception:
        dtags = d["lang"]["tokens"]
    if parsecmds:
        for tag in dtags:
            if ("<" in dtags[tag] and ">" in dtags[tag]): # got cmd string
                dtags[tag] = valvelang.disassemble_command_string(dtags[tag])
    return dtags

def write_lang(filepath, language, vlang_dict):
    """Write dict as a Valve lang"""
    vd = vlang_dict.copy()
    # first. Reassemble all cmd strings, because vdf library won't understand us otherwise (rightfully so).
    for key in vd:
        if type(vd[key]).__name__ == 'list':
            vd[key] = valvelang.assemble_command_string(vd[key])
    vd_full = {"lang": {"Language": language, "Tokens": vd}}
    vdf.dump(vd_full, open(filepath, 'wt', encoding='utf-16'), escaped=False)