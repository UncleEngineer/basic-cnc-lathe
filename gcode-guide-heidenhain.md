# 📋 คู่มือการเขียน G-Code สไตล์ Heidenhain (TNC)

> รวมข้อมูลจากไฟล์ `.hnc` จริง + เอกสาร Heidenhain Official  
> ครอบคลุมตั้งแต่พื้นฐานถึง Cycle · Radius Comp · Arc · M-Code เต็ม

---

## สารบัญ

1. [โครงสร้างโปรแกรม](#1-โครงสร้างโปรแกรม)
2. [Header — บรรทัด 0–2](#2-header--บรรทัด-02)
3. [Tool DEF & CALL](#3-tool-def--call)
4. [Start-up Sequence](#4-start-up-sequence)
5. [การเคลื่อนที่ (L Command)](#5-การเคลื่อนที่-l-command)
6. [Radius Compensation](#6-radius-compensation)
7. [Arc / Circle](#7-arc--circle)
8. [Peck Drilling (Manual)](#8-peck-drilling-manual)
9. [CYCL DEF — Drilling Cycles](#9-cycl-def--drilling-cycles)
10. [M-Code รายการเต็ม](#10-m-code-รายการเต็ม)
11. [ISO G-Code ของ Heidenhain](#11-iso-g-code-ของ-heidenhain)
12. [LBL Subroutines](#12-lbl-subroutines)
13. [Templates พร้อมใช้](#13-templates-พร้อมใช้)
14. [กฎสำคัญ (สรุปรวม)](#14-กฎสำคัญ-สรุปรวม)

---

## 1. โครงสร้างโปรแกรม

Heidenhain ใช้ภาษา **Conversational** (ภาษาธรรมดา) แทน G-code มาตรฐาน — อ่านง่ายกว่า Fanuc/Siemens มาก แต่ก็รองรับ ISO G-code ได้เช่นกัน

```
① BEGIN PGM / BLK FORM   ── ประกาศโปรแกรม & Workpiece   (บรรทัด 0–2)
② TOOL DEF / TOOL CALL   ── กำหนดและเรียก Tool           (บรรทัด 3–4)
③ Start-up               ── ยก Z · เปิด Spindle · Coolant (บรรทัด 5–7)
④ Machining              ── เคลื่อนที่ / เจาะ / กัด       (บรรทัด 10+ นับ +2)
⑤ End                    ── ยก Z · M2 · END PGM
```

> 💡 **จุดเด่น Heidenhain vs Fanuc:** ใช้ `L` แทน G01 · `CC`+`C` แทน G02/G03 · `CYCL DEF` แทน Canned Cycle

---

## 2. Header — บรรทัด 0–2

```
0 BEGIN PGM 7227 MM
1 BLK FORM 0.1 Z X+0 Y+0 Z-50
2 BLK FORM 0.2 X+100 Y+100 Z+0
```

| คำสั่ง | ความหมาย | หมายเหตุ |
|--------|----------|----------|
| `BEGIN PGM [N] MM` | เริ่มโปรแกรม N หน่วย mm | ใช้ `INCH` แทน `MM` ได้ |
| `BLK FORM 0.1 Z X.. Y.. Z..` | มุมล่าง-ซ้าย ของ Workpiece | สำหรับ simulation |
| `BLK FORM 0.2 X.. Y.. Z..` | มุมบน-ขวา ของ Workpiece | `Z+0` = ผิวหน้าชิ้นงาน |
| `END PGM [N] MM` | จบโปรแกรม | N ต้องตรงกับ BEGIN |

---

## 3. Tool DEF & CALL

```
3 TOOL DEF 1 L+0 R+3       ; นิยาม Tool 1: ความยาว +0, รัศมี +3mm
4 TOOL CALL 1 Z S2000       ; เรียก Tool 1 แกน Z ความเร็ว 2000 RPM
```

### TOOL DEF Parameters

| Parameter | ความหมาย |
|-----------|----------|
| `[N]` | หมายเลข Tool (1–32767) |
| `L+0` | Tool length offset |
| `R+[n]` | Tool radius (mm) |

### TOOL CALL Parameters

| Parameter | ความหมาย |
|-----------|----------|
| `[N]` | หมายเลข Tool |
| `Z` | แกน Spindle |
| `S[rpm]` | ความเร็วรอบ |
| `DR+[n]` | Delta radius (ปรับ offset เล็กน้อย) |

### 📐 ขนาดดอกเจาะ (R → Ø)

| R | Ø |
|---|---|
| R+2.25 | Ø4.5 mm |
| R+2.5  | Ø5 mm   |
| R+3    | Ø6 mm   |
| R+3.5  | Ø7 mm   |
| R+3.75 | Ø7.5 mm |
| R+4    | Ø8 mm   |
| R+5    | Ø10 mm  |

> ⚠️ `TOOL CALL 0 Z` = ไม่มี Tool — ใช้ก่อน M6 เพื่อปล่อย Spindle

---

## 4. Start-up Sequence

**ตายตัว 3 บรรทัด — ห้ามเปลี่ยน**

```
5 L Z+50 R0 F10000 M3    ; ยก Z safe · ยกเลิก comp · เปิด Spindle CW
6 L X-2 Y-2 F10000       ; ไปตำแหน่งนอกชิ้นงาน (Spindle เสถียร)
7 L Z+50 F1000 M8        ; ยืนยัน Z+50 · เปิด Coolant
```

### การนับบรรทัด

| ช่วง | ลำดับ | หมายเหตุ |
|------|-------|----------|
| 0–7 | +1 | Header + Tool + Start-up |
| 10 เป็นต้นไป | +2 | กระโดดข้าม 8, 9 เสมอ |

> 💡 `FMAX` ใช้แทน `F10000` ได้ในเครื่อง TNC รุ่นใหม่ — หมายถึง Rapid traverse สูงสุดของเครื่อง

---

## 5. การเคลื่อนที่ (L Command)

`L` = Linear move เทียบเท่า G01 ใน Fanuc

```
L X±value Y±value Z±value R[comp] F[feed] M[code]
```

| ส่วนประกอบ | ความหมาย | ตัวอย่าง |
|-----------|----------|---------|
| `X±n Y±n Z±n` | พิกัด Absolute | `X-312.000 Y0.000` |
| `IX±n IY±n IZ±n` | Incremental (เพิ่มจากตำแหน่งปัจจุบัน) | `IX+50` |
| `R0 / RL / RR` | Radius comp: ยกเลิก / ซ้าย / ขวา | `RL F500` |
| `F[n]` | Feed rate (ว่าง = ใช้ค่าเดิม) | `F1000` หรือ `FMAX` |
| `M[n]` | M-code ทำงานพร้อมกัน | `M3` |

### ⬆️ ลำดับ Z ที่ใช้บ่อย

| Z | ชื่อ | ใช้เมื่อ |
|---|------|---------|
| `Z+50` | Safe Height | เริ่ม/จบโปรแกรม |
| `Z30.000` | Clearance สูง | ระหว่างรู — เจาะตื้น |
| `Z10.000` | Clearance ต่ำ | ระหว่างรู — เจาะลึก |
| `Z3.000` | Approach / Retract Peck | ก่อนเจาะ / ระหว่าง Peck |
| `Z-n.nnn` | Cutting Depth | ค่าลบ = เข้าชิ้นงาน |

---

## 6. Radius Compensation

| Code | Fanuc เทียบ | ความหมาย |
|------|------------|----------|
| `R0` | G40 | ยกเลิก compensation |
| `RL` | G41 | ชดเชยรัศมีทางซ้าย |
| `RR` | G42 | ชดเชยรัศมีทางขวา |

```
10 L X+50 Y+75 RL F500    ; เริ่ม compensation (เข้า contour)
12 L X+100 Y+75            ; กัดไปตาม contour
14 L X+100 Y+25
16 L X+50 Y+25
18 L X+50 Y+50 R0          ; ยกเลิก compensation
```

> 📌 **การเจาะรู:** ใช้แค่ `R0` — ไม่ต้องการ radius comp สำหรับ plunge drilling

### Approach & Depart Contour

| Code | ความหมาย |
|------|----------|
| `G26 R[n]` | Tangential approach เข้า contour |
| `G27 R[n]` | Tangential depart ออกจาก contour |

---

## 7. Arc / Circle

Heidenhain ใช้ `CC` กำหนดจุดศูนย์กลาง + `C` สำหรับ Arc

```
10 CC X+50 Y+50             ; กำหนดจุดศูนย์กลาง
12 L X+50 Y+75 RL F500      ; เคลื่อนไปจุดเริ่ม arc
14 C X+75 Y+50 DR+           ; arc CW ไป X75 Y50 (DR+ = CW)
16 C X+50 Y+25 DR+
18 C X+25 Y+50 DR+
20 C X+50 Y+75 DR+           ; ครบวงกลม
```

| คำสั่ง | ความหมาย | Fanuc เทียบ |
|--------|----------|------------|
| `CC X.. Y..` | กำหนดจุดศูนย์กลาง | — (ใช้ I, J ใน G02/G03) |
| `C X.. Y.. DR+` | Arc CW | G02 |
| `C X.. Y.. DR-` | Arc CCW | G03 |
| `CR X.. Y.. R±n` | Arc ระบุ Radius โดยตรง | G02/G03 + R |

### ✂️ Chamfer และ Corner Rounding

```
12 L X+100 CHF 5             ; ตัดมุม 5mm
14 L Y+80 RND R8             ; Round มุม R8
```

---

## 8. Peck Drilling (Manual)

### 8.1 Single Peck — ตื้น (<5mm)

```
10 L X-312.000 Y0.000 F1000  ; ไปตำแหน่งรู XY
12 L Z30.000 F               ; Clearance Z30
14 L Z3.000 F                ; Approach Z+3
16 L Z-3.000 F80             ; เจาะ (F80 = Cutting feed)
18 L Z30.000 F               ; Retract → รูถัดไป
```

### 8.2 Multi Peck — ลึก (>5mm) · 5mm/Peck · ตัวอย่าง 28mm

```
10 L X[X] Y[Y] F1000
12 L Z10.000 F               ; Clearance
14 L Z3.000 F                ; Approach
16 L Z-2.000 F80             ; Peck 1  ──┐
18 L Z3.000 F                ; Retract   │
20 L Z-2.000 F               ; กลับลง   │ pattern ซ้ำ
22 L Z-7.000 F               ; Peck 2    │ +5mm ต่อ Peck
24 L Z3.000 F                ;           │
26 L Z-7.000 F               ;           │
28 L Z-12.000 F              ; Peck 3  ──┘
   ...
52 L Z-28.000 F              ; Final depth
54 L Z10.000 F               ; Retract → รูถัดไป
```

> 📐 **สูตร Z sequence:** `-2 → +3 → -2 → -7 → +3 → -7 → -12 → +3 → -12 → -17 ...`

---

## 9. CYCL DEF — Drilling Cycles

### 9.1 Cycle 200 — Drilling

```
10 CYCL DEF 200 DRILLING
     Q200=3        ; Set-up clearance (mm เหนือผิว)
     Q201=-28      ; Depth (ค่าลบ)
     Q206=80       ; Feed rate เจาะ
     Q202=5        ; Plunging depth per peck
     Q210=0        ; Dwell time ด้านบน (วินาที)
     Q203=+0       ; Z ผิวชิ้นงาน
     Q204=50       ; 2nd set-up clearance
     Q211=0        ; Dwell time ที่ความลึก

20 L X-99.750 Y40.000 FMAX M89   ; ไปรู + เรียก Cycle
22 L X99.750 Y-40.000 FMAX        ; รูถัดไป (Cycle อัตโนมัติ)
24 L Z+50 FMAX M30                ; ยกเลิก M89 · จบ
```

### 9.2 Cycle 205 — Universal Pecking

```
10 CYCL DEF 205 UNIVERSAL PECKING
     Q200=3        ; Set-up clearance
     Q201=-28      ; Depth
     Q206=80       ; Feed rate plunging
     Q202=5        ; Max plunging depth
     Q258=0.1      ; Upper advanced stop distance
     Q259=1        ; Lower advanced stop distance
     Q203=+0       ; Z surface
     Q204=50       ; 2nd set-up clearance
     Q257=5        ; Depth for chip breaking
     Q256=0.2      ; Retract distance for chip breaking
     Q211=0.2      ; Dwell time at depth
```

### 9.3 รายการ Drilling Cycles

| Cycle | ชื่อ | ใช้สำหรับ |
|-------|------|----------|
| `CYCL DEF 200` | Drilling | เจาะตรงธรรมดา |
| `CYCL DEF 201` | Reaming | คว้านรู |
| `CYCL DEF 202` | Boring | คว้านรูละเอียด |
| `CYCL DEF 203` | Universal Drilling | เจาะพร้อม chip breaking |
| `CYCL DEF 205` | Universal Pecking | เจาะลึก Peck อัตโนมัติ |
| `CYCL DEF 206` | Tapping (floating) | ต๊าปด้วย floating holder |
| `CYCL DEF 207` | Rigid Tapping | ต๊าปแบบ Rigid |
| `CYCL DEF 240` | Centering | เจาะนำศูนย์ |

### 9.4 Pattern Cycles

| Cycle | ชื่อ | ใช้สำหรับ |
|-------|------|----------|
| `CYCL DEF 220` | Circular Pattern | วนเจาะเป็นวงกลม (Bolt circle) |
| `CYCL DEF 221` | Linear Pattern | เจาะเป็นแถวตรง |

```
; ตัวอย่าง Bolt Circle — 4 รู บน PCD Ø200
10 CYCL DEF 220 CIRCULAR PATTERN
     Q216=+0       ; Center X
     Q217=+0       ; Center Y
     Q244=200      ; PCD diameter
     Q245=+0       ; Start angle
     Q246=+360     ; End angle
     Q247=+90      ; Angular step (90° × 4 = 360°)
     Q241=4        ; จำนวนรู
     Q200=3        ; Set-up clearance
     Q203=+0       ; Surface Z
     Q204=50       ; 2nd clearance
     Q301=+1       ; Move to clearance (1=yes)
```

---

## 10. M-Code รายการเต็ม

### M-Code พื้นฐาน

| M-Code | ความหมาย | หมายเหตุ |
|--------|----------|---------|
| `M0` | หยุดโปรแกรม (Spindle STOP · Coolant OFF) | กด Start เพื่อดำเนินต่อ |
| `M1` | Optional STOP | หยุดเฉพาะเมื่อเปิด opt. stop |
| `M2` ⭐ | จบโปรแกรม (Spindle STOP · Coolant OFF · กลับ block 1) | ใช้ในทุกไฟล์ |
| `M3` ⭐ | เปิด Spindle หมุน CW | บรรทัด 5 |
| `M4` | เปิด Spindle หมุน CCW | |
| `M5` | หยุด Spindle | |
| `M6` | เปลี่ยน Tool (Spindle STOP) | ต้องใช้ TOOL CALL ก่อน |
| `M8` ⭐ | เปิด Coolant | บรรทัด 7 |
| `M9` | ปิด Coolant | |
| `M13` | Spindle CW + Coolant ON พร้อมกัน | แทน M3+M8 |
| `M14` | Spindle CCW + Coolant ON พร้อมกัน | |
| `M30` | เหมือน M2 | |

⭐ = ใช้บ่อยในไฟล์ `.hnc` ที่วิเคราะห์

### M-Code ขั้นสูง

| M-Code | ความหมาย |
|--------|----------|
| `M89` | Cycle call แบบ Modal (ทำงานทุกครั้งที่มี L command) |
| `M91` | พิกัดในบรรทัดนั้นอ้างอิง Machine datum |
| `M92` | พิกัดอ้างอิงตำแหน่ง tool change |
| `M99` | Cycle call แบบ Non-modal (ทำครั้งเดียว) |
| `M103` | ลด feed rate ขณะ plunge ตาม factor % |
| `M109/M110` | Constant contouring speed ที่ cutting edge |
| `M118` | Superimpose handwheel ระหว่าง program run |
| `M120` | Look-ahead สำหรับ radius compensation |
| `M128` | TCPM — รักษาตำแหน่ง tool tip เมื่อหมุนแกน |
| `M140` | Retract ออกจาก contour ในทิศแกน tool |
| `M148` | Retract tool อัตโนมัติเมื่อ NC stop |

---

## 11. ISO G-Code ของ Heidenhain

### การเคลื่อนที่

| G-Code | ความหมาย |
|--------|----------|
| `G00` | Rapid traverse |
| `G01` | Linear interpolation |
| `G02` | Circular CW |
| `G03` | Circular CCW |
| `G10` | Rapid traverse (Polar) |
| `G11` | Linear (Polar) |
| `G12/G13` | Circular CW/CCW (Polar) |

### Radius Compensation

| G-Code | ความหมาย |
|--------|----------|
| `G40` | ยกเลิก comp (= R0) |
| `G41` | ชดเชยซ้าย (= RL) |
| `G42` | ชดเชยขวา (= RR) |
| `G24 R[n]` | Chamfer |
| `G25 R[n]` | Corner rounding |
| `G26 R[n]` | Approach contour |
| `G27 R[n]` | Depart contour |

### Drilling Cycles (ISO)

| G-Code | ความหมาย |
|--------|----------|
| `G83` | Pecking |
| `G84` | Tapping (floating) |
| `G85` | Rigid tapping |
| `G200` | Drilling |
| `G203` | Universal drilling |
| `G205` | Universal pecking |
| `G220` | Circular pattern |
| `G221` | Linear pattern |

### Coordinate & Unit

| G-Code | ความหมาย |
|--------|----------|
| `G90` | Absolute dimensions |
| `G91` | Incremental dimensions |
| `G70` | Inches |
| `G71` | Millimeters |
| `G17` | Working plane XY / tool Z |
| `G53` | Datum shift (datum table) |
| `G54` | Datum shift (in program) |
| `G73` | Rotation |
| `G72` | Scaling factor |
| `G28` | Mirror image |

---

## 12. LBL Subroutines

ใช้ `LBL` สร้าง Subroutine และ `CALL LBL` เพื่อเรียกซ้ำ — ลดการเขียน code ซ้ำๆ

```
10 L X+50 Y+30 FMAX          ; ไปรูแรก
12 CALL LBL 1                 ; เรียก subroutine เจาะ
14 L X+100 Y+30 FMAX          ; ไปรูสอง
16 CALL LBL 1
18 L Z+50 FMAX M2

20 LBL 1                      ; ── จุดเริ่มต้น Subroutine
22 L Z3.000 FMAX
24 L Z-10.000 F80
26 L Z30.000 FMAX
28 LBL 0                      ; ── จุดสิ้นสุด (LBL 0 = END)
```

### Loop ด้วย REP

```
10 CALL LBL 5 REP 4           ; เรียก LBL 5 ซ้ำ 4 ครั้ง
```

> 💡 มีรูที่มี pattern เจาะเหมือนกัน 10 รู → เขียน Subroutine 1 ชุด แล้ว `CALL LBL` 10 ครั้ง

---

## 13. Templates พร้อมใช้

### 🅐 Template A — เจาะรูตื้น (Single Peck)

```
0 BEGIN PGM XXXX MM
1 BLK FORM 0.1 Z X+0 Y+0 Z-50
2 BLK FORM 0.2 X+100 Y+100 Z+0
3 TOOL DEF 1 L+0 R+[RADIUS]
4 TOOL CALL 1 Z S2000
5 L Z+50 R0 F10000 M3
6 L X-2 Y-2 F10000
7 L Z+50 F1000 M8

10 L X[X1] Y[Y1] F1000
12 L Z30.000 F
14 L Z3.000 F
16 L Z[DEPTH] F80
18 L Z30.000 F          ; ← วนรูถัดไป: L X[X2]... → Z3 → DEPTH → Z30

XX L Z+50 R0 F10000 M2
XX END PGM XXXX MM
```

### 🅑 Template B — เจาะรูลึก (Multi Peck 28mm)

```
; ── 1 รู ลึก 28mm ── คัดลอก block นี้ซ้ำสำหรับรูถัดไป
10 L X[X1] Y[Y1] F1000
12 L Z10.000 F
14 L Z3.000 F
16 L Z-2.000 F80         ; Peck 1
18 L Z3.000 F
20 L Z-2.000 F
22 L Z-7.000 F           ; Peck 2
24 L Z3.000 F
26 L Z-7.000 F
28 L Z-12.000 F          ; Peck 3
30 L Z3.000 F
32 L Z-12.000 F
34 L Z-17.000 F          ; Peck 4
36 L Z3.000 F
38 L Z-17.000 F
40 L Z-22.000 F          ; Peck 5
42 L Z3.000 F
44 L Z-22.000 F
46 L Z-27.000 F          ; Peck 6
48 L Z3.000 F
50 L Z-27.000 F
52 L Z-28.000 F          ; Final depth
54 L Z10.000 F           ; Retract → รูถัดไป
```

### 🅒 Template C — เจาะรูลึกด้วย CYCL DEF 205 (สั้นกว่า Manual มาก)

```
0 BEGIN PGM XXXX MM
1 BLK FORM 0.1 Z X+0 Y+0 Z-50
2 BLK FORM 0.2 X+100 Y+100 Z+0
3 TOOL DEF 1 L+0 R+3
4 TOOL CALL 1 Z S2000
5 L Z+50 R0 F10000 M3
6 L X-2 Y-2 F10000
7 L Z+50 F1000 M8

10 CYCL DEF 205 UNIVERSAL PECKING
12   Q200=3
14   Q201=-28
16   Q206=80
18   Q202=5
20   Q203=+0
22   Q204=50
24   Q256=0.2  Q257=5  Q211=0

26 L X[X1] Y[Y1] FMAX M89     ; รูที่ 1
28 L X[X2] Y[Y2] FMAX          ; รูที่ 2 (Cycle ทำงานอัตโนมัติ)
30 L Z+50 FMAX M2
32 END PGM XXXX MM
```

---

## 14. กฎสำคัญ (สรุปรวม)

### ✅ ต้องทำเสมอ

- `BEGIN`/`END PGM` ใส่เลขตรงกับชื่อไฟล์
- `BLK FORM 0.1` และ `0.2` ทุกโปรแกรม
- Start-up 3 บรรทัด (5–7) ตายตัว ห้ามเปลี่ยน
- กระโดดจาก 7 → 10 นับ +2 ตลอด
- จบด้วย `L Z+50 R0 F10000 M2`
- XY ใส่ทศนิยม 3 ตำแหน่ง: `X-312.000`
- Approach ที่ `Z+3` ก่อนเจาะทุกครั้ง

### ⚡ Feed Rate Rules

| Feed | ใช้เมื่อ |
|------|---------|
| `F10000` หรือ `FMAX` | Rapid / เคลื่อนเร็ว |
| `F1000` | เคลื่อน XY ไปตำแหน่งรู |
| `F80` | Cutting feed ดอก Ø6+ |
| `F70` | Cutting feed ดอกเล็กกว่า Ø6 |
| `F` (ว่าง) | ใช้ Feed ล่าสุด |

> Peck แรกต้องใส่ F ทุกครั้ง

### 🚫 ห้ามทำ

- ห้ามเปลี่ยน S — ใช้ `S2000` เสมอ
- ห้ามใส่ `RL`/`RR` ระหว่างเจาะ — ใช้ `R0` เท่านั้น
- ห้ามเคลื่อน X/Y ขณะ Z อยู่ในชิ้นงาน
- Retract Peck ต้องขึ้น `Z+3` (ไม่ใช่ Z10/Z30)

### 💡 เคล็ดลับ

- ใช้ `CYCL DEF 205` แทน Manual Peck สำหรับโปรแกรมใหม่ — สั้นกว่ามาก
- ใช้ `LBL` Subroutine สำหรับรูที่มี pattern เหมือนกัน
- `FMAX` ปลอดภัยกว่า `F10000` เพราะปรับตามเครื่องอัตโนมัติ
- `M13` = `M3`+`M8` รวมกัน ใช้แทนได้

### 🔄 เปรียบเทียบ Heidenhain vs Fanuc

| การทำงาน | Heidenhain | Fanuc |
|----------|-----------|-------|
| เคลื่อนตรง | `L X+50 Y+30 F500` | `G01 X50. Y30. F500` |
| Rapid | `L X+50 FMAX` | `G00 X50.` |
| Arc CW | `CC X+50 Y+50` + `C X+75 Y+25 DR+` | `G02 X75. Y25. I50. J50.` |
| R Comp ซ้าย | `RL` | `G41` |
| R Comp ยกเลิก | `R0` | `G40` |
| Spindle ON CW | `M3` | `M03` |
| Coolant ON | `M8` | `M08` |
| จบโปรแกรม | `M2` | `M30` |
| Peck Drill | `CYCL DEF 205` | `G83` |

---

*วิเคราะห์จากไฟล์ .hnc จริง 14 ไฟล์ + Heidenhain Official Documentation (Helman CNC · Klartext Portal)*
