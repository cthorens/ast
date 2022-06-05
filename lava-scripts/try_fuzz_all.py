#!/usr/bin/env python3

from pathlib import Path
import asyncio
import sys
import os
import subprocess
import logging

import time

logging.basicConfig(level=logging.INFO)

if(len(sys.argv) < 2):
    print("try_fuzz_all.py <fuzz_target_in_app>")
    exit(0)

apps_dir = Path("app/").resolve()
fuzz_target = Path(sys.argv[1]).resolve()

fuzz_target_rel = os.path.relpath(fuzz_target, apps_dir)

fuzz_dir = Path("bug_fuzzing_collection").resolve()


bugdirs = [d for d in fuzz_dir.iterdir() if d.is_dir]
times_success = []
times_failure = []

TIMEOUT = 120

async def main():
    successes = 0
    for this_bugdir in bugdirs:
        logging.info(" Fuzzing {} ...".format(this_bugdir.name))
        found_bug = False
        attempt = 0
        t0 = time.monotonic_ns()
        this_bug_time = 0
        while (this_bug_time < TIMEOUT and not found_bug):
            logging.info(" attempt {} ...".format(attempt))

            this_fuzz_target = this_bugdir / fuzz_target_rel

            async def run_and_check():
                fuzz_p = await asyncio.create_subprocess_exec(
                    "cargo", "fuzz", "run", "fuzz_target_1", "--", "-rss_limit_mb=4096",
                    cwd=this_fuzz_target,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )

                async for line in fuzz_p.stdout:
                    if (b"panicked at 'Bug found'" in line):
                        print(line.decode(),end="")
                        return True

                return False

            found_bug = False
            try:
                found_bug = await asyncio.wait_for(run_and_check(), timeout=TIMEOUT)
            except asyncio.exceptions.TimeoutError:
                found_bug = False

            this_bug_time = (time.monotonic_ns() - t0) * 1e-9
            attempt += 1
        
        if found_bug:
            times_success.append(this_bug_time)

            logging.info(" Bug found for {}".format(this_bugdir.name))
            successes += 1
        else:
            times_failure.append(this_bug_time)
            logging.info(" Failed to find bug for {}".format(this_bugdir.name))

    logging.info(" Done fuzzing. {} / {} successes.".format(successes, len(bugdirs)))
    
    avg_success = sum(times_success) / len(times_success) if len(times_success) != 0 else 0
    avg_failure = sum(times_failure) / len(times_failure) if len(times_failure) != 0 else 0
    
    print(times_success)
    print(times_failure)
    logging.info(" Average time to find a bug: {}s".format(avg_success))
    logging.info(" Average time before giving up: {}s".format(avg_failure ))




if __name__ == "__main__":
    asyncio.run(main())