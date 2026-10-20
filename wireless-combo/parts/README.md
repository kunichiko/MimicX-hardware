# wireless-combo/parts

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
Origin が **KiCad 標準ライブラリ** の部品は、フットプリントと 3D モデルが
KiCad Libraries (CC-BY-SA 4.0 + 例外条項) のコピー。シンボルとラッパ .ato は自作。
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
| `AO3401A_SOT23` | C15127 | 自作 | — |
| `CONNFLY_Elec_DS1037_09FNAKT74_0CC` | C75749 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_CONNFLY-Elec-DS1037-09FNAKT74-0CC_C75749.pdf) |
| `Everlight_Elec_19_217_GHC_YR1S2_3T` | C72043 | ベンダー由来 | — |
| `Hubei_KENTO_Elec_KT_0603G` | C12624 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_1806151818_Hubei-KENTO-Elec-KT-0603G_C12624.pdf) |
| `Hubei_KENTO_Elec_KT_0603R` | C2286 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_1810231112_Hubei-KENTO-Elec-KT-0603R_C2286.pdf) |
| `IDC_Header_2x04` | C9135 | KiCad 標準ライブラリ | — |
| `IDC_Header_2x05` | C5665 | KiCad 標準ライブラリ | — |
| `JST_XH_B3B` | C144394 | 自作 | — |
| `MountingHole_M3` | C0000000 (ダミー、非実装) | KiCad 標準ライブラリ | — |
| `MiniDIN_7P_X68000` | C0000000 | 自作 | — |
| `SS14_SMA` | C2480 | 自作 | — |
| `Samsung_Electro_Mechanics_CL05B104KO5NNNC` | C1525 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL05B104KO5NNNC_C1525.pdf) |
| `Samsung_Electro_Mechanics_CL10A475KO8NNNC` | C19666 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL10A475KO8NNNC_C19666.pdf) |
| `Samsung_Electro_Mechanics_CL21A226MAQNNNE` | C45783 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL21A226MAQNNNE_C45783.pdf) |
| `TOSHIBA_TC7MPB9307FT_EL` | C2675018 | ベンダー由来 | [PDF](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2108071630_TOSHIBA-TC7MPB9307FT-EL_C2675018.pdf) |
| `UNI_ROYAL_0402WGF1001TCE` | C11702 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010216_UNI-ROYAL-Uniroyal-Elec-0402WGF1001TCE_C11702.pdf) |
| `UNI_ROYAL_0402WGF1002TCE` | C25744 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2411221126_UNI-ROYAL-Uniroyal-Elec-0402WGF1002TCE_C25744.pdf) |
| `UNI_ROYAL_0402WGF1003TCE` | C25741 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010100_UNI-ROYAL-Uniroyal-Elec-0402WGF1003TCE_C25741.pdf) |
| `UNI_ROYAL_0402WGF4700TCE` | C25117 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2205311900_UNI-ROYAL-Uniroyal-Elec-0402WGF4700TCE_C25117.pdf) |
| `UNI_ROYAL_0402WGF4701TCE` | C25900 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010045_UNI-ROYAL-Uniroyal-Elec-0402WGF4701TCE_C25900.pdf) |
| `WCH_CH32X035G8U6` | C7437027 | ベンダー由来 | [PDF](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2404070952_WCH-Jiangsu-Qin-Heng-CH32X035G8U6_C7437027.pdf) |
| `Worldsemi_WS2812B_2020` | C965555 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2012110135_Worldsemi-WS2812B-2020_C965555.pdf) |
| `XIAO_ESP32C6` | C0000001 | 自作 | — |
| `XKB_Connectivity_TS_1187A_B_A_B` | C318884 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_XKB-Connection-TS-1187A-B-A-B_C318884.pdf) |
| `XUNPU_TS_1088_AR02016` | C720477 | ベンダー由来 | [PDF](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_XUNPU-TS-1088-AR02016_C720477.pdf) |
