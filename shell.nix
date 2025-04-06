{
  pkgs ? import <nixpkgs> { },
  ...
}:
let
  simple-disk-benchmark = pkgs.callPackage (
    {
      lib,
      stdenv,
      rustPlatform,
      fetchFromGitHub,
    }:
    rustPlatform.buildRustPackage rec {
      pname = "simple-disk-benchmark";
      version = "0.1.10";

      src = fetchFromGitHub {
        owner = "oskardotglobal";
        repo = "simple-disk-benchmark-rs";
        rev = version;
        hash = "sha256-xTugrFIRIq9J/KChzD3wKg/bzdugDtLLqGwR0dbuxp0";
      };
      cargoHash = "sha256-hbGUxQyIAEDoLgW77Wbr/tmWK9Q+Iq3G18Nbf03d6/M=";

      meta = {
        description = "A simple disk benchmark tool";
        homepage = "https://github.com/schwa/simple-disk-benchmark-rs";
        license = [ lib.licenses.mit ];
        mainProgram = "simple-disk-benchmark";
      };
    }
  ) { };
in
pkgs.mkShellNoCC {
  buildInputs = with pkgs; [
    simple-disk-benchmark
    nushell
    python311
    python311Packages.uv
  ];
}
