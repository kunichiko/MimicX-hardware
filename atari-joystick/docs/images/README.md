# atari-joystick — images

`render-top.png` / `render-bottom.png` are generated from the KiCad layout:

```sh
kicad-cli pcb render --side top --quality high --width 1400 --height 1400 \
    --rotate "0,0,90" --zoom 0.8 \
    -o atari-joystick/docs/images/render-top.png \
    atari-joystick/layouts/default/default.kicad_pcb
```

(`kicad-cli` lives inside the app bundle on macOS:
`/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`.)

Photographs of the assembled board go here too. Use these names so the links in
`../../README.md` resolve without further edits:

| file | what |
|---|---|
| `photo-top.jpg` | assembled board, component side |
| `photo-bottom.jpg` | assembled board, solder side |
| `photo-in-use.jpg` | plugged into the real machine |

Keep each one under ~1 MB (1600 px on the long edge is plenty for a README).
