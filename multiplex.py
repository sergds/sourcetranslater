def multiplex_requests(vals: list):
    res = ""
    for v in vals:
        if len(res) == 0:
            res = res + v
        else:
            res = res + "\n" + v
    return res

def demultiplex_requests(muxd):
    return muxd.split("\n")