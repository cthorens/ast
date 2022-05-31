#![no_main]
use libfuzzer_sys::fuzz_target;

use std::fs::File;
use std::io::Write;

fuzz_target!(|data: &[u8]| {
    let mut f = File::create("input.txt").expect("Cannot open input.txt for writing");
    f.write_all(&data).expect("Cannot write to input.txt");
    test_rust::main();
});
