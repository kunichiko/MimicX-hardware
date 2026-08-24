# x68000-keyboard — images

`render-top.png` / `render-bottom.png` are generated from the KiCad layout:

```sh
kicad-cli pcb render --side top --quality high --width 1400 --height 1400 \
    --rotate "0,0,90" --zoom 0.8 \
    -o x68000-keyboard/docs/images/render-top.png \
    x68000-keyboard/layouts/default/default.kicad_pcb
```

(`kicad-cli` lives inside the app bundle on macOS:
`/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`.)

Photographs of the assembled board go here too. Use these names so the links in
`../../README.md` resolve without further edits:

| file | what |
|---|---|
| `x68000-keyboard-photo.jpg` | assembled board next to its 3D-printed shell (in use) |
| `x68000-keyboard-photo-in-use.jpg` | plugged into the real machine (not taken yet) |

Keep each one under ~1 MB (1600 px on the long edge is plenty for a README).
