import math
import time
from typing import List

from py3dbp.figure.packer import Packer
from py3dbp.spec import Bin, ItemSet
from utils.constants import DEFAULT_NUMBER_OF_DECIMALS
from utils.merge_item import MergeItemTool


class Solution:
    def __init__(self, items: List[ItemSet]):
        self.items = items
        self.volume, self.side_length, self.max_side, self.min_side = (
            self.__get_init_box_size()
        )

    def __rotation_box(self, box: Bin) -> List[Bin]:
        """
        旋转箱子
        """
        from itertools import permutations

        boxs = []
        box_permutations = list(permutations([box.width, box.height, box.depth]))
        for index, box_permutation in enumerate(box_permutations):
            new_box = Bin(
                partno=box.partno + f"_rotation_{index}",
                WHD=box_permutation,
                max_weight=box.max_weight,
                put_type=box.put_type,
            )
            boxs.append(new_box)
        return boxs

    def find_box(
        self,
        max_width: float = float("inf"),
        max_height: float = float("inf"),
        max_depth: float = float("inf"),
        painting: bool = False,
        number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS,
    ) -> dict:
        """
        max_width: 箱子最大宽度
        max_height: 箱子最大高度
        max_depth: 箱子最大深度
        painting: 是否画图
        """
        total_items = 0
        pack_items = []
        for item in self.items:
            pack_items.extend(item.generate_items())
        self.packer = Packer()
        self.packer.items = pack_items
        self.packer.total_items = total_items
        result = self.packer.find_box(
            max_width, max_height, max_depth, number_of_decimals=number_of_decimals
        )
        if painting:
            from py3dbp.utils.painter import Painter

            box = result["box"]
            painter = Painter(box)
            fig = painter.plotBoxAndItems(
                title=box.partno, alpha=0.2, write_num=True, fontsize=10
            )
            fig.show()
        return result

    def pack_verify(
        self,
        bins: [Bin],
        items: List[ItemSet] = None,
        bigger_first=True,
        distribute_items=True,
        fix_point=True,
        check_stable=True,
        support_surface_ratio=0,
        binding: list = [],
        painting: bool = False,
    ):
        """
        :param  bins: 盒子大小
                bigger_first: 放置
                distribute_items=True，按顺序将物品放入箱子中，如果箱子已满，则剩余物品将继续装入下一个箱子，直到所有箱子装满或所有物品都被打包。 distribute_items=False，比较所有箱子的打包情况，即每个箱子打包所有物品，而不是剩余物品。
                fix_point 重力问题
                check_stable 稳定性
                support_surface_ratio 可支撑的面积大小
                binding： binding = [(orange,apple),(computer,hat,watch)]用来组合打包
        """

        pack_items = []
        items = items or self.items
        for item in items:
            pack_items.extend(item.generate_items())
        total_items = len(pack_items)
        packer = Packer()
        packer.bins = bins
        packer.items = pack_items
        packer.total_items = total_items
        packer.pack(
            bigger_first=bigger_first,
            distribute_items=distribute_items,
            fix_point=fix_point,
            check_stable=check_stable,
            support_surface_ratio=support_surface_ratio,
            binding=binding,
            number_of_decimals=2,
        )

        result = {}
        for box in packer.bins:
            box_name = box.partno
            result[box_name] = {}
            dic = {}
            for item in box.unfitted_items:
                dic[item.name] = dic.get(item.name, 0) + 1
            result[box_name]["unfitted_items"] = dic

            dic = {}
            for item in box.items:
                dic[item.partno] = {
                    "name": item.name,
                    "position": item.position,
                    "width": item.width,
                    "height": item.height,
                    "depth": item.depth,
                    "weight": item.weight,
                }
            result[box_name]["fitted_items"] = dic
            result[box_name]["width"] = box.width
            result[box_name]["height"] = box.height
            result[box_name]["depth"] = box.depth
            result[box_name]["weight"] = box.max_weight
            if result[box_name]["unfitted_items"]:
                result[box_name]["resolve"] = False
            else:
                result[box_name]["resolve"] = True
            if painting:
                from py3dbp.utils.painter import Painter

                painter = Painter(box)
                fig = painter.plotBoxAndItems(
                    title=box.partno, alpha=0.2, write_num=True, fontsize=10
                )
        if painting:
            fig.show()
        return result

    def __get_init_box_size(self):
        volume = 0
        max_side = 0
        min_side = float("inf")

        for item in self.items:
            # 累加计算总体积
            volume += item.width * item.height * item.depth * item.quantity

            max_side = max(max_side, item.width, item.height, item.depth)
            min_side = min(min_side, item.width, item.height, item.depth)

        # 基于总体积计算合适的箱子边长（立方根后向上取整）
        side_length = math.ceil(math.pow(volume, 1 / 3))

        return volume, side_length, max_side, min_side

    def find_box_by_min_side(
        self,
        bigger_first=True,
        fix_point=True,
        check_stable=True,
        support_surface_ratio=0,
        binding: list = [],
    ):
        """
        按最小边长合并计算箱子尺寸
        """
        # 初始化箱子尺寸字典,合并相同尺寸的物品
        merged_tools = MergeItemTool(items=self.items)

        # 计算最小箱子尺寸
        for length in range(
            self.side_length,
            max(self.max_side, self.side_length + self.side_length // 2),
        ):
            # 合并物品
            new_item_dict = merged_tools.get_merged_item(length)
            bin = Bin(
                partno="box",
                WHD=(length, length, length),
                max_weight=9999999,
                put_type=0,
            )
            items = list(new_item_dict.values())
            result = self.pack_verify(
                bins=[bin],
                items=items,
                bigger_first=bigger_first,
                distribute_items=False,
                fix_point=fix_point,
                check_stable=check_stable,
                support_surface_ratio=support_surface_ratio,
                binding=binding,
            )
            if not result[bin.partno]["resolve"]:
                continue
            else:
                return length

    def find_box_by_enum(
        self,
        bigger_first=True,
        fix_point=True,
        check_stable=True,
        support_surface_ratio=0.1,
        binding: list = [],
    ):
        """
        二分法枚举所有箱子尺寸
        """

        min_side = self.side_length
        max_side = max(self.max_side, self.side_length + self.side_length // 2)

        # 二分法
        while min_side < max_side:
            mid = (min_side + max_side) // 2
            bin = Bin(partno="box", WHD=(mid, mid, mid), max_weight=9999999, put_type=0)
            result = self.pack_verify(
                bins=[bin],
                bigger_first=bigger_first,
                distribute_items=False,
                fix_point=fix_point,
                check_stable=check_stable,
                support_surface_ratio=support_surface_ratio,
                binding=binding,
            )
            if not result[bin.partno]["resolve"]:
                min_side = mid + 1
            else:
                max_side = mid
        return min_side

    def find_box_by_factorization(
        self,
        bigger_first=True,
        fix_point=True,
        check_stable=True,
        support_surface_ratio=0.1,
        binding: list = [],
        length_max: int = 0,
    ):
        """
        通过因式分解计算合适的箱子尺寸。
        考虑装箱策略，包括物品的大小、固定点、稳定性检查以及支撑面积比例等因素。
        """
        length = max(self.side_length + self.side_length // 2, length_max)
        boxes = []
        for i in range(length, self.min_side - 1, -1):
            if self.volume % i == 0:  # 如果i是volume的因子
                for j in range(i, self.min_side - 1, -1):  # 优化循环起始和终止条件
                    if (self.volume // i) % j == 0:
                        k = self.volume // (i * j)  # 计算第三维度
                        if k < self.min_side:
                            continue  # 如果箱子的最小边长大于最小物品的边长，则跳过
                        # 创建箱子并进行旋转，考虑不同方向
                        box = Bin(
                            partno="box", WHD=(i, j, k), max_weight=9999999, put_type=0
                        )
                        boxes = self.__rotation_box(box)
                        for box in boxes:
                            result = self.pack_verify(
                                bins=[box],
                                bigger_first=bigger_first,
                                distribute_items=False,
                                fix_point=fix_point,
                                check_stable=check_stable,
                                support_surface_ratio=support_surface_ratio,
                                binding=binding,
                            )
                            for res in result.values():
                                if res["resolve"]:
                                    return res["width"], res["height"], res["depth"]
        return None  # 如果没有找到合适的箱子，返回None
