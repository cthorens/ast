#![no_main]
use libfuzzer_sys::fuzz_target;

use std::fs::File;
use std::io::Write;
use std::path::PathBuf;


fuzz_target!(|data: &[u8]| {
    if data.len() < 500 {
        return;
    }
    let fname_len = data[0] as usize;

    println!("Fname_len = {}", fname_len);

    let fname = String::from_utf8_lossy(&data[1..(1+fname_len)]);
    
    println!("Fuzzing against file {}", fname);

    let path = PathBuf::from(fname.to_string());

    let mut f = File::create(&path).expect("Cannot open input_file for writing");
    f.write_all(&data).expect("Cannot write to input.txt");


    let file = match elf::File::open_path(&path) {
        Ok(f) => f,
        Err(e) => panic!("Error: {:?}", e),
    };
});
