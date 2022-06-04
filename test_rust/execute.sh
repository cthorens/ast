#!/usr/bin/env bash

SCRIPTS_DIR="$(realpath "../lava-scripts")"

NAME="test_rust"
TARGET="./target/debug/test_rust"

echo "Compile the executable..."

(
  cd app &&
  RUSTFLAGS="-g -C target-feature=+crt-static" cargo build
)


echo "Run panda dynamic analysis..."
python3 panda.py

echo "Parse logs to get tainted asm lines..."
python3 "$SCRIPTS_DIR/parse_logs.py" "$NAME"

echo "Convert tainted asm lines to src lines..."
cat addr.txt | \
  addr2line -e "app/$TARGET" |\
  sort --unique |\
  grep "$NAME" | \
  tee lines.txt

echo "Inject bugs..."
python3 "$SCRIPTS_DIR/inject.py"


echo "Make fuzz targets"
python3 "$SCRIPTS_DIR/make_fuzz_targets.py" "./app/"

bash "$SCRIPTS_DIR/make_main_public.sh" "bug_fuzzing_collection"
