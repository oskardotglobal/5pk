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
      version = "0.1.9";

      src = fetchFromGitHub {
        owner = "schwa";
        repo = "simple-disk-benchmark-rs";
        rev = version;
        hash = "sha256-fpfZVtAII4Y2SJhcmhtP1ZkN4yXIQ31vhvjo/p24r/Q=";
      };
      cargoHash = "sha256-gnSWIL9Nz9TmnxRRJqdwfAyGgTxtq98jP2lwkQkFE90=";

      nativeBuildInputs = [ ];
      buildInputs = [ ]; # lib.optionals stdenv.hostPlatform.isDarwin [ apple-sdk_11 ];

      meta = {
        description = " A simple disk benchmark tool";
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
