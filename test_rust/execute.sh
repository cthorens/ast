cd app
rustc -g -C target-feature=+crt-static main.rs
cd ..
python3 panda.py
python3 parse_logs.py main

cat addr.txt | addr2line -e app/main | sort --unique | grep test_rust > lines.txt

python3 inject.py
