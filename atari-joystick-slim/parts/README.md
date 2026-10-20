# atari-joystick-slim/parts

atopile は部品ごとに 1 ディレクトリを作る。中身は 3 種類:

| ファイル | 内容 | 権利者 |
|---|---|---|
| `*.ato` | 部品を Mimic X の回路に繋ぐためのラッパ | **このプロジェクト** (CERN-OHL-S-2.0) |
| `*.kicad_sym` / `*.kicad_mod` | シンボル / フットプリント | 下表の Origin 欄 |
| `*.step` / `*.STEP` | 3D モデル | 部品ベンダー |

Origin が **ベンダー由来** の部品のシンボル・フットプリント・3D モデルは、
LCSC / EasyEDA のデータを atopile (faebryk) が変換したもの、およびそれを
KiCad で調整した派生物であり、**このリポジトリのライセンスの対象外**。
Origin が **自作** の部品はディレクトリ全体が CERN-OHL-S-2.0 の対象。
詳細はリポジトリルートの [`NOTICE`](../../NOTICE) を参照。

> KiCad の footprint editor で保存し直すと `generator` フィールドが `pcbnew` に
> 書き換わるため、**`generator` の値では由来を判別できない**。一次情報は git 履歴:
> `git log --follow -- <file>` で最初のコミットまで遡る。

## データシート

**データシート PDF はこのリポジトリに含めない** — 再配布の可否が部品メーカー
ごとに不明なため。入手先は各 `*.ato` の `has_datasheet` トレイトに URL として
書いてあり、下表はその一覧。`ato build` は必要に応じて `build/cache/` に自動で
取得する (git 管理外)。

| 部品ディレクトリ | LCSC | Origin | データシート |
|---|---|---|---|
| `DSUB9_SolderCup_Edge` | C0000000 | 自作 | — |
| `Everlight_Elec_19_217_GHC_YR1S2_3T` | C72043 | ベンダー由来 | — |
| `Hubei_KENTO_Elec_KT_0603G` | C12624 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_1806151818_Hubei-KENTO-Elec-KT-0603G_C12624.pdf) |
| `Hubei_KENTO_Elec_KT_0603R` | C2286 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_1810231112_Hubei-KENTO-Elec-KT-0603R_C2286.pdf) |
| `Korean_Hroparts_Elec_TYPE_C_31_M_12` | C165948 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2205251630_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.pdf) |
| `Samsung_Electro_Mechanics_CL05A105KA5NQNC` | C52923 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL05A105KA5NQNC_C52923.pdf) |
| `Samsung_Electro_Mechanics_CL05B104KO5NNNC` | C1525 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL05B104KO5NNNC_C1525.pdf) |
| `Samsung_Electro_Mechanics_CL10A475KO8NNNC` | C19666 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL10A475KO8NNNC_C19666.pdf) |
| `TECH_PUBLIC_LP5907MFX_3_3` | C23380874 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2406281354_TECH-PUBLIC-LP5907MFX-3-3_C23380874.pdf) |
| `TOSHIBA_TC7MPB9307FT_EL` | C2675018 | ベンダー由来 | [PDF](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2108071630_TOSHIBA-TC7MPB9307FT-EL_C2675018.pdf) |
| `UNI_ROYAL_0402WGF1001TCE` | C11702 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010216_UNI-ROYAL-Uniroyal-Elec-0402WGF1001TCE_C11702.pdf) |
| `UNI_ROYAL_0402WGF4700TCE` | C25117 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2205311900_UNI-ROYAL-Uniroyal-Elec-0402WGF4700TCE_C25117.pdf) |
| `UNI_ROYAL_0402WGF4701TCE` | C25900 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010045_UNI-ROYAL-Uniroyal-Elec-0402WGF4701TCE_C25900.pdf) |
| `UNI_ROYAL_0402WGF5101TCE` | C25905 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010045_UNI-ROYAL-Uniroyal-Elec-0402WGF5101TCE_C25905.pdf) |
| `WCH_CH32X035G8U6` | C7437027 | ベンダー由来 | [PDF](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2404070952_WCH-Jiangsu-Qin-Heng-CH32X035G8U6_C7437027.pdf) |
| `Worldsemi_WS2812B_2020` | C965555 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2012110135_Worldsemi-WS2812B-2020_C965555.pdf) |
| `XKB_Connectivity_TS_1187A_B_A_B` | C318884 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_XKB-Connection-TS-1187A-B-A-B_C318884.pdf) |
| `XUNPU_TS_1088_AR02016` | C720477 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_XUNPU-TS-1088-AR02016_C720477.pdf) |
