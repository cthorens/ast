# LAVA_Rust

## Setup

- Download the Docker image for `panda`.

```console
$ docker pull pandare/panda
```

- Create and start a Docker container with a bind mount exposing the files from LAVA_Rust

```console
# Supposing `lava_rust` contains the necessary files, i.e:
$ tree -L 1 lava_rust
lava_rust
├── elf_test
├── lava-scripts
├── README.md
└── svgcleaner_test

$ docker create --init -it --name panda \
   --mount type=bind,src="$(realpath lava_rust)",dst=/app \
   pandare/panda bash
$ docker start panda

# Check that the creation was successful
$ docker ps
CONTAINER ID   IMAGE              COMMAND   CREATED      STATUS        PORTS     NAMES
1ae1ea3b9c44   pandare/pandadev   "bash"    6 days ago   Up 10 hours             panda
```

- You can now open a shell in the Docker image to run the analysis, the injection, and the fuzzing

## Run all steps

To quickly run every step of LAVA_Rust and obtain ready-to-fuzz targets, simply use the scripts `setup.sh` and `execute.sh`:

```console
$ docker exec -it panda bash
$ cd /app/elf_test

# Clone the crates where we will inject bugs, and apply patches
$ ./setup.sh

# Execute: analysis, injection, fuzzing setup
# This runs:
#  - panda.py: dynamic taint analysis
#  - parse_logs.py: extract attack points as assembly lines from the logs
#  - addr2line: find source location corresponding to the attack points
#  - inject.py: inject the bug at the attack point
#  - make_fuzz_targets.py: create full Rust projects with the corrupted source file, and the necessary setup for fuzzing.
$ ./execute.sh

# Each subdirectory in `bug_fuzz_collection` is now a Rust project with a bug injected 
$ ls bug_fuzz_collection
bug0 bug1 bug2 ...
# The file info.txt describes the location of the injected bug (original file and line)
$ cat bug_fuzz_collection/bug0/info.txt
/app/elf_test/app/rust-elf/src/lib.rs
102
```

It is now possible to run the fuzzers: you may choose between AFL.rs or libFuzzer. You may exit Docker and run these on the host operating system. You may change the timeout variable in both fuzzing scripts to control how much time is spent on each bug at most.

NOTE: You __need__ to be in the directory `elf_test` (or `svgcleaner_test`) when running the scripts.

```console
# 1. libFuzzer

# Install cargo fuzz
$ cargo install cargo-fuzz

# Run the fuzzer on all the injected bugs
# Need to pass the location of the program with the fuzzing entrypoint __in the sources__
$ cd lava_rust/elf_test
$ python3 ../lava-scripts/try_fuzz_all.py app/rust-readelf
INFO:root: Fuzzing bug16 ...
INFO:root: attempt 0 ...
...
...
thread '<unnamed>' panicked at 'Bug found', /home/vogier/Documents/Polytechnique-git/ast/elf_test/bug_fuzzing_collection/bug16/rust-elf/src/lib.rs:143:25                      
INFO:root: Bug found for bug16
INFO:root: Fuzzing bug21 ...
...
...
INFO:root: Done fuzzing. 16 / 42 successes.
INFO:root: Average time to find a bug: 60.41580296168751s
INFO:root: Average time before giving up: 123.23385356896156es



# 2. AFL.rs

# Install AFL.rs
$ cargo install afl

# Run the fuzzer on all the injected bugs
# Need to pass:
# - the location of the program with the fuzzing entrypoint __in the sources__
# - the name of the binary and the arguments to pass (excluding the filename)
$ python3 ../lava-scripts/try_fuzz_all_afl.py app/rust-readelf "rust-readelf -h -f @@"
Fuzzing bug16 ...                                                                                                     
Build executable to test...                                                                                           
binary is /home/vogier/Documents/Polytechnique-git/ast/elf_test/bug_fuzzing_collection/bug16/rust-readelf/target/debug/rust-readelf                                                                                        Build the fuzz target...
Start watcher and fuzzer...
Running crashfile:
memory allocation of 3401614098432 bytes failed
Crash is not our bug
...
Running crashfile:                  
thread 'main' panicked at 'Bug found', /home/vogier/Documents/Polytechnique-git/ast/elf_test/bug_fuzzing_collection/bug16/rust-elf/src/lib.rs:143:25
Bug found for bug16 !
Fuzzing bug21 ...
...
```



## Svgcleaner

Similarly, it is possible to inject bugs in svgcleaner and fuzz them

```console
$ docker exec -it panda bash
$ cd /app/svgcleaner_test
$ ./setup.sh
$ ./execute.sh

# libfuzzer
$ python3 ../lava-scripts/try_fuzz_all.py app/svgcleaner

# AFL
$ ../lava-scripts/try_fuzz_all_afl.py app/svgcleaner "svgcleaner @@ out.svg"
```