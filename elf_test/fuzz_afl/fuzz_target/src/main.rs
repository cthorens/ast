#[macro_use]
extern crate afl;
extern crate readelf;

use std::fs::File;
use std::io::Write;

fn main() {
    fuzz!(|data: &[u8]| {

        //if data.len() < 1 { return; }

        let mut f = File::create("ls").expect("Cannot open ls for writing");
        f.write_all(&data).expect("Cannot write to ls");

        let args = ["readelf", "-f", "ls", "-h"].iter().map(|&s| s.into()).collect();

        readelf::main_entry(args);

    });
}
