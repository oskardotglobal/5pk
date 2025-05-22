{
  pkgs ? import <nixpkgs> { },
  ...
}:
let
  simple-disk-benchmark = pkgs.callPackage (
    {
      lib,
      rustPlatform,
      fetchFromGitHub,
    }:
    rustPlatform.buildRustPackage rec {
      pname = "simple-disk-benchmark";
      version = "0.1.10";

      src = fetchFromGitHub {
        owner = "schwa";
        repo = "simple-disk-benchmark-rs";
        rev = version;
        hash = "sha256-VvuSIVYv6HnAraep1zAv5wTmKNxQEPyymaEeDRz2oQg=";
      };

      cargoHash = "sha256-iRKwl3GNprlanbhNH63G1AastGPx4+hZJaGrTlYPGKA=";

      meta = {
        description = "A simple disk benchmark tool";
        homepage = "https://github.com/schwa/simple-disk-benchmark-rs";
        license = [ lib.licenses.mit ];
        mainProgram = "simple-disk-benchmark";
      };
    }
  ) { };
in
pkgs.mkShell {
  buildInputs = with pkgs; [
    simple-disk-benchmark
    nushell
    python311
    python311Packages.uv
  ];
}
