import os
from typing import List, Union

from DL3Dbp.MCTS.node import Node


class MCTS:
    def __init__(self) -> None:
        raise NotImplementedError

    def selection(self, node: Node) -> List[Node]:
        # 选择节点
        # 基于选择算法，从根节点开始，选择采用UCB计算得到的最大的值的孩子节点，如此向下搜索，直到来到树的底部的叶子节点（没有孩子节点的节点），等待下一步操作。
        raise NotImplementedError

    def expansion(self, path: List[Node]) -> List[Node]:
        # 扩展节点
        # 对于一个节点，如果它没有孩子节点，需要扩展它，即添加它的子节点。从当前节点的状态开始，对所有可能的动作进行扩展，并将它们添加到它的孩子节点中。
        # 到达叶子节点后，如果还没有到达终止状态（比如五子棋的五子连星），那么就要对这个节点进行扩展，扩展出一个或多个节点（也就是进行一个可能的action然后进入下一个状态）。
        raise NotImplementedError

    def simulation(self, path: List[Node]) -> List[Node]:
        # 模拟
        # 对于一个节点，如果它没有结果（即它是一个叶子节点），需要进行模拟，即在它的子节点中随机选择一个动作，然后将它应用到游戏状态上，直到游戏结束。
        # 基于目前的这个状态，根据某一种策略（例如random policy）进行模拟，直到游戏结束为止，产生结果，比如胜利或者失败。
        # 对于每一步模拟，都要更新它的胜率和遍历次数。
        raise NotImplementedError

    def backpropagation(self, path: List[Node]) -> None:
        # 反向传播
        # 对于一个节点，如果它是一个叶子节点，需要更新它的胜率和遍历次数，并向上回溯，直到根节点。
        # 对于每一步回溯，都要更新它的胜率和遍历次数。
        raise NotImplementedError

    def step(self) -> None:
        # 一次迭代
        # 选择、扩展、模拟、反向传播，一步一步地进行博弈。

        # 对于训练模式，需要进行模拟，即在游戏状态上随机选择一个动作，然后将它应用到游戏状态上，直到游戏结束。
        # 对于评估模式，需要选择最佳动作，即在游戏状态上采用UCB计算得到的最大的值的孩子节点，如此向下搜索，直到来到树的底部的叶子节点（没有孩子节点的节点），等待下一步操作。

        # 进行模拟，即在游戏状态上随机选择一个动作，然后将它应用到游戏状态上，直到游戏结束。
        # 更新它的胜率和遍历次数，并向上回溯，直到根节点。
        raise NotImplementedError

    def self_play(self, iterations: int = 1) -> None:
        # 自我对弈
        # 需要进行多次迭代，每次迭代都要进行一次自我对弈，即需要在游戏状态上随机选择一个动作，然后将它应用到游戏状态上，直到游戏结束。
        # 然后，需要更新它的胜率和遍历次数，并向上回溯，直到根节点。
        # 最后，需要进行一次迭代。
        raise NotImplementedError

    def save(self, file_path: Union[str, os.PathLike]) -> None:
        # 保存模型
        # 包括游戏、副本游戏、训练模式、根节点、缓存表。
        raise NotImplementedError

    def load(self, file_path: Union[str, os.PathLike]) -> None:
        # 加载模型
        # 包括游戏、副本游戏、训练模式、根节点、缓存表。

        raise NotImplementedError
