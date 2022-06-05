#![no_main]
use libfuzzer_sys::fuzz_target;

use std::fs::File;
use std::io::Write;


fuzz_target!(|data: &[u8]| {    
    //println!("Fuzzing against file {}", fname);

    if data.len() < 1 { return; }

    let mut f = File::create("ls").expect("Cannot open ls for writing");
    f.write_all(&data).expect("Cannot write to ls");

    let args = ["readelf", "-f", "ls", "-h"].iter().map(|&s| s.into()).collect();

    readelf::main_entry(args);
});
