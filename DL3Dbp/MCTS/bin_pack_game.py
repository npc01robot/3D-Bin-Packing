from typing import List, Any, Dict, Tuple

from DL3Dbp.MCTS.game import Game
from DL3Dbp.MCTS.item_node import ItemNode


class BinPackingGame(Game):
    def __init__(self, items: List[ItemNode]):
        super().__init__()
        self.container = []
        self.items = items
        self.current_item_index = 0

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
        raise NotImplementedError

    def possible_actions(self) -> list[tuple[int, int, int]]:
        """
        当前玩家本回合可以采取的可能行动列表

        axis * rotation 一共是18种可能的动作，
        需要考虑是否放的下，比如最大支撑面积等
        """
        actions = []
        current_item = self.items[self.current_item_index]
        for x in range(self.container.width - current_item.width + 1):
            for y in range(self.container.height - current_item.height + 1):
                for z in range(self.container.depth - current_item.depth + 1):
                    if self.is_valid_placement(current_item, x, y, z):
                        actions.append((x, y, z))
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
        raise NotImplementedError

    def winner(self) -> List[int]:
        """
        如果所有玩家都输了，则清空列表
        或
        如果游戏以平局结束，则列出玩家名单
        或
        如果至少有一名玩家获胜，则列出获胜者名单
        """
        raise NotImplementedError
