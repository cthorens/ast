cd app
git clone https://github.com/RazrFalcon/svgdom.git
git clone https://github.com/RazrFalcon/svgcleaner.git
cd svgdom
git checkout 179b6c2935cc17856c1c7af8dd8898a1e562841f
cd ../..

cp -f Cargo_svgcleaner.toml app/svgcleaner/Cargo.toml

cd app/svgcleaner
RUSTFLAGS="-g -C target-feature=+crt-static" cargo build
cd ../..
