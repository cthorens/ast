#!/usr/bin/env bash


NAME="test_rust"
TARGET="./target/debug/test_rust"

echo "Compile the executable..."

(
  cd app &&
  RUSTFLAGS="-g -C target-feature=+crt-static" cargo build
)


echo "Run panda dynamic analysis..."
python3 panda.py "$TARGET"

echo "Parse logs to get tainted asm lines..."
python3 parse_logs.py "$NAME"

echo "Convert tainted asm lines to src lines..."
cat addr.txt | \
  addr2line -e "app/$TARGET" |\
  sort --unique |\
  grep "$NAME" | \
  tee lines.txt

echo "Inject bugs..."
python3 inject.py
