import time

from py3dbp import Bin, Packer, Painter
from py3dbp.spec.item_set import ItemSet


class Solution:
    def __init__(self,items:list[ItemSet]):
        self.items = items

    def find(self):
        total_items = 0
        pack_items = []
        for item in self.items:
            pack_items.extend(item.items)
            total_items += item.quantity
        self.packer = Packer()
        self.packer.items = pack_items
        self.packer.total_items = total_items
        box = self.packer.find_box()
        painter = Painter(box)
        fig = painter.plotBoxAndItems(
            title=box.partno,
            alpha=0.2,
            write_num=True,
            fontsize=10
        )

        fig.show()
        return box
    def pack_verify(self,bins:[Bin],
            bigger_first=True,
            distribute_items=True,
            fix_point=True,
            check_stable=True,
            support_surface_ratio=0.75,
            binding:list = [],
            painting:bool = False,):
        """
        :param bins: 盒子大小
               bigger_first: 放置
               distribute_items=True，按顺序将物品放入箱子中，如果箱子已满，则剩余物品将继续装入下一个箱子，直到所有箱子装满或所有物品都被打包。 distribute_items=False，比较所有箱子的打包情况，即每个箱子打包所有物品，而不是剩余物品。
                fix_point 重力问题
                check_stable 稳定性
                support_surface_ratio 可支a 撑的面积大小
                binding： binding = [(orange,apple),(computer,hat,watch)]用来组合打包
        """
        start = time.time()
        self.bins = bins
        total_items = 0
        pack_items = []
        for item in self.items:
            pack_items.extend(item.items)
            total_items += item.quantity
        self.packer = Packer()
        self.packer.bins = bins
        self.packer.items = pack_items
        self.packer.total_items = total_items
        self.packer.pack(bigger_first=bigger_first,distribute_items=distribute_items,fix_point=fix_point, check_stable=check_stable,support_surface_ratio=support_surface_ratio,binding=binding)
        stop = time.time()

        result = {}
        for box in self.packer.bins:
            box_name = box.partno
            result[box_name] = {}
            dic = {}
            for item in box.unfitted_items:
                dic[item.name] = dic.get(item.name,0) + 1
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
            if result[box_name]["unfitted_items"]:
                result[box_name]["resolve"] = False
            else:
                result[box_name]["resolve"] = True
            if painting:
                painter = Painter(box)
                fig = painter.plotBoxAndItems(
                    title=box.partno,
                    alpha=0.2,
                    write_num=True,
                    fontsize=10
                )
        result["exec_time"] = stop - start
        if painting:
            fig.show()

        return result

