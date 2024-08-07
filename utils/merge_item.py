import copy
from typing import Any, Dict, List

from py3dbp.spec.item_set import ItemSet


class MergeItemTool:
    def __init__(self, items: List[ItemSet]):
        self.items = items
        self.item_dict = self.__init_item_dict()

    def __init_item_dict(self) -> Dict[str, Any]:
        """初始化item_dict"""
        item_dict = {}
        for item in self.items:
            side_dic = {
                "w": item.width,
                "h": item.height,
                "d": item.depth,
            }
            name = ",".join(map(str, sorted(side_dic.values())))
            if item_dict.get(name):
                item_dict[name].quantity += item.quantity
            else:
                item_dict[name] = copy.deepcopy(item)
        return item_dict

    def get_merged_item(self, side_length):
        # 获取合并后的item_dict
        new_item_dict = copy.deepcopy(self.item_dict)
        old_item_dict = copy.deepcopy(self.item_dict)
        for item in old_item_dict.values():
            self.merge_items(item, new_item_dict, side_length)
        # todo 这个地方需要优化，可以对大体积保留一个item进行回溯
        if len(self.item_dict.values()) == 1:
            new_item_dict = self.devanning_partno(new_item_dict, self.items[0])
        return new_item_dict

    def __get_surface_area(self, width, height, depth):
        return 2 * (width * height + width * depth + height * depth)

    def merge_items_by_area(
        self,
        item_set: ItemSet,
        new_item_dict: Dict[str, ItemSet],
        max_length: int = 99999,
        max_area: int = 99999,
    ):
        # 合并相同产品规格的箱子，按面积合并
        old_side_li = [item_set.width, item_set.height, item_set.depth]
        old_side_li = sorted(old_side_li)
        old_name = ",".join(map(str, old_side_li))
        old_item = new_item_dict.get(old_name)
        # 数量小于等于1,超过最大长度，不合并
        if (
            item_set.quantity <= 1
            or (old_item and old_item.quantity <= 1)
            or item_set.width * item_set.height * 2 > max_area
            or item_set.height * item_set.depth * 2 > max_area
            or item_set.depth * item_set.width * 2 > max_area
        ):
            return
        min_surface_area = float("inf")
        min_index = -1
        for i in range(3):
            new_dimensions = old_side_li.copy()
            new_dimensions[i] *= 2  # 倍增当前维度
            current_surface_area = self.__get_surface_area(
                new_dimensions[0], new_dimensions[1], new_dimensions[2]
            )
            if current_surface_area < min_surface_area:
                min_surface_area = current_surface_area
                min_index = i
        min_surface_dimensions = old_side_li.copy()
        min_surface_dimensions[min_index] *= 2  # 倍增当前维度
        new_side_li = sorted(min_surface_dimensions)
        new_name = ",".join(map(str, new_side_li))

        # 先合并相同的产品规格
        new_item = new_item_dict.get(new_name)

        half_quantity = item_set.quantity // 2
        full_quantity = half_quantity * 2

        if new_item:
            new_item.quantity = new_item.quantity + half_quantity  # 数量减半
        else:
            new_item = ItemSet(
                partno=new_name,
                name=new_name,
                quantity=item_set.quantity // 2,  # 数量减半
                width=new_side_li[0],
                height=new_side_li[1],
                depth=new_side_li[2],
                weight=1,
            )
        new_item.child = item_set
        new_item_dict[new_name] = new_item
        item_set.quantity = item_set.quantity - full_quantity  # 数量减半
        if item_set.quantity <= 0:
            new_item_dict.pop(old_name)
        else:
            new_item_dict[old_name] = item_set
        self.merge_items_by_area(new_item, new_item_dict, max_length, max_area)

    def merge_items(
        self,
        item_set: ItemSet,
        new_item_dict: Dict[str, ItemSet],
        max_length: int = 99999,
    ):
        # 合并相同产品规格的箱子，按最小边长合并
        old_side_dic = {
            "w": item_set.width,
            "h": item_set.height,
            "d": item_set.depth,
        }
        old_name = ",".join(map(str, sorted(old_side_dic.values())))
        key, value = min(old_side_dic.items(), key=lambda x: x[1])
        # old_item 防止重复合并
        old_item = new_item_dict.get(old_name)
        # 数量小于等于1,超过最大长度，不合并
        if (
            item_set.quantity <= 1
            or (old_item and old_item.quantity <= 1)
            or value * 2 > max_length
        ):
            return

        new_side_dic = copy.deepcopy(old_side_dic)
        new_side_dic[key] = value * 2
        new_name = ",".join(map(str, sorted(new_side_dic.values())))

        # 先合并相同的产品规格
        new_item = new_item_dict.get(new_name)

        half_quantity = item_set.quantity // 2
        full_quantity = half_quantity * 2

        # 存在相同的产品规格，数量相加
        if new_item:
            new_item.quantity = new_item.quantity + half_quantity  # 数量减半
        else:
            new_item = ItemSet(
                partno=new_name,
                name=new_name,
                quantity=item_set.quantity // 2,  # 数量减半
                width=new_side_dic["w"],
                height=new_side_dic["h"],
                depth=new_side_dic["d"],
                weight=1,
            )
        new_item.child = item_set
        new_item_dict[new_name] = new_item
        item_set.quantity = item_set.quantity - full_quantity  # 数量减半
        if item_set.quantity <= 0:
            new_item_dict.pop(old_name)
        else:
            new_item_dict[old_name] = item_set
        self.merge_items(new_item, new_item_dict, max_length)

    # 递归获取单品的深度
    def devanning(self, item_set: ItemSet, depth: int = 0):
        if item_set.child:
            return self.devanning(item_set.child, depth + 1)
        return depth

    def devanning_partno(
        self, new_item_dict: Dict[str, ItemSet], original_item: ItemSet
    ):
        # 回溯
        depth_list = []
        max_merged_item = None
        max_depth = 0
        for item in new_item_dict.values():
            depth = self.devanning(item)
            if depth > max_depth:
                max_depth = depth
                max_merged_item = item
            depth_list += [depth] * item.quantity

        depth_list.pop(depth_list.index(max_depth))
        quantity = sum([2**i for i in depth_list])
        original_item.quantity = quantity
        max_merged_item.quantity = 1
        return {"max_merged_item": max_merged_item, "original_item": original_item}
