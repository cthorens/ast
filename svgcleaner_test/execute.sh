cd app/svgcleaner
RUSTFLAGS="-g -C target-feature=+crt-static" cargo build
cd ../..

python3 panda.py
python3 parse_logs.py svgcleaner

cat addr.txt | addr2line  -e app/svgcleaner/target/debug/svgcleaner | sort --unique | grep app > lines.txt

python3 inject.py
