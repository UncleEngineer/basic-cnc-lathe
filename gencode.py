z_start = -2
facing_point = -0.1
retract = z_start + 2 # edit > 2
x_start = -25.5

work_diameter = 23.9
turning_length = 14
percut = 0.5 # edit here for cut
cal = int(turning_length / percut)
# next version mod for left lenght
print('กินทั้งหมด: {} รอบ'.format(cal) )
feed_rate = 50

cal_z = z_start
cal_retract = retract

for i in range(cal):
    print('G01 f{} z{}'.format(feed_rate,cal_z)) # new
    print('G01 f{} x{}'.format(feed_rate,facing_point))
    print('G00 z{}'.format(cal_retract)) # new
    print('G00 x{}'.format(x_start))
    cal_z -= percut # -2.5
    cal_retract = cal_z + 2 # -2.5 + 2 = -0.5, 
    print('(----------)')

