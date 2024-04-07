import random

from py3dbp import Item
from py3dbp.utils.auxiliary_methods import set2Decimal
from py3dbp.utils.constants import DEFAULT_NUMBER_OF_DECIMALS


class ItemSet:
    """
    This class represents the type of an item in the 3D building process.
    """

    def __init__(
            self, partno: str, name: str, width: float, height: float, depth: float, weight: float, color: str = "",
            quantity: int = 1,
            typeof: str = "cube", level: int = 1, loadbear: float = 99, updown: bool = True,
    ):
        """
        partno: str, 唯一标识符前缀
        name: str, item名称
        width: float, item宽度
        height: float, item高度
        depth: float, item深度
        weight: float, item重量
        color: str, item颜色
        quantity: int, item数量
        typeof: str, item类型，cube, cylinder
        level: int, item优先级，数字越大优先级越高 1-3
        loadbear: float, 承重能力
        updown: bool, 是否上下翻转，仅对cube有效
        """
        self.partno = partno
        self.name = name
        self.width = width
        self.height = height
        self.depth = depth
        self.weight = weight
        self.quantity = quantity
        self.typeof = typeof
        self.level = level
        self.loadbear = loadbear
        self.updown = updown if typeof == "cube" else False
        self.color = color if color else self.generate_color()
        self.merged_list = []
        self.items = self.generate_items()

    def generate_items(self):
        items = []
        for i in range(self.quantity):
           items.append(Item(
                partno=f'{self.partno}_{i + 1}',
                name=self.name,
                WHD=(self.width, self.height, self.depth),
                weight=self.weight,
                color=self.color,
                typeof=self.typeof,
                level=self.level,
                loadbear=self.loadbear,
                updown=self.updown
            ))
        return items

    def generate_color(self):
        r = random.randint(0, 255)  # 随机生成红色通道的值
        g = random.randint(0, 255)  # 随机生成绿色通道的值
        b = random.randint(0, 255)  # 随机生成蓝色通道的值
        color_code = f'#{r:02x}{g:02x}{b:02x}'  # 将RGB值转换为颜色代码格式
        return color_code

    def get_max_side(self):
        return max(self.width, self.height, self.depth)