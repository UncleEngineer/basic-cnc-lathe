# CNC Lathe G-code Example

# Objective

ตัวอย่างโปรแกรม CNC Lathe สำหรับ:

- ชิ้นงานเริ่มต้น DIA 50 mm
- ต้องการปอกผิว OD
- กลึงยาว 30 mm
- ให้เหลือ DIA 40 mm
- ใช้ G71 Roughing Cycle
- กินลึกครั้งละ 0.2 mm

# Machine Controller

- FANUC 0T
- FANUC Lathe Control
- เครื่องกลึง CNC ทั่วไป

# G-code Program

```gcode
%
O1001

G21
G18
G40
G99

T0101

G97 S800 M03
M08

G00 X52 Z2

G71 U0.2 R0.5
G71 P100 Q200 U0.2 W0.1 F0.25

N100
G00 X40 Z0
G01 Z-30

N200

G70 P100 Q200

G00 X100 Z100

M09
M05
M30
%
```

# Program Explanation

## G21

```gcode
G21
```

ใช้หน่วยเป็น millimeter

---

## G18

```gcode
G18
```

เลือก Plane แบบ XZ สำหรับเครื่องกลึง

---

## G40

```gcode
G40
```

ยกเลิก Tool Nose Compensation

---

## G99

```gcode
G99
```

Feed แบบ mm/rev

---

## T0101

```gcode
T0101
```

เรียกมีด Tool 1 และ Offset 1

---

## G97 S800 M03

```gcode
G97 S800 M03
```

- G97 = ใช้รอบ spindle คงที่
- S800 = 800 RPM
- M03 = spindle หมุนตามเข็มนาฬิกา

---

## M08

```gcode
M08
```

เปิด coolant

---

## G00 X52 Z2

```gcode
G00 X52 Z2
```

วิ่งเร็วไปตำแหน่งเริ่มต้นก่อนเข้ากลึง

- X52 = สูงกว่าผิวงาน
- Z2 = อยู่หน้าชิ้นงาน 2 mm

---

# G71 Roughing Cycle

## G71 U0.2 R0.5

```gcode
G71 U0.2 R0.5
```

ความหมาย:

- G71 = Rough Turning Cycle
- U0.2 = กินลึกครั้งละ 0.2 mm
- R0.5 = retract มีดกลับ 0.5 mm หลังจบแต่ละ pass

---

## G71 P100 Q200 U0.2 W0.1 F0.25

```gcode
G71 P100 Q200 U0.2 W0.1 F0.25
```

รายละเอียด:

- P100 = เริ่มอ่าน profile ที่ N100
- Q200 = จบ profile ที่ N200
- U0.2 = เหลือ allowance ด้าน X สำหรับ finish
- W0.1 = เหลือ allowance ด้าน Z สำหรับ finish
- F0.25 = feed 0.25 mm/rev

---

# Profile Definition

## N100

```gcode
N100
G00 X40 Z0
```

เริ่ม profile งาน

เครื่องจะเข้าใจว่าต้องกลึง OD ให้เหลือ DIA 40

---

## G01 Z-30

```gcode
G01 Z-30
```

กลึงยาว 30 mm

ช่วง Z0 ถึง Z-30 จะถูกปอกให้เหลือ DIA 40

---

## N200

```gcode
N200
```

จุดจบของ profile

---

# G70 Finish Cycle

```gcode
G70 P100 Q200
```

Finish profile อีกรอบเพื่อเก็บผิวงานให้เรียบ

---

# End Program

## ถอนมีด

```gcode
G00 X100 Z100
```

ถอนมีดออกจากชิ้นงาน

---

## ปิด coolant และ spindle

```gcode
M09
M05
```

- M09 = Coolant OFF
- M05 = Spindle STOP

---

## จบโปรแกรม

```gcode
M30
```

End Program

# Machining Result

จาก DIA 50 mm

เครื่องจะ rough ประมาณ:

```text
50.0
49.6
49.2
48.8
...
40.4
```

แล้ว Finish เหลือ:

```text
40.0
```

# Workpiece Shape

```text
Original Material

DIA 50
|======================|

Machined Area

|<------ 30 mm ------>|

Result:

DIA 40
|----------------------|
```

# Summary

โปรแกรมนี้ใช้ G71 Roughing Cycle เพื่อ:

- ปอกผิว OD อัตโนมัติ
- ลดขนาดจาก DIA 50 → DIA 40
- กลึงยาว 30 mm
- กินลึกครั้งละ 0.2 mm
- Finish ด้วย G70