from typing import List, Any, Dict, Tuple

import numpy as np

from DL3Dbp.MCTS.game import Game
from DL3Dbp.MCTS.item_node import ItemNode
from utils.auxiliary_methods import intersect, can_place
from utils.constants import RotationType, Axis


class BinPackingGame(Game):
    def __init__(self, items: List[ItemNode]):
        super().__init__()
        self.container = np.array([])
        self.items = items
        self.current_item_index = 0
        self.fit_items = []
        self.unfit_items = []

    def render(self) -> None:
        """
        将以文本或其他方式输出游戏当前状态的视觉表现
        """
        # TODO: 画图显示
        pass

    def get_state(self) -> Dict[str, Any]:
        """
        当前状态
        """
        return {
            "items": self.items,
            "container": self.container,
            "current_item_index": self.current_item_index
        }

    def number_of_players(self) -> int:
        """
        玩家个数
        """
        raise NotImplementedError

    def current_player(self) -> int:
        """
        本回合采取行动的玩家编号
        """
        return self.current_item_index

    def possible_actions(self) -> list[tuple[tuple[int, int, int], int, int]]:
        """
        当前玩家本回合可以采取的可能行动列表

        axis * rotation * position
        需要考虑是否放的下，比如最大支撑面积等
        action = (摆放位置)，(放置方向)，(旋转角度)
        """
        # TODO: 实现
        # 1、是否相交
        # 2、是否放的下
        self.current_item_index += 1
        actions = []
        item = self.items[self.current_item_index]
        item_np = item.get_dimension(True)
        results = []
        for i in Axis.ALL:  # axis x,y,z 轴扩展
            positions = self.container.copy()  # 复制 containers
            positions[:, i] += positions[:, i + 6]
            positions[:, 3:6] = positions[:, :3] + item_np[:, 1:]
            positions[:, 6:9] = item_np[:, 1:]
            positions[:, -2] = i
            positions[:, -1] = item_np[:, 0]
            results.append(positions)
        result_array = np.array(results).reshape(-1, self.container.shape[1])  # 解的集合
        can_place(self.container, result_array)

        return actions

    def take_action(self, action: int) -> None:
        """
        下一个玩家应该在游戏结束后选择
        """
        raise NotImplementedError

    def has_outcome(self) -> bool:
        """
        是否结束
        """
        if self.current_item_index >= len(self.items):
            return True
        return False

    def winner(self) -> List[int]:
        """
        如果所有玩家都输了，则清空列表
        或
        如果游戏以平局结束，则列出玩家名单
        或
        如果至少有一名玩家获胜，则列出获胜者名单
        """
        raise NotImplementedError



    def checkDepth(self, unfix_point, length=0):
        """fix item position z"""
        length = float(length) if length else float(self.depth)
        z_ = [[0, 0], [length, length]]
        for j in self.fit_items:
            # creat x set
            x_bottom = set([i for i in range(int(j[0]), int(j[1]))])
            x_top = set([i for i in range(int(unfix_point[0]), int(unfix_point[1]))])
            # creat y set
            y_bottom = set([i for i in range(int(j[2]), int(j[3]))])
            y_top = set([i for i in range(int(unfix_point[2]), int(unfix_point[3]))])
            # find intersection on x set and y set.
            if len(x_bottom & x_top) != 0 and len(y_bottom & y_top) != 0:
                z_.append([float(j[4]), float(j[5])])
        top_depth = unfix_point[5] - unfix_point[4]
        # find diff set on z_.
        z_ = sorted(z_, key=lambda z_: z_[1])
        for j in range(len(z_) - 1):
            if z_[j + 1][0] - z_[j][1] >= top_depth:
                return z_[j][1]
        return unfix_point[4]

    def checkWidth(self, unfix_point, length=0):
        """fix item position x"""
        length = float(length) if length else float(self.width)
        x_ = [[0, 0], [length, length]]
        for j in self.fit_items:
            # creat z set
            z_bottom = set([i for i in range(int(j[4]), int(j[5]))])
            z_top = set([i for i in range(int(unfix_point[4]), int(unfix_point[5]))])
            # creat y set
            y_bottom = set([i for i in range(int(j[2]), int(j[3]))])
            y_top = set([i for i in range(int(unfix_point[2]), int(unfix_point[3]))])
            # find intersection on z set and y set.
            if len(z_bottom & z_top) != 0 and len(y_bottom & y_top) != 0:
                x_.append([float(j[0]), float(j[1])])
        top_width = unfix_point[1] - unfix_point[0]
        # find diff set on x_bottom and x_top.
        x_ = sorted(x_, key=lambda x_: x_[1])
        for j in range(len(x_) - 1):
            if x_[j + 1][0] - x_[j][1] >= top_width:
                return x_[j][1]
        return unfix_point[0]

    def checkHeight(self, unfix_point, length=0):
        """fix item position y"""
        length = float(length) if length else float(self.width)
        y_ = [[0, 0], [length, length]]
        for j in self.fit_items:
            # creat x set
            x_bottom = set([i for i in range(int(j[0]), int(j[1]))])
            x_top = set([i for i in range(int(unfix_point[0]), int(unfix_point[1]))])
            # creat z set
            z_bottom = set([i for i in range(int(j[4]), int(j[5]))])
            z_top = set([i for i in range(int(unfix_point[4]), int(unfix_point[5]))])
            # find intersection on x set and z set.
            if len(x_bottom & x_top) != 0 and len(z_bottom & z_top) != 0:
                y_.append([float(j[2]), float(j[3])])
        top_height = unfix_point[3] - unfix_point[2]
        # find diff set on y_bottom and y_top.
        y_ = sorted(y_, key=lambda y_: y_[1])
        for j in range(len(y_) - 1):
            if y_[j + 1][0] - y_[j][1] >= top_height:
                return y_[j][1]

        return unfix_point[2]