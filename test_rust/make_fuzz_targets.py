#!/usr/bin/env python3

from pathlib import Path
import shutil
import os
import re

import tomlkit

fuzz_common = Path("fuzz_common").absolute()
bug_collection = Path("bug_collection").absolute()
bug_fuzzing_collection = Path("bug_fuzzing_collection").absolute()


bug_fuzzing_collection.mkdir()

main_def_pattern = re.compile(r'fn\s*main')
main_pub_def_pattern = re.compile(r'pub\s*fn\s*main')
def make_main_public(src):
    if main_pub_def_pattern.match(src):
        return src
    else:
        return main_def_pattern.sub("pub fn main", src)

cargo_src_f = Path("app/Cargo.toml")
cargo_dest = ""
with cargo_src_f.open("r") as f:
    cargo_src = tomlkit.load(f)

    # replace bin target by lib target
    # TODO: keep both bin and lib target to make testing easier
    cargo_src.pop("bin")

    if not "lib" in cargo_src:
        cargo_src["lib"] = {}

    cargo_dest = tomlkit.dumps(cargo_src)


for i, bug_src in enumerate(bug_collection.iterdir()):
    print(f"Processing bug {bug_src}")
    destdir = bug_fuzzing_collection / f"bug{i}"
    destdir.mkdir()

    # write bug injection parameters to a file
    (destdir / "injection_description.txt").write_text(bug_src.stem)

    # copy source code to target
    # additionnaly replace "fn main" by "pub fn main"

    codedir = destdir / "src"
    codedir.mkdir()
    dest_code = codedir / "lib.rs"
    dest_code.write_text(make_main_public(bug_src.read_text()))

    # write a cargo file
    (destdir / "Cargo.toml").write_text(cargo_dest)


    # symlink the fuzz targets
    fuzz_dir = destdir / "fuzz"
    os.symlink(os.path.relpath(fuzz_common, destdir), fuzz_dir)