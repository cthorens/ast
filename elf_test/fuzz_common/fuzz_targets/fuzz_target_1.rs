#![no_main]
use libfuzzer_sys::fuzz_target;

use std::fs::File;
use std::io::Write;

use elf::ParseError;

fuzz_target!(|data: &[u8]| {    
    //println!("Fuzzing against file {}", fname);

    if data.len() < 1 { return; }

    let mut f = File::create("input.txt").expect("Cannot open input.txt for writing");
    f.write_all(&data).expect("Cannot write to input.txt");

    let _res : Result<(),()> = match elf::File::open_path("input.txt") {
        Ok(_f) => Ok(()),
        Err(ParseError) => Ok(()),
        Err(e) => panic!("Error: {:?}", e),
    };
});
