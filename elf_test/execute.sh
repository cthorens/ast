#!/usr/bin/env bash


SCRIPTS_DIR="$(realpath "../lava-scripts")"


echo "Compile the executable..."
(
  cd app/rust-readelf &&
  RUSTFLAGS="-g -C target-feature=+crt-static" cargo build --target x86_64-unknown-linux-gnu
)

echo "Run panda dynamic analysis..."
python3 panda.py

echo "Parse logs to get tainted asm lines..."
python3 "$SCRIPTS_DIR/parse_logs.py" rust-readelf

echo "Convert tainted asm lines to src lines..."
cat addr.txt | addr2line  -e app/rust-readelf/target/x86_64-unknown-linux-gnu/debug/rust-readelf | sort --unique | grep app > lines.txt

echo "Inject bugs..."
python3 "$SCRIPTS_DIR/inject.py"

echo "Make fuzz targets"
python3 "$SCRIPTS_DIR/make_fuzz_targets.py" "./app/rust-elf"


#python3 test.py
