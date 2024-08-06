from typing import Any, List


class Game:
    def __init__(self):
        raise NotImplementedError

    def render(self) -> None:
        """
        将以文本或其他方式输出游戏当前状态的视觉表现
        """
        raise NotImplementedError

    def get_state(self) -> Any:
        """
        当前状态
        """
        raise NotImplementedError

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

    def possible_actions(self) -> List[int]:
        """
        当前玩家本回合可以采取的可能行动列表
        """
        raise NotImplementedError

    def take_action(self, action: int) -> None:
        """
        下一个玩家应该在游戏结束后选择
        """
        raise NotImplementedError

    def has_outcome(self) -> bool:
        """
        游戏是否结束
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