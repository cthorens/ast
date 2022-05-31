//use std::env;
use std::fs::File;
use std::io::Read;

fn main() {
    let mut f = File::open("input.txt").expect("Cannot read input.txt");
    let mut buffer = [0; 10];

    f.read(&mut buffer).unwrap();


    println!("{}", buffer[0].wrapping_add(buffer[1]));

    if buffer[0] == 0 {
        println!("{}", buffer[1]);
    }

    let add = (buffer[0] as u16).wrapping_add(buffer[1] as u16).wrapping_add(buffer[2] as u16);

    if add <= 10 {
        println!("{}", add);
    } else {
        println!("add bigger than 10 : {}", add.wrapping_add(buffer[5] as u16));
    }
}
