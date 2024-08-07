import copy

import numpy as np

from py3dbp.spec.bin import Bin
from py3dbp.spec.item import Item
from utils.constants import Axis


class Packer:

    def __init__(self):
        """ """
        self.bins = []
        self.items = []
        self.unfit_items = []
        self.total_items = 0
        self.binding = []
        # self.apex = []

    def addBin(self, bin):
        """ """
        return self.bins.append(bin)

    def addItem(self, item):
        """ """
        self.total_items = len(self.items) + 1

        return self.items.append(item)

    def packBin(self, item: Item, bin: Bin, max_width, max_height, max_depth):
        """ """
        bin.fix_point = True
        bin.check_stable = True
        bin.support_surface_ratio = 0
        if not bin.items:
            return bin.putItemV2(
                item,
                [item.position],
            )
        # 正轴方向摆放
        items_in_bin = bin.items
        pivots = set()
        # 获取所有item的可放置位置
        for ib in items_in_bin:
            w, h, d = ib.getDimension()
            for axis in range(3):
                pivot = list(ib.position)  # 创建pivot的副本
                pivot[axis] += [w, h, d][axis]  # 根据不同轴更新pivot的位置
                pivots.add(tuple(pivot))  # 将pivot位置加入集合

        # 移除items_in_bin中已存在的位置
        pivots.difference_update({tuple(ib.position) for ib in items_in_bin})
        pivots = [list(p) for p in pivots]  # 将集合转换为列表，保持原有数据结构
        fit = bin.putItemV2(item, pivots, max_width, max_height, max_depth)
        return fit

    def pack2Bin(
        self, bin: Bin, item: Item, fix_point, check_stable, support_surface_ratio
    ):
        """pack item to bin"""
        fitted = False
        bin.fix_point = fix_point
        bin.check_stable = check_stable
        bin.support_surface_ratio = support_surface_ratio

        # first put item on (0,0,0) , if corner exist ,first add corner in box.
        if bin.corner != 0 and not bin.items:
            corner_lst = bin.addCorner()
            for i in range(len(corner_lst)):
                bin.putCorner(i, corner_lst[i])

        elif not bin.items:
            response = bin.putItem(item, item.position)

            if not response:
                bin.unfitted_items.append(item)
            return

        for axis in range(0, 3):
            items_in_bin = bin.items
            for ib in items_in_bin:
                pivot = [0, 0, 0]
                w, h, d = ib.getDimension()
                if axis == Axis.WIDTH:
                    pivot = [ib.position[0] + w, ib.position[1], ib.position[2]]
                elif axis == Axis.HEIGHT:
                    pivot = [ib.position[0], ib.position[1] + h, ib.position[2]]
                elif axis == Axis.DEPTH:
                    pivot = [ib.position[0], ib.position[1], ib.position[2] + d]

                if bin.putItem(item, pivot, axis):
                    fitted = True
                    break
            if fitted:
                break
        if not fitted:
            bin.unfitted_items.append(item)

    def sortBinding(self, bin):
        """sorted by binding"""
        b, front, back = [], [], []
        for i in range(len(self.binding)):
            b.append([])
            for item in self.items:
                if item.name in self.binding[i]:
                    b[i].append(item)
                elif item.name not in self.binding:
                    if len(b[0]) == 0 and item not in front:
                        front.append(item)
                    elif item not in back and item not in front:
                        back.append(item)

        min_c = min([len(i) for i in b])

        sort_bind = []
        for i in range(min_c):
            for j in range(len(b)):
                sort_bind.append(b[j][i])

        for i in b:
            for j in i:
                if j not in sort_bind:
                    self.unfit_items.append(j)

        self.items = front + sort_bind + back
        return

    def putOrder(self):
        """Arrange the order of items"""
        r = []
        for i in self.bins:
            # open top container
            if i.put_type == 2:
                i.items.sort(key=lambda item: item.position[0], reverse=False)
                i.items.sort(key=lambda item: item.position[1], reverse=False)
                i.items.sort(key=lambda item: item.position[2], reverse=False)
            # general container
            elif i.put_type == 1:
                i.items.sort(key=lambda item: item.position[1], reverse=False)
                i.items.sort(key=lambda item: item.position[2], reverse=False)
                i.items.sort(key=lambda item: item.position[0], reverse=False)
            else:
                pass
        return

    def gravityCenter(self, bin):
        """
        Deviation Of Cargo gravity distribution
        """
        w = int(bin.width)
        h = int(bin.height)
        d = int(bin.depth)

        area1 = [set(range(0, w // 2 + 1)), set(range(0, h // 2 + 1)), 0]
        area2 = [set(range(w // 2 + 1, w + 1)), set(range(0, h // 2 + 1)), 0]
        area3 = [set(range(0, w // 2 + 1)), set(range(h // 2 + 1, h + 1)), 0]
        area4 = [set(range(w // 2 + 1, w + 1)), set(range(h // 2 + 1, h + 1)), 0]
        area = [area1, area2, area3, area4]

        for i in bin.items:

            x_st = int(i.position[0])
            y_st = int(i.position[1])
            if i.rotation_type == 0:
                x_ed = int(i.position[0] + i.width)
                y_ed = int(i.position[1] + i.height)
            elif i.rotation_type == 1:
                x_ed = int(i.position[0] + i.height)
                y_ed = int(i.position[1] + i.width)
            elif i.rotation_type == 2:
                x_ed = int(i.position[0] + i.height)
                y_ed = int(i.position[1] + i.depth)
            elif i.rotation_type == 3:
                x_ed = int(i.position[0] + i.depth)
                y_ed = int(i.position[1] + i.height)
            elif i.rotation_type == 4:
                x_ed = int(i.position[0] + i.depth)
                y_ed = int(i.position[1] + i.width)
            elif i.rotation_type == 5:
                x_ed = int(i.position[0] + i.width)
                y_ed = int(i.position[1] + i.depth)

            x_set = set(range(x_st, int(x_ed) + 1))
            y_set = set(range(y_st, y_ed + 1))

            # cal gravity distribution
            for j in range(len(area)):
                if x_set.issubset(area[j][0]) and y_set.issubset(area[j][1]):
                    area[j][2] += int(i.weight)
                    break
                # include x and !include y
                elif (
                    x_set.issubset(area[j][0]) == True
                    and y_set.issubset(area[j][1]) == False
                    and len(y_set & area[j][1]) != 0
                ):
                    y = len(y_set & area[j][1]) / (y_ed - y_st) * int(i.weight)
                    area[j][2] += y
                    if j >= 2:
                        area[j - 2][2] += int(i.weight) - x
                    else:
                        area[j + 2][2] += int(i.weight) - y
                    break
                # include y and !include x
                elif (
                    x_set.issubset(area[j][0]) == False
                    and y_set.issubset(area[j][1]) == True
                    and len(x_set & area[j][0]) != 0
                ):
                    x = len(x_set & area[j][0]) / (x_ed - x_st) * int(i.weight)
                    area[j][2] += x
                    if j >= 2:
                        area[j - 2][2] += int(i.weight) - x
                    else:
                        area[j + 2][2] += int(i.weight) - x
                    break
                # !include x and !include y
                elif (
                    x_set.issubset(area[j][0]) == False
                    and y_set.issubset(area[j][1]) == False
                    and len(y_set & area[j][1]) != 0
                    and len(x_set & area[j][0]) != 0
                ):
                    all = (y_ed - y_st) * (x_ed - x_st)
                    y = len(y_set & area[0][1])
                    y_2 = y_ed - y_st - y
                    x = len(x_set & area[0][0])
                    x_2 = x_ed - x_st - x
                    area[0][2] += x * y / all * int(i.weight)
                    area[1][2] += x_2 * y / all * int(i.weight)
                    area[2][2] += x * y_2 / all * int(i.weight)
                    area[3][2] += x_2 * y_2 / all * int(i.weight)
                    break

        r = [area[0][2], area[1][2], area[2][2], area[3][2]]
        result = []
        for i in r:
            result.append(round(i / sum(r) * 100, 2))
        return result

    def find_box(
        self,
        max_height,
        max_weight,
        max_length,
        number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS,
    ) -> dict:

        for item in self.items:
            item.formatNumbers(number_of_decimals)
        # Item : sorted by volumn -> sorted by loadbear -> sorted by level -> binding
        self.items.sort(key=lambda item: item.getVolume(), reverse=True)
        # self.items.sort(key=lambda item: item.getMaxArea(), reverse=bigger_first)
        self.items.sort(key=lambda item: item.loadbear, reverse=True)
        self.items.sort(key=lambda item: item.level, reverse=False)
        box = Bin(
            "box",
            (0, 0, 0),
            max_weight=99999,
            put_type=0,
            number_of_decimals=number_of_decimals,
        )
        for item in self.items:
            fit = self.packBin(item, box, max_height, max_weight, max_length)
            if not fit:
                return {"status": False, "item": item, "box": box}
        return {"status": True, "box": box}

    def pack(
        self,
        bigger_first=False,
        distribute_items=True,
        fix_point=True,
        check_stable=True,
        gravity=False,
        support_surface_ratio=0.75,
        binding=[],
        number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS,
    ):
        """pack master func"""
        # set decimals
        for bin in self.bins:
            bin.formatNumbers(number_of_decimals)

        for item in self.items:
            item.formatNumbers(number_of_decimals)
        # add binding attribute
        self.binding = binding
        # Bin : sorted by volumn
        self.bins.sort(key=lambda bin: bin.getVolume(), reverse=bigger_first)
        # Item : sorted by volumn -> sorted by loadbear -> sorted by level -> binding
        self.items.sort(key=lambda item: item.getVolume(), reverse=bigger_first)
        # self.items.sort(key=lambda item: item.getMaxArea(), reverse=bigger_first)
        self.items.sort(key=lambda item: item.loadbear, reverse=True)
        self.items.sort(key=lambda item: item.level, reverse=False)
        # sorted by binding
        if binding != []:
            self.sortBinding(bin)

        for idx, bin in enumerate(self.bins):
            # pack item to bin
            for item in self.items:
                self.pack2Bin(bin, item, fix_point, check_stable, support_surface_ratio)

            if binding != []:
                # resorted
                self.items.sort(key=lambda item: item.getVolume(), reverse=bigger_first)
                self.items.sort(key=lambda item: item.loadbear, reverse=True)
                self.items.sort(key=lambda item: item.level, reverse=False)
                # clear bin
                bin.items = []
                bin.unfitted_items = self.unfit_items
                bin.fit_items = np.array([[0, bin.width, 0, bin.height, 0, 0]])
                # repacking
                for item in self.items:
                    self.pack2Bin(
                        bin, item, fix_point, check_stable, support_surface_ratio
                    )

            # Deviation Of Cargo Gravity Center
            if gravity:
                self.bins[idx].gravity = self.gravityCenter(bin)

            if distribute_items:
                for bitem in bin.items:
                    no = bitem.partno
                    for item in self.items:
                        if item.partno == no:
                            self.items.remove(item)
                            break

        # put order of items
        self.putOrder()

        if self.items != []:
            self.unfit_items = copy.deepcopy(self.items)
            self.items = []
        # for item in self.items.copy():
        #     if item in bin.unfitted_items:
        #         self.items.remove(item)
