cd app
git clone https://github.com/cole14/rust-elf.git
git clone https://github.com/cole14/rust-readelf.git
cd ..

cp -f Cargo_rust-readelf.toml app/rust-readelf/Cargo.toml

cd app/rust-readelf
RUSTFLAGS="-g -C target-feature=+crt-static" cargo build
cd ../..
