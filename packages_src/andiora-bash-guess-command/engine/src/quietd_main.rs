fn main() {
    let mut arguments = std::env::args_os().skip(1);
    let result = match (arguments.next(), arguments.next(), arguments.next()) {
        (None, None, None) => andiora_quiet_engine::runtime::serve_stdio(),
        (Some(flag), Some(path), None) if flag == "--fixture-bin-dir" => {
            andiora_quiet_engine::runtime::serve_stdio_with_fixture_bin(path.into())
        }
        _ => {
            eprintln!("usage: andiora-quietd [--fixture-bin-dir PATH]");
            std::process::exit(2);
        }
    };
    if let Err(error) = result {
        eprintln!("andiora-quietd: {error}");
        std::process::exit(1);
    }
}
