# Dev shell for the blog (no flakes). Usage: `nix-shell`, then `task build`.
# nixpkgs is pinned in nix/pin.json; bump it with `task nix:pin`.
let
  pin = builtins.fromJSON (builtins.readFile ./nix/pin.json);
  pkgs = import (fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/${pin.rev}.tar.gz";
    sha256 = pin.sha256;
  }) {
    config = { };
    overlays = [ ];
  };

  python = pkgs.python3.withPackages (ps: [
    ps.sphinx
    ps.myst-parser # write pages in Markdown
    ps.sphinx-design # collapsible dropdowns
    ps.furo # theme
    ps.sphinxext-opengraph # link previews when the post is shared
    ps.sphinx-autobuild # `task preview`
  ]);
in
pkgs.mkShell {
  packages = [
    python
    pkgs.go-task
    pkgs.qrencode # `task qr`
    pkgs.curl # `task nix:pin`
    pkgs.jq # `task nix:pin`
  ];
}
