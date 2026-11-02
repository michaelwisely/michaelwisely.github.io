# michaelwisely.github.io

My blog, built with [Sphinx](https://www.sphinx-doc.org/). First post: the Skeleton-inator.

## Quick start

All you need is [Nix](https://nixos.org/download/) (no flakes).

```sh
nix-shell      # first run downloads the pinned packages; later runs are quick
task build     # build the site into _build/html
task preview   # live preview at http://127.0.0.1:8000, rebuilds when you save
```

Other tasks (`task --list` shows them all):

| Task | What it does |
|---|---|
| `task linkcheck` | Checks that every external link still works |
| `task qr` | Makes a printable QR code for the skeleton-inator post in `_build/qr/` (`task qr URL=...` for any other link) |
| `task clean` | Deletes `_build/` |
| `task nix:pin` | Bumps the pinned nixpkgs in `nix/pin.json` to the newest commit on its branch |

## Layout

```
shell.nix                 the dev shell (Python + Sphinx, Task, qrencode)
nix/pin.json              pinned nixpkgs (nixos-26.05)
Taskfile.yml              the tasks above
src/conf.py               Sphinx settings
src/index.md              home page and list of posts
src/posts/                one Markdown file per post, images in src/posts/img/
src/_static/custom.css    small style tweaks
.github/workflows/        publishes to GitHub Pages on push
```

## Adding a post

1. Create `src/posts/<name>.md`. Copy the top of `skeleton-inator.md` for the title, date, and description.
2. Add it to the list and the `toctree` in `src/index.md`.
3. `task preview` and check it on your phone too.

## Publishing

Pushing to `main` runs the "Publish site" GitHub Action. It builds the site in the same Nix shell and deploys it to GitHub Pages.
