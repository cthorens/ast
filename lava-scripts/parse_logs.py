#!/usr/bin/env python3

from pandare import plog_reader
import sys

def select_pc_instr(pc,l):
    for ul in unique_lib:
        if ul[0] <= pc and pc <= ul[0] + ul[1]:
            main_pc.add(pc)
            if not pc in bytes_used:
                bytes_used[pc] = l
   
def select_pc_branch(pc):
    for ul in unique_lib:
        if ul[0] <= pc and pc <= ul[0] + ul[1]:
            main_pc_branch.add(pc)

if len(sys.argv) < 2:
    print("Usage : parse_logs.py executable_name max_liveness(default=10) min_bytes_to_use(default=2)")
    exit()


lib_name = sys.argv[1]
if len(sys.argv) > 2:
    max_live = int(sys.argv[2])
else:
    max_live = 10
if len(sys.argv) > 3:
    min_bytes = int(sys.argv[3])
else:
    min_bytes = 2

main_pc = set()
main_pc_branch = set()

bytes_used = {}
bytes_label = {}
libs_for_thread = {}
bytes_liveness = {}
with plog_reader.PLogReader("pandalog.plog") as plr:
    for i,m in enumerate(plr):
        if m.HasField("tainted_instr"):
            ti = m.tainted_instr
            for tq in ti.taint_query:
                if tq.HasField("unique_label_set"):
                    taint_byte = tq.unique_label_set
                    bytes_label[taint_byte.ptr] = taint_byte.label
                    bytes_liveness[taint_byte.ptr] = 0
        if m.HasField("asid_libraries"):
            al = m.asid_libraries
            thread = m.asid
            these_libs = []
            for lib in al.modules:
                if lib_name in lib.file:
                    these_libs.append(lib)
                if len(these_libs) > 0:
                    if not (thread in libs_for_thread):
                        libs_for_thread[thread] = []
                    libs_for_thread[thread].append(these_libs)


threads = list(libs_for_thread.keys())

all_modules = []
for t in threads:
	all_modules = all_modules + libs_for_thread.get(t) 

unique_lib = set()
for mod in all_modules:
    for l in mod:
        tup = (l.base_addr,l.size)
        unique_lib.add(tup)


with plog_reader.PLogReader("pandalog.plog") as plr:
    for i,m in enumerate(plr):
        if m.HasField("tainted_instr"):
            ti = m.tainted_instr
            labels = set()
            for tq in ti.taint_query:
                ptr = tq.ptr
                if ptr in bytes_label:
                    labels.add(ptr)
            select_pc_instr(m.pc,labels)
        if m.HasField("tainted_branch"):
            select_pc_branch(m.pc)
            for tq in m.tainted_branch.taint_query:
                ptr = tq.ptr
                if ptr in bytes_liveness:
                    bytes_liveness[ptr] += 1


base_lib = (0,0)
for ul in unique_lib:
    if base_lib[0] == 0:
        base_lib = ul
    elif base_lib[0] > ul[0]:
        base_lib = ul
        

f = open("addr.txt","w")

for mp in main_pc:
    for bu in bytes_used[mp]:
        if bytes_liveness[bu] <= max_live and len(bytes_label[bu]) >= min_bytes:
            f.write(hex(mp-base_lib[0]))
            f.write("\n")
