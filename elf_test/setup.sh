#!/usr/bin/env bash

(
  cd app
  git clone https://github.com/cole14/rust-elf.git
  git clone https://github.com/cole14/rust-readelf.git

  # replace unrecoverable panics by recoverable Err()
  patch rust-elf/src/utils.rs utils.patch

  # add fuzzing entrypoint in executable
  patch  rust-readelf/src/rust-readelf.rs readelf.patch
)

# Make rust-readelf build against the local version of rust-elf
# and expose main_entrypoint() as a library function
cp -f Cargo_rust-readelf.toml app/rust-readelf/Cargo.toml

(
  # Build rust readelf (and rust elf)
  cd app/rust-readelf
  RUSTFLAGS="-g -C target-feature=+crt-static" cargo build --target x86_64-unknown-linux-gnu
)
