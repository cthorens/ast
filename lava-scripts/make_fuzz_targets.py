#!/usr/bin/env python3

from pathlib import Path
from posixpath import relpath
import shutil
import os
import re
import sys

import tomlkit


main_def_pattern = re.compile(r'fn\s*main')
main_pub_def_pattern = re.compile(r'pub\s*fn\s*main')
def make_main_public(src):
    if main_pub_def_pattern.match(src):
        return src
    else:
        return main_def_pattern.sub("pub fn main", src)




def main(argv):
    src_app = Path("app/").resolve()
    if len(argv) >= 2:
        src_app = Path(argv[1]).resolve()

    fuzz_common = Path("fuzz_common").resolve()
    bug_collection = Path("bug_collection").resolve()
    bug_fuzzing_collection = Path("bug_fuzzing_collection").resolve()

    bug_fuzzing_collection.mkdir()

    cargo_src_f = src_app / "Cargo.toml"
    cargo_dest_content = ""
    pkg_name = ""
    has_lib = True
    with cargo_src_f.open("r") as f:
        cargo_src = tomlkit.load(f)

        if not "lib" in cargo_src:
            cargo_src["lib"] = {}
            has_lib = False

        cargo_dest_content = tomlkit.dumps(cargo_src)

        pkg_name = cargo_src["package"]["name"]


    min_lib="""\
pub mod main;

pub fn main_entry()
{
    return main::main();
}    
""".format(pkg_name)


    for bug_src in bug_collection.iterdir():
        print(f"Processing bug {bug_src}")

        bugfile = bug_src / "bug.rs"
        infofile = bug_src / "info.txt"

        # read the original path from the info file
        info_lines = infofile.read_text().splitlines()
        orig_path = Path(info_lines[0]).resolve()
        bugfile_relpath = orig_path.relative_to(src_app)

        destdir = bug_fuzzing_collection / bug_src.name
        if (destdir.exists()):
            print("WARN: skipping this bug, target dir {destir} exists already.")
            continue
        
        # replicate the app, bug change the content to
        # 1. contain the file with the injected bug
        # 2. make main public (if an executable)
        # 3. expose a lib target in Cargo.toml (if not present)
        shutil.copytree(src_app, destdir)

        # keep track of info
        shutil.copy(infofile, destdir)

        # 1. Place file with injected bug
        bugfile_in_dest = destdir / bugfile_relpath
        shutil.copy(bugfile, bugfile_in_dest)
        #bugfile_in_dest.write_text(make_main_public(bug_src.read_text()))

        # write a cargo file
        # and optionnaly a minimal library entrypoint
        (destdir / "Cargo.toml").write_text(cargo_dest_content)
        libfile = bugfile_in_dest.with_name("lib.rs")
        if not has_lib:
            if libfile.exists():
                print("WARN: no lib in Cargo.toml but lib.rs already exists! Overwriting.")
            libfile.write_text(min_lib)

        
        # symlink the fuzz targets
        fuzz_dir = destdir / "fuzz"
        os.symlink(os.path.relpath(fuzz_common, destdir), fuzz_dir)



if __name__ == "__main__":
    main(sys.argv)