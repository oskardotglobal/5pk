{
  inputs.flakelight.url = "github:nix-community/flakelight";

  outputs =
    {
      flakelight,
      ...
    }:
    flakelight ./. {
      systems = [
        "x86_64-linux"
        "aarch64-darwin"
      ];

      formatter = pkgs: pkgs.nixfmt-rfc-style;

      devShell =
        pkgs:
        let
          simple-disk-benchmark = pkgs.callPackage (
            {
              lib,
              rustPlatform,
              fetchFromGitHub,
              system,
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

              cargoHash = "sha256-CCRK+vNZYpU4WLxU77AToKe1sgK5/cSe88Gmz3CZMAc=";

              meta = {
                description = "A simple disk benchmark tool";
                homepage = "https://github.com/schwa/simple-disk-benchmark-rs";
                license = [ lib.licenses.mit ];
                mainProgram = "simple-disk-benchmark";
              };
            }
          ) { };
          libraryPath = pkgs.lib.makeLibraryPath (
            with pkgs;
            [
              zlib
              zstd
              stdenv.cc.cc
              curl
              openssl
              attr
              libssh
              bzip2
              libxml2
              acl
              libsodium
              util-linux
              xz
            ]
          );
        in
        {
          env = pkgs.lib.mkIf (pkgs.system != "aarch64-darwin") {
            LD_LIBRARY_PATH = libraryPath;
          };

          packages = with pkgs; [
            simple-disk-benchmark
            nushell
            python313
            python313Packages.uv
            python313Packages.hatchling
          ];
        };
    };
}
