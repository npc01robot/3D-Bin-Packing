from decimal import Decimal

import numpy as np

from .constants import Axis


def rectIntersect(item1, item2, x, y):
    d1 = item1.getDimension()
    d2 = item2.getDimension()

    cx1 = item1.position[x] + d1[x] / 2
    cy1 = item1.position[y] + d1[y] / 2
    cx2 = item2.position[x] + d2[x] / 2
    cy2 = item2.position[y] + d2[y] / 2

    ix = max(cx1, cx2) - min(cx1, cx2)
    iy = max(cy1, cy2) - min(cy1, cy2)

    return ix < (d1[x] + d2[x]) / 2 and iy < (d1[y] + d2[y]) / 2


def intersect(item1, item2):
    return (
        rectIntersect(item1, item2, Axis.WIDTH, Axis.HEIGHT)
        and rectIntersect(item1, item2, Axis.HEIGHT, Axis.DEPTH)
        and rectIntersect(item1, item2, Axis.WIDTH, Axis.DEPTH)
    )


def np_rect_intersect(item1, item2):
    # 获取物体1和物体2在各轴的范围
    x1_min, y1_min, z1_min = item1[:, 0], item1[:, 1], item1[:, 2]
    x1_max, y1_max, z1_max = item1[:, 3], item1[:, 4], item1[:, 5]

    x2_min, y2_min, z2_min = item2[:, 0], item2[:, 1], item2[:, 2]
    x2_max, y2_max, z2_max = item2[:, 3], item2[:, 4], item2[:, 5]

    # 判断是否在x, y, z轴上相交
    x_overlap = (x1_min[:, np.newaxis] < x2_max) & (x1_max[:, np.newaxis] > x2_min)
    y_overlap = (y1_min[:, np.newaxis] < y2_max) & (y1_max[:, np.newaxis] > y2_min)
    z_overlap = (z1_min[:, np.newaxis] < z2_max) & (z1_max[:, np.newaxis] > z2_min)

    # 只有在所有轴上都有重叠时，物体才相交
    return x_overlap & y_overlap & z_overlap

def np_intersect(items, to_place):
    return np_rect_intersect(to_place, items).any(axis=1)

def can_place(items, to_place):
    # 判断所有待放置物体是否与已放置物体相交
    return ~np_intersect(items, to_place)

# 示例使用
# items = np.array([
#     [0, 0, 0, 1, 1, 1, 1, 1, 1],
#     [0, 0, 1, 1, 1, 2, 1, 1, 1]
# ])
#
# to_place = np.array([[1 0 0 3 2 2 2 2 2 0 0]
#  [2 1 1 5 4 4 3 3 3 0 1]
#  [0 1 0 2 3 2 2 2 2 1 0]
#  [1 2 1 4 5 4 3 3 3 1 1]
#  [0 0 1 2 2 3 2 2 2 2 0]
#  [1 1 2 4 4 5 3 3 3 2 1]])
#
# result = can_place(items, to_place)
# print(result)  # 输出: [False, True, False]  (假设这些物体是彼此相交的)



def getLimitNumberOfDecimals(number_of_decimals):
    return Decimal("1.{}".format("0" * number_of_decimals))


def set2Decimal(value, number_of_decimals=0):
    number_of_decimals = getLimitNumberOfDecimals(number_of_decimals)

    return Decimal(value).quantize(number_of_decimals)


def calculate_standard_deviation(dimensions):
    width, height, depth = dimensions
    ratios = [depth / width, width / height, height / depth]
    min_diff = abs(min(ratios) - 1)
    max_diff = abs(max(ratios) - 1)

    # 计算差值，越接近1表示越接近正方体
    diff = 1 - (max_diff + min_diff) / 2

    return diff
