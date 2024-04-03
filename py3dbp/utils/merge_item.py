import copy

from py3dbp.spec.item_set import ItemSet


def merge_items(item_set, new_item_dict):
    old_side_dic = {
        "w": item_set.width,
        "h": item_set.height,
        "d": item_set.depth,
    }
    old_name = ",".join(sorted(map(str, old_side_dic.values())))
    key, value = min(old_side_dic.items(), key=lambda x: x[1])

    new_side_dic = copy.deepcopy(old_side_dic)
    new_side_dic[key] = value * 2
    new_name = ",".join(sorted(map(str, new_side_dic.values())))

    # 先合并相同的产品规格
    old_item_set = new_item_dict.get(old_name)
    if old_item_set:
        item_set.quantity += old_item_set.quantity

    if item_set.quantity < 1:
        return new_item_dict
    if item_set.quantity > 1:
        new_item_set = ItemSet(
            partno=new_name,
            name=new_name,
            quantity=item_set.quantity // 2,  # 数量减半
            width=new_side_dic["w"],
            height=new_side_dic["h"],
            depth=new_side_dic["d"],
            weight=0.1,
        )
        new_item_dict[new_name] = new_item_set
    if item_set.quantity % 2:
        new_item_set = ItemSet(
            partno=new_name,
            name=new_name,
            quantity=1,  # 数量减半
            width=old_side_dic["w"],
            height=old_side_dic["h"],
            depth=old_side_dic["d"],
            weight=0.1,
        )
        new_item_dict[old_name] = new_item_set

    return new_item_dict


items = [
    ItemSet(
        partno="12345",
        name="item1",
        quantity=3,
        width=5,
        height=20,
        depth=10,
        weight=100,
    ),
    ItemSet(
        partno="67890",
        name="item2",
        quantity=3,
        width=10,
        height=20,
        depth=10,
        weight=100,
    ),
    ItemSet(
        partno="123456",
        name="item3",
        quantity=9,
        width=10,
        height=20,
        depth=10,
        weight=100,
    ),
]

new_item_dict = {}
for item in items:
    merge_items(item, new_item_dict)
