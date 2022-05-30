cd app/rust-readelf
RUSTFLAGS="-g -C target-feature=+crt-static" cargo build
cd ../..

python3 panda.py
python3 parse_logs.py rust-readelf

cat addr.txt | addr2line  -e app/rust-readelf/target/debug/rust-readelf | sort --unique | grep app > lines.txt

python3 inject.py
python3 test.py
