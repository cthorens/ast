#!/usr/bin/env python3

from pathlib import Path
from posixpath import relpath
import shutil
import os
import re
import sys
import logging

import tomlkit


def main(argv):
    if len(argv) < 2:
        logging.error("make_fuzz_targets.py <app_to_fuzz_in_apps>")
        return 0

    all_apps = Path("app/").resolve()
    to_fuzz_app = Path(argv[1]).resolve()

    fuzz_common = Path("fuzz_common").resolve()
    bug_collection = Path("bug_collection").resolve()
    bug_fuzzing_collection = Path("bug_fuzzing_collection").resolve()

    bug_fuzzing_collection.mkdir()


    for bug_src in bug_collection.iterdir():
        print(f"Processing bug {bug_src}")

        bugfile = bug_src / "bug.rs"
        infofile = bug_src / "info.txt"

        # read the original path from the info file
        info_lines = infofile.read_text().splitlines()
        orig_path = Path(info_lines[0]).resolve()
        bugfile_relpath = orig_path.relative_to(all_apps)

        destdir = bug_fuzzing_collection / bug_src.name
        if (destdir.exists()):
            print("WARN: skipping this bug, target dir {destir} exists already.")
            continue
        
        # replicate the app, replace file by bug-injected version
        shutil.copytree(all_apps, destdir)

        # keep track of info
        shutil.copy(infofile, destdir)

        # Place file with injected bug
        bugfile_in_dest = destdir / bugfile_relpath
        shutil.copy(bugfile, bugfile_in_dest)
        #bugfile_in_dest.write_text(make_main_public(bug_src.read_text()))

        
        # symlink the fuzz targets
        fuzz_app_dest = destdir / os.path.relpath(to_fuzz_app, all_apps)
        fuzz_dir = destdir  / os.path.relpath(to_fuzz_app, all_apps) / "fuzz"
        os.symlink(os.path.relpath(fuzz_common, fuzz_app_dest), fuzz_dir)



if __name__ == "__main__":
    main(sys.argv)
