# Utility module for Valve lang files.


# input --- vlang file contents as string with newlines
# retval --- vlang dict[str, str]
def parse_as_dict(vlang: str):
    lines = vlang.splitlines()
    res = {}
    level = 0 # 0 = top level of vlang. we are interested in level 2, where all the tag/string pairs are.
    for l in lines:
        if level < 0:
            raise RuntimeError("vlang parse error: level < 0")
            break
        if l == "{":
            level += 1
        if l == "}":
            level -= 1
        if level == 2 and l != "{":
            res[l.split(sep="\t")[0].replace('"', '')] = l.split(sep="\t")[-1].replace('"', '')
    if level != 0:
        raise RuntimeError("vlang parse error: level != 0 at EOF")
    return res

# Write dict as a Valve lang
def write_lang(filepath, language, vlang_dict):
    f = open(filepath, "w", encoding="utf16")
    f.write('"lang"\n') # Write header
    f.write("{\n") # Level 1 --- language info
    f.write(f'"Language"\t"{language}"\n"Tokens"\n')
    f.write("{\n") # Level 2 --- pairs
    for tag in vlang_dict:
        f.write(f'"{tag}"\t"{vlang_dict[tag]}"\n')
    f.write("}\n") # Level 2 closed
    f.write("}\n") # Level 1 closed
    f.close()