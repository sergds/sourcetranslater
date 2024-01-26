# Filesystem class with vpk support
import vpk
import os

class Filesystem:
    """
    A simple Source Engine-like FileSystem for sourcetranslater. Designed primarily for reading UTF-16LE text files, but can be extended for more by adding more methods.
    Constructor takes a path to game as an argument (Half - Life 2, Portal, etc.) to find all potential mod dirs and mount their vpks.
    Every method has a doc string.
    WARNING: find_file returns file paths with basedir prepended to them, strip it away and use as a basedir parameter for the rest of the methods. Sorry about that.
    ### Methods:
    - find_file(self, filename: str, firstonly: bool = True, globsearch: bool = False, searchpaths: list[str] = []) -> (bool, set[str])
    - file_exists(self, filepath: str, basedir = "") -> bool
    - read_file_text(self, filepath: str, basedir: str = "") -> str
    """
    # initialize FS with gamepath. We'll use it to deduce all the basedirs and load all the dir vpks in them.
    def __init__(self, gamepath) -> None:
        self.gamepath = gamepath
        self.basedirs = [] # relative paths (hl2, left4dead, etc.)
        self.dir_vpks = [] # relative paths (left4dead/pak01_dir.vpk, etc.)
        self.loaded_vpks = dict[str, vpk.VPK]() # vpk objects. str is a dir_vpks entry for it
        print("[Filesystem] init")
        # Find basedirs
        with os.scandir(self.gamepath) as it:
            for entry in it:
                if not entry.name == 'bin' and not entry.name == 'config' and entry.is_dir():
                    self.basedirs.append(entry.name)
                    print("[Filesystem][init][search] found basedir " + entry.name)
        # Find Directory VPKs
        for bdir in self.basedirs:
            print("[Filesystem][init][find vpks] searching " + os.path.join(self.gamepath, bdir))
            with os.scandir(os.path.join(self.gamepath, bdir)) as it:
                for entry in it:
                    if "_dir" in entry.name and "vpk" in entry.name and entry.is_file():
                        print("[Filesystem][init][VPK] found dir vpk " + os.path.join(bdir, entry.name))
                        self.dir_vpks.append(os.path.join(bdir, entry.name))
        # Load VPKs
        for fvpk in self.dir_vpks:
            print("[Filesystem][init][VPK] mounting " + fvpk)
            self.loaded_vpks[fvpk] = vpk.open(os.path.join(self.gamepath, fvpk))
    def find_file(self, filename: str, firstonly: bool = True, globsearch: bool = False, searchpaths: list[str] = []) -> (bool, set[str]):
        """
        If file exists also returns set with relative paths in [basedir/path/to/file] format.
        - filename: str, self-explanatory.
        - firstonly: bool, find only one occurence of the file.
        - globsearch: bool, find all files whose names contain filename. For example, find all the _russian.txt files for lang vdfs for russian language.
        - searchpaths: list[str], search in these basedirs only. Uses basedirs discovered on init if len == 0.
        """
        # Search OS's vfs first
        ret_files = set[str]()
        ret_result = False
        bdirs = searchpaths.copy()
        if len(bdirs) == 0:
            bdirs = self.basedirs.copy()
        for bdir in bdirs:
            for root, dirs, files in os.walk(os.path.join(self.gamepath, bdir)):
                for f in files:
                    if globsearch:
                        if filename in f:
                            ret_files.add(os.path.normpath(os.path.join(bdir, os.path.relpath(root, start=os.path.join(self.gamepath, bdir)), f)))
                            ret_result = True
                            if firstonly:
                                return ret_result, ret_files
                    else:
                        if f == filename:
                            ret_files.add(os.path.normpath(os.path.join(bdir, os.path.relpath(root, start=os.path.join(self.gamepath, bdir)), f)))
                            ret_result = True
                            if firstonly:
                                return ret_result, ret_files
        # Also search the VPKs if not found or searching all occurences
        if not ret_result or not firstonly:
            for vpkobj in self.loaded_vpks:
                if os.path.split(vpkobj)[0] in bdirs:
                    for filepath in self.loaded_vpks[vpkobj]:
                        if globsearch:
                            if filename in os.path.basename(filepath):
                                ret_files.add(os.path.normpath(os.path.join(os.path.split(vpkobj)[0], filepath)))
                                ret_result = True
                                if firstonly:
                                    return ret_result, ret_files
                        else:
                            if os.path.basename(filepath) == filename:
                                ret_files.add(os.path.normpath(os.path.join(os.path.split(vpkobj)[0], filepath)))
                                ret_result = True
                                if firstonly:
                                    return ret_result, ret_files
        return ret_result, ret_files
    def file_exists(self, filepath: str, basedir = "") -> bool:
        """
        Does file exist in fs?
        - if basedir is set, then search only in the specified basedir
        """
        # Is file in OS vfs?
        bdirs = []
        if basedir != "":
            bdirs.append(basedir)
        else:
            bdirs = self.basedirs.copy()
        for bdir in bdirs:
            if os.path.exists(os.path.join(self.gamepath, bdir, os.path.normpath(filepath))):
                return True
        # Search VPKs
        for fvpk in self.loaded_vpks:
            if os.path.split(fvpk)[0] in bdirs:
                for fpath in self.loaded_vpks[fvpk]:
                    if os.path.normpath(fpath) == os.path.normpath(filepath):
                     return True
        return False
    def read_file_text(self, filepath: str, basedir: str = "") -> str:
        """
        Read the contents of a file in the fs and return as a utf-16le string. if file doesn't exist, returns empty string. IO Exceptions are not handled by this method.
        - filepath is a relative path to a file that needs to be read.
        - basedir is base directory of a mod. "The main search path" if you wish.
        """
        bdirs = []
        #if not self.file_exists(filepath=filepath, basedir=basedir): # very expensive, don't uncomment.
        #    return ""
        if basedir != "":
            bdirs.append(basedir)
        else:
            bdirs = self.basedirs.copy()
        for bdir in bdirs:
            if os.path.exists(os.path.join(self.gamepath ,bdir, os.path.normpath(filepath))):
                with open(os.path.join(self.gamepath ,bdir, os.path.normpath(filepath)), "rt", encoding="utf-16le") as f:
                    return f.read()
        for vpkfile, handle in self.loaded_vpks.items():
            for bdir in bdirs:
                if not bdir in vpkfile: # vpkfile contains basedir as a first path component
                    continue # We need only vpks we CARE about.
            try:
                f = handle[os.path.normpath(filepath).replace("\\", "/")] # vpk needs paths to be posix format
                return f.read().decode("utf-16le")
            except Exception:
                continue
        return ""