#!/usr/bin/env python3

from pathlib import Path
import random
import os

path_bugs = Path("bug_collection")
path_bugs.mkdir(exist_ok=True)

f = Path("lines.txt")
inject_pot = f.read_text().splitlines()

bug_id = 0

for ip in inject_pot:

    ip_clean = ip.strip("\n").split(":")
    ip_file = Path(ip_clean[0])
    ip_number = int(ip_clean[1]) - 1
    f2_lines = ip_file.read_text().splitlines()
    bug_line = f2_lines[ip_number]
    
    if " = " in bug_line:
        print(bug_line)
        lop = bug_line.split(" = ")[0]
        print(lop)
        var_name = lop.split(" ")[-1]
        print(var_name)
        
        rand_b = random.randint(0,255) 
        bug_str = "if " + var_name + " as u8 == "+ str(rand_b) + " { panic!(\"Bug found\") }"
        f2_lines.insert(ip_number+1,bug_str+"\n")


        bug_dir = path_bugs / f"bug{bug_id}"
        bug_dir.mkdir(exist_ok=True)

        # write the modified file and keep track of its path
        # in the orginal folder
        new_f2 = bug_dir / "bug.rs"
        new_f2_info_file = bug_dir / "info.txt"

        f2_lines = "\n".join(f2_lines)
        new_f2.write_text(f2_lines)

        new_f2_info_file.write_text("\n".join([str(ip_file), str(bug_line)]))

        bug_id += 1

        
        
