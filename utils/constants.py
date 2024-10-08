# 旋转类型
class RotationType:
    RT_WHD = 0
    RT_HWD = 1
    RT_HDW = 2
    RT_DHW = 3
    RT_DWH = 4
    RT_WDH = 5

    ALL = [RT_WHD, RT_HWD, RT_HDW, RT_DHW, RT_DWH, RT_WDH]
    Notupdown = [RT_WHD, RT_HWD]


# 放置方向，三个方向
class Axis:
    WIDTH = 0
    HEIGHT = 1
    DEPTH = 2

    ALL = [WIDTH, HEIGHT, DEPTH]


# 小数位数
DEFAULT_NUMBER_OF_DECIMALS = 0

# 初始位置
START_POSITION = [0, 0, 0]
