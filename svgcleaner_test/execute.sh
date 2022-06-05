#!/usr/bin/env bash

SCRIPTS_DIR="$(realpath "../lava-scripts")"

echo "Compile the executable..."

(
    cd app/svgcleaner
    RUSTFLAGS="-g -C target-feature=+crt-static" cargo build
)

# panda can't handle long paths in folder to copy
rm -rf app/svgcleaner/target/debug/build

echo "Run panda dynamic analysis..."
python3 panda.py


echo "Parse logs to get tainted asm lines..."
python3 "$SCRIPTS_DIR/parse_logs.py" svgcleaner

echo "Convert tainted asm lines to src lines..."
cat addr.txt | addr2line  -e app/svgcleaner/target/x86_64-unknown-linux-gnu/debug/svgcleaner | sort --unique | grep app > lines.txt


echo "Inject bugs..."
python3 "$SCRIPTS_DIR/inject.py"
