#!/usr/bin/env python3

from pathlib import Path
import asyncio
import sys
import os
import subprocess
import shutil
import time
import shlex

import asyncinotify

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log(s):
    print(f"{bcolors.OKCYAN}{s}{bcolors.ENDC}")


if(len(sys.argv) < 3):
    print("try_fuzz_all.py <app_to_fuzz_in_apps> <cmd with @@ as inputfile>")
    exit(0)

app_to_fuzz = sys.argv[1]
cmd = sys.argv[2]
cmd_split = shlex.split(cmd)



apps_dir = Path("app/").resolve()
app_to_fuzz_rel = os.path.relpath(app_to_fuzz, apps_dir)

afl_fuzz_dir = Path("fuzz_afl").resolve()
fuzz_target_dir = afl_fuzz_dir / "fuzz_target"
fuzz_target_cargo_template = (fuzz_target_dir /  "Cargo.toml.template").read_text()
fuzz_target_cargo = fuzz_target_dir / "Cargo.toml"

bug_fuzzing_collection_dir = Path("bug_fuzzing_collection").resolve()


bugdirs = [d for d in bug_fuzzing_collection_dir.iterdir() if d.is_dir]
times_success = []
times_failure = []


TIMEOUT = 1000

async def main():
    successes = 0
    for this_bugdir in bugdirs:
        log("Fuzzing {} ...".format(this_bugdir.name))
        found_bug = False     
        
        # build the binary (to test crashes later)
        log("Build executable to test...")
        pbuild_exec = await asyncio.create_subprocess_exec(
            "cargo", "build",
            cwd=this_bugdir / app_to_fuzz_rel,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        binary = this_bugdir / app_to_fuzz_rel / "target/debug" / cmd_split[0]
        log("-> binary is {}".format(binary.resolve()))

        # rebuild fuzz target against the new source
        # replace the path in the Cargo.toml to point to this_bugdir
        cargo_content = fuzz_target_cargo_template.replace("@@BUG_DIRECTORY@@", str(this_bugdir)) 
        fuzz_target_cargo.write_text(cargo_content)

        log("Rebuild the fuzz target...")
        pbuild_fuzz_target = await asyncio.create_subprocess_exec(
            "cargo", "afl", "build",
            cwd=afl_fuzz_dir / "fuzz_target",
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        # Wait for both build jobs to complete
        await asyncio.gather(pbuild_exec.wait(), pbuild_fuzz_target.wait())

        # remove the "out/" directory
        log("Remove previous fuzz output...")
        afl_outdir = afl_fuzz_dir / "fuzz_target/out"
        if afl_outdir.exists():
            shutil.rmtree(afl_outdir)

        afl_crashdir = afl_outdir / "default/crashes"

        # check new crashfiles
        async def watch_and_test():
            with asyncinotify.Inotify() as inotify:
                # UGLY: busy loop trying to attach inotify to afl_crashdir (wait for creation)
                watcher_added = False
                while not watcher_added:
                    try:
                        inotify.add_watch(afl_crashdir,  asyncinotify.Mask.CREATE | asyncinotify.Mask.MOVED_TO)
                        watcher_added = True
                    except Exception as e:
                        print(e, afl_crashdir)
                        await asyncio.sleep(0.5)
                
                log("Watching crashdir ...")
                async for event in inotify:
                    # new crash file created
                    log("New crashfile: {}".format(event.path))

                    crashfile = event.path
                    if not (crashfile.is_file() and crashfile.parent == afl_crashdir):
                        continue
                    cmd_args = shlex.split(cmd.replace("@@", str(crashfile)))[1:]
                    cmd2 = [str(binary)] + cmd_args
                    print("cmd=", cmd2)
                    log("Running crashfile:\n")
                    # test if the crashfile triggers the bug
                    bug_proc = await asyncio.create_subprocess_exec(
                        *cmd2,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                    )
                    async for line in bug_proc.stdout:
                        print(line.decode(), end="")
                        if (b"panicked at 'Bug found'" in line):
                            return True
                    log("Crash is not our bug")
        
        log("Start watcher and fuzzer...")

        # start fuzzing!
        t0 = time.monotonic_ns()

        # run the fuzzer in the background
        afl_proc = await asyncio.create_subprocess_exec(
            "cargo", "afl", "fuzz", "-i", "in", "-o", "out", "target/debug/fuzz-target",
            cwd=afl_fuzz_dir / "fuzz_target",
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL 
        )

        watcher = asyncio.create_task(watch_and_test())
        
        found_bug = False
        try:
            await asyncio.wait_for(watcher, timeout= TIMEOUT)
            found_bug = True
        except asyncio.exceptions.TimeoutError:
            found_bug = False
        this_bug_time = (time.monotonic_ns() - t0) * 1e-9

        # bug found or timeout: kill afl
        log("Terminate AFL...")
        if afl_proc.returncode is None:
            afl_proc.terminate()

        if found_bug:
            times_success.append(this_bug_time)
            log("Bug found for {} !".format(this_bugdir.name))
            successes += 1
        else:
            times_failure.append(this_bug_time)
            log("Failed to find bug for {}".format(this_bugdir.name))
        

    log(" Done fuzzing. {} / {} successes.".format(successes, len(bugdirs)))
    
    avg_success = sum(times_success) / len(times_success) if len(times_success) != 0 else 0
    avg_failure = sum(times_failure) / len(times_failure) if len(times_failure) != 0 else 0
    
    print(times_success)
    print(times_failure)
    log("Average time to find a bug: {}s".format(avg_success))
    log("Average time before giving up: {}s".format(avg_failure))




if __name__ == "__main__":
    asyncio.run(main())