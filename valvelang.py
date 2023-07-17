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
    #Commit stale stuff.
    if len(currsub) != 0:
        substrings.append(currsub)
    if len(currcmd) != 0:
        substrings.append('')
        cmds.append(currcmd)


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
    teststr = "<sfx><len:5>[Тиканье часов]"
    t = disassemble_command_string(teststr)
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
    lines = vlang.splitlines(True)
    res = {}
    level = 0 # 0 = top level of vlang. we are interested in level 2, where all the tag/string pairs are.
    cmdstrings = 0 # Just for statistics.
    multilinestrings = 0 # just for stats 2.
    multilinestrings_tags = "" # just for stats 2.
    multilinestrings_currtag = "" # just for stats 2.
    collectingmultiline = False
    tmpstrbuf = ""
    for l in lines:
        if level < 0:
            raise RuntimeError("valvelang parse error: level < 0")
        if l == "{\n":
            level += 1
        if l == "}\n":
            level -= 1
        if level == 2 and l != "{\n":
            l_clean = re.split("\[\$[a-zA-Z0-9]+\]", l)[0] # Remove these [$THINGS]. 100% will break something, but thats the best part of it >:]. because it will be a headache and a waste of time to handle every quirk of valve's lang files just to break the freaking text.
            if l_clean[-1] == "\t":
                l_clean = l_clean[:len(l_clean)-1:1] + '\n' # Quickly replace TAB with a newline. Like The [$THING] never existed here, ok?
            thestr = ""
            if len(l_clean) > 2:
                if l_clean.count('\n') > 1 or (l_clean[-2] != '"' and (l_clean.count('"') == 3 or l_clean.count("\t") == 1)) or (l_clean[-2] == '"' and (l_clean[-3] == ' ' or  l_clean[-3] == '\t')) and not collectingmultiline:
                    multilinestrings += 1
                    collectingmultiline = True
                    multilinestrings_tags = multilinestrings_tags + " " + l_clean.split(sep="\t")[0]
                    multilinestrings_currtag = l_clean.split(sep="\t")[0]
                    tmpstrbuf = tmpstrbuf + l_clean.split(sep="\t")[-1].replace('"', '')
                    #print("PRIMARY!!: " + l_clean)
                    continue # continue to the next line of string to start collecting it
            # Stumbled upon a multiline string? Well there goes my valve lang parser...
            if collectingmultiline:
                if l_clean.count('"') == 0:
                    tmpstrbuf = tmpstrbuf + l_clean # Collect it line by line
                    #print(l_clean)
                    continue
                elif l_clean.count('"') == 1:
                    if l_clean != '"\n': # Contains more than a " ? Include that!
                        tmpstrbuf = tmpstrbuf + l_clean.replace('"', '')
                        #print(l_clean)
                    collectingmultiline = False
                    thestr = tmpstrbuf

            if len(thestr) == 0:
                thestr = l_clean.split(sep="\t")[-1].replace('"', '')
            if not ("<" in thestr and ">" in thestr) and not parsecmds:
                if multilinestrings_currtag != "":
                    res[multilinestrings_currtag.replace('"', '')] = thestr
                    multilinestrings_currtag = ""
                else:
                    res[l_clean.split(sep="\t")[0].replace('"', '')] = thestr.replace("\n", "")
            else:
                cmdstrings += 1
                if multilinestrings_currtag != "":
                    res[multilinestrings_currtag.replace('"', '')] = disassemble_command_string(thestr)
                    multilinestrings_currtag = ""
                else:
                    res[l_clean.split(sep="\t")[0].replace('"', '')] = disassemble_command_string(thestr.replace("\n",''))
    if level != 0:
        raise RuntimeError("valvelang parse error: level != 0 at EOF")
    if parsecmds:
        print(f"valvelang: in total {str(cmdstrings)} strings with commands disassembled")
    print(f"valvelang: in total {str(multilinestrings)} multiline strings defeated! namely:" + multilinestrings_tags)
    return res

# Write dict as a Valve lang
def write_lang(filepath, language, vlang_dict):
    f = open(filepath, "w", encoding="utf16")
    f.write('"lang"\n') # Write header
    f.write("{\n") # Level 1 --- language info
    f.write(f'"Language"\t"{language}"\n"Tokens"\n')
    f.write("{\n") # Level 2 --- pairs
    for tag in vlang_dict:
        val = vlang_dict[tag]
        if type(val).__name__ != 'list':
            if val.count("\n") == 1: # [english] strings usually have newlines at the end:
                # So, remove that
                val = val.replace('\n', "", 1) 
        if type(vlang_dict[tag]).__name__ == 'str':
            f.write(f'"' + tag.replace("\n", "") + f'"\t"{vlang_dict[tag]}"\n')
        elif type(vlang_dict[tag]).__name__ == 'list':
            f.write(f'"' + tag.replace("\n", "") + f'"\t"{assemble_command_string(vlang_dict[tag])}"\n')
    f.write("}\n") # Level 2 closed
    f.write("}\n") # Level 1 closed
    f.close()