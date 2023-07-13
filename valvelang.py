import re
# Utility module for Valve lang files.

# If string has commands. it will return list:
# list[0] --- list that contains commands in their original order. list[1] --- list that contains substrings and empty strings where cmds were
def disassemble_command_string(stringval):
    if not ("<" in stringval and ">" in stringval):
        return stringval
    cmds = []
    substrings = []
    currsub = ""
    currcmd = ""
    proccmd = False
    for c in stringval:
        if c == "<": # Opened cmd, commit current substring, start command.
            proccmd = True
            if len(currsub) != 0:
                substrings.append(currsub)
            currsub = ""
            currcmd = currcmd + c
            continue
        elif c == ">": # Closed cmd, commit current cmd, start substring
            proccmd = False
            currcmd = currcmd + c
            substrings.append('')
            cmds.append(currcmd)
            currcmd = ""
            continue
        if proccmd:
            currcmd = currcmd + c
        else:
            currsub = currsub + c
        

    return [cmds, substrings]

# Reassemble processed string with commands
# Returns str
def assemble_command_string(listcmdstr):
    res = listcmdstr[1].copy()
    currcmd = 0
    for substr in res:
        if substr == '':
            res[res.index(substr)] = listcmdstr[0][currcmd]
            currcmd += 1
    return "".join(res)

def test_cmdstring_processing():
    teststr = "<clr:255,0,0>This is red<I> and italics<B> and<cr>bold<B><I><clr:255,255,255> white again.<sfx><norepeat:1>"
    t = disassemble_command_string("<clr:255,0,0>This is red<I> and italics<B> and<cr>bold<B><I><clr:255,255,255> white again.<sfx><norepeat:1>")
    t2 = assemble_command_string(t)
    print(teststr)
    print(t2)
    print("".join(t[1]))
    assert(teststr == t2)
    print("test_cmdstring_processing: PASSED")

# input --- vlang file contents as string with newlines. parsecmds --- parse commands in lang file
# retval --- vlang dict[str, str/list]. There may be lists as values in case string contained commands (<clr:r,g,b>, <sfx>, <norepeat:N>). \
# In that case list[0] --- list that contains commands in their original order. list[1] --- list that contains substrings and empty strings where cmds were
def parse_as_dict(vlang: str, parsecmds: bool):
    lines = vlang.splitlines()
    res = {}
    level = 0 # 0 = top level of vlang. we are interested in level 2, where all the tag/string pairs are.
    cmdstrings = 0 # Just for statistics.
    for l in lines:
        if level < 0:
            raise RuntimeError("valvelang parse error: level < 0")
            break
        if l == "{":
            level += 1
        if l == "}":
            level -= 1
        if level == 2 and l != "{":
            thestr = l.split(sep="\t")[-1].replace('"', '')
            if not ("<" in thestr and ">" in thestr) and not parsecmds:
                res[l.split(sep="\t")[0].replace('"', '')] = thestr
            else:
                cmdstrings += 1
                res[l.split(sep="\t")[0].replace('"', '')] = disassemble_command_string(thestr)
    if level != 0:
        raise RuntimeError("valvelang parse error: level != 0 at EOF")
    if parsecmds:
        print(f"valvelang: in total {str(cmdstrings)} strings with commands disassembled")
    return res

# Write dict as a Valve lang
def write_lang(filepath, language, vlang_dict):
    f = open(filepath, "w", encoding="utf16")
    f.write('"lang"\n') # Write header
    f.write("{\n") # Level 1 --- language info
    f.write(f'"Language"\t"{language}"\n"Tokens"\n')
    f.write("{\n") # Level 2 --- pairs
    for tag in vlang_dict:
        if type(vlang_dict[tag]).__name__ == 'str':
            f.write(f'"{tag}"\t"{vlang_dict[tag]}"\n')
        elif type(vlang_dict[tag]).__name__ == 'list':
            f.write(f'"{tag}"\t"{assemble_command_string(vlang_dict[tag])}"\n')
    f.write("}\n") # Level 2 closed
    f.write("}\n") # Level 1 closed
    f.close()