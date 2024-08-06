import random
from typing import Optional, Dict

from DL3Dbp.MCTS.node import Node
from py3dbp.utils.auxiliary_methods import set2Decimal
from py3dbp.utils.constants import DEFAULT_NUMBER_OF_DECIMALS, START_POSITION, RotationType


class ItemNode(Node):
    def __init__(self, partno: str, typeof: str, width: float, height: float, depth: float, weight: float, level: int,
                 loadbear: bool, updown: bool, color: str, item: int, position_type: int, prev_node: Optional[Node] = None,
                 transposition_table: Optional[Dict[tuple, Node]] = None):
        # 玩家指的是当前物品，状态为 已经放置和未放置的物品
        super().__init__()
        self.item = item  # 子节点玩家
        self.position_type = position_type  # 位置类型, 6种 上下左右前后
        self.rotation_type = 0        # 旋转类型 6种
        self.prev_node = prev_node  # 前置节点
        self.transposition_table = transposition_table  # {(item, position_type, rotation_type): Node} 缓存表
        self.children = dict()  # {action: Node} 子节点字典

        self.is_expanded = False  # 是否扩展
        self.has_outcome = False  # 是否有结果

        self.w = 0.  # 前一个玩家的胜率
        self.n = 0  # 遍历所有的游戏次数

        # 基本信息
        self.partno = partno
        self.typeof = typeof
        self.width = width
        self.height = height
        self.depth = depth
        self.weight = weight
        # Packing Priority level ,choose 1-3
        self.level = level
        # loadbear
        self.loadbear = loadbear
        # Upside down? True or False
        self.updown = updown if typeof == "cube" else False
        # Draw item color
        self.color = color
        # 当前节点已经组合的物品信息
        self.max_height = 0
        self.max_width = 0
        self.max_depth = 0

        self.total_weight = 0

        #是否已经放置
        self.is_packed = False

        # 物品位置 (x,y,z)
        self.position = START_POSITION
        # Decimals of the dimensions
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS

    def __get_total_volume(self):
        # 计算体积
        return set2Decimal(self.max_height * self.max_width * self.max_depth)

    def format_numbers(self, number_of_decimals):
        """ """
        self.width = set2Decimal(self.width, number_of_decimals)
        self.height = set2Decimal(self.height, number_of_decimals)
        self.depth = set2Decimal(self.depth, number_of_decimals)
        self.weight = set2Decimal(self.weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def string(self):
        """ """
        return "%s(%sx%sx%s, weight: %s) pos(%s) rt(%s) vol(%s)" % (
            self.partno,
            self.width,
            self.height,
            self.depth,
            self.weight,
            self.position,
            self.rotation_type,
            self.get_volume(),
        )

    def get_volume(self):
        """ """
        return set2Decimal(
            self.width * self.height * self.depth, self.number_of_decimals
        )

    def get_max_area(self):
        """ """
        a = (
            sorted([self.width, self.height, self.depth], reverse=True)
            if self.updown == True
            else [self.width, self.height, self.depth]
        )

        return set2Decimal(a[0] * a[1], self.number_of_decimals)

    def get_dimension(self):
        """rotation type"""
        if self.rotation_type == RotationType.RT_WHD:
            dimension = [self.width, self.height, self.depth]
        elif self.rotation_type == RotationType.RT_HWD:
            dimension = [self.height, self.width, self.depth]
        elif self.rotation_type == RotationType.RT_HDW:
            dimension = [self.height, self.depth, self.width]
        elif self.rotation_type == RotationType.RT_DHW:
            dimension = [self.depth, self.height, self.width]
        elif self.rotation_type == RotationType.RT_DWH:
            dimension = [self.depth, self.width, self.height]
        elif self.rotation_type == RotationType.RT_WDH:
            dimension = [self.width, self.depth, self.height]
        else:
            dimension = []

        return dimension

    def eval(self, training: bool, ) -> float:
        # 计算体积大小，体积越小，长边越接近短边，胜率越大
        # TODO: 增加其他评价指标
        return self.w / self.n if self.n > 0 else float("inf") if training else 0.

    def add_child(self, next_item: int, next_position_type: int, next_rotation_type: int, action: int,
                  partno: str, typeof: str, width: float, height: float, depth: float, weight: float, level: int,
                  loadbear: bool, updown: bool, color: str, item: int, position_type: int,
                  prev_node: Optional[Node] = None,
                  ) -> None:
        # 添加子节点
        # 存入下一个玩家的状态和动作
        if action in self.children:
            return
        # 缓存表
        if self.transposition_table is not None:
            key = (next_item, next_position_type, next_rotation_type)
            if key in self.transposition_table:
                self.children[action] = self.transposition_table[key]
            else:
                self.children[action] = self.transposition_table[key] = ItemNode(partno, typeof, width, height,
                                                                                 depth, weight, level, loadbear,
                                                                                 updown, color, next_item,
                                                                                 next_position_type,
                                                                                 transposition_table=self.transposition_table)
        else:
            self.children[action] = ItemNode(partno, typeof, width, height, depth, weight, level, loadbear, updown,
                                             color, next_item, next_position_type, prev_node=self,
                                             transposition_table=self.transposition_table)

    def choose_best_action(self, training: bool) -> int:
        # 选择最佳动作
        """
        1、体积最小
        2、最长边最短
        3、约束条件达标
        4、装箱算法胜率高
        """
        # TODO 增加其他评价指标
        return max(self.children, key=lambda action: self.children[action].eval(training))

    def choose_random_action(self) -> int:
        # 随机选择动作
        return random.sample(list(self.children), 1)[0]

    def update_node(self, value: float) -> None:
        # 更新节点
        self.w += value
        self.n += 1
        # TODO 更新其他数据
