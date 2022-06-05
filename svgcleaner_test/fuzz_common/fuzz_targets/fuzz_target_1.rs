#![no_main]

extern crate svgdom;


use libfuzzer_sys::fuzz_target;

use std::fs::File;
use std::io::Write;

use svgcleaner::{
    cleaner,
    CleaningOptions,
    StyleJoinMode,
};

use svgdom::{
    Indent,
    ListSeparator,
    AttributesOrder,

    ParseOptions,
    WriteOptions,
};


fn process_file(path : &str) -> Result<(),Box<dyn std::error::Error>>
{
    let parse_opt = ParseOptions {
        parse_comments: true,
        parse_declarations: true,
        parse_unknown_elements: true,
        parse_unknown_attributes: true,
        parse_px_unit: false,
        skip_unresolved_classes: true,
        skip_invalid_attributes: false,
        skip_invalid_css: false,
        skip_paint_fallback: false,
    };

    let write_opt = WriteOptions {
        indent: Indent::Spaces(4),
        attributes_indent: Indent::None,
        use_single_quote: false,
        trim_hex_colors: false,
        write_hidden_attributes: false,
        remove_leading_zero: true,
        use_compact_path_notation: false,
        join_arc_to_flags: false,
        remove_duplicated_path_commands: false,
        use_implicit_lineto_commands: false,
        simplify_transform_matrices: false,
        list_separator: ListSeparator::Space,
        attributes_order: AttributesOrder::Alphabetical,
    };

    let cleaning_opt = CleaningOptions::default();


    let raw = cleaner::load_file(path)?;

    let input_size = raw.len();
    let mut buf = raw.into_bytes();

    let mut doc = cleaner::parse_data(std::str::from_utf8(&buf).unwrap(), &parse_opt)?;
    cleaner::clean_doc(&mut doc, &cleaning_opt, &write_opt)?;
    cleaner::write_buffer(&doc, &write_opt, &mut buf);
    cleaner::save_file(&buf[..], path)?;

    Ok(())
}

fuzz_target!(|data: String| {
    if data.len() < 1 { return; }

    let path = "test.svg";
    let mut f = File::create(path).expect("Cannot open test.svg for writing");
    f.write_all(data.as_bytes()).expect("Cannot write to test.svg");

    let _result: Result<_, _> = process_file(path);
 
});
