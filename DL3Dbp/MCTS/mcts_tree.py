import gc
import os
import pickle
import random
from copy import deepcopy
from tqdm.auto import tqdm
from typing import List, Union, Optional

from DL3Dbp.MCTS.game import Game
from DL3Dbp.MCTS.item_node import ItemNode
from DL3Dbp.MCTS.mcts import MCTS


class MCTSTree(MCTS):
    def __init__(self, game: Game, allow_transpositions: bool = True, training: bool = True,
                 item_node: Optional[ItemNode] = None):
        super().__init__()
        self.game = game  # 博弈游戏
        self.copied_game = deepcopy(self.game)  # 游戏副本

        self.transposition_table = dict() if allow_transpositions is True else None  # {(player, state): Node} 缓存表
        self.root = item_node  # 根节点
        if self.transposition_table is not None:
            self.transposition_table[(self.game.current_player(), str(self.game.get_state()))] = self.root  # 缓存根节点
        self.training = training  # 是否训练模式

    def selection(self, node: ItemNode) -> List[ItemNode]:
        # 选择节点
        # 基于选择算法，从根节点开始，我们选择采用UCB计算得到的最大的值的孩子节点，如此向下搜索，直到我们来到树的底部的叶子节点（没有孩子节点的节点），等待下一步操作。

        path = [node]
        while path[-1].is_expanded is True and path[-1].has_outcome is False:  # 如果不是叶子节点，则开始循环
            action = path[-1].choose_best_action(self.training)  # 选择最佳动作
            path.append(path[-1].children[action])  # 向下搜索
            self.copied_game.take_action(action)  # 应用动作到副本游戏
        return path

    def expansion(self, path: List[ItemNode]) -> List[ItemNode]:
        # 扩展节点
        # 对于一个节点，如果它没有孩子节点，我们需要扩展它，即添加它的子节点。我们从当前节点的状态开始，对所有可能的动作进行扩展，并将它们添加到它的孩子节点中。
        # 到达叶子节点后，如果还没有到达终止状态（比如五子棋的五子连星），那么我们就要对这个节点进行扩展，扩展出一个或多个节点（也就是进行一个可能的action然后进入下一个状态）。
        if self.copied_game.has_outcome() is True:  # 如果游戏已经结束，则不需要扩展
            path[-1].has_outcome = True  # 标记结果
            return path

        if path[-1].is_expanded is False:  # 如果节点没有扩展过，则扩展
            for action in self.copied_game.possible_actions():  # 遍历所有可能的动作
                expanded_game = deepcopy(self.copied_game)  # 扩展游戏
                expanded_game.take_action(action)  # 应用动作到游戏
                path[-1].add_child(expanded_game.current_player(), str(expanded_game.get_state()), action)  # 添加子节点

            assert len(path[-1].children) > 0  # 至少有一个子节点

            path[-1].is_expanded = True  # 标记扩展
            action = path[-1].choose_random_action()  # 随机选择一个动作
            path.append(path[-1].children[action])  # 向下搜索
            self.copied_game.take_action(action)  # 应用动作到副本游戏
        return path

    def simulation(self, path: List[ItemNode]) -> List[ItemNode]:
        # 模拟
        # 对于一个节点，如果它没有结果（即它是一个叶子节点），我们需要进行模拟，即在它的子节点中随机选择一个动作，然后将它应用到游戏状态上，直到游戏结束。
        # 基于目前的这个状态，根据某一种策略（例如random policy）进行模拟，直到游戏结束为止，产生结果，比如胜利或者失败。
        # 对于每一步模拟，我们都要更新它的胜率和遍历次数。
        while self.copied_game.has_outcome() is False:  # 直到游戏结束
            action = random.choice(self.copied_game.possible_actions())  # 随机选择一个动作
            self.copied_game.take_action(action)  # 应用动作到游戏
            path[-1].add_child(self.copied_game.current_player(), str(self.copied_game.get_state()), action)  # 添加子节点
            path.append(path[-1].children[action])  # 向下搜索
        return path

    def backpropagation(self, path: List[ItemNode]) -> None:
        # 反向传播
        # 对于一个节点，如果它是一个叶子节点，我们需要更新它的胜率和遍历次数，并向上回溯，直到根节点。
        # 对于每一步回溯，我们都要更新它的胜率和遍历次数。
        if self.copied_game.has_outcome() is True:  # 如果游戏已经结束，则不需要反向传播
            winners = self.copied_game.winner()  # 获得胜利者
            number_of_winners = len(winners)  # 获得胜利者数量
            path[0].n += 1  # 遍历次数加1
            for i in range(1, len(path)):  # 向上回溯
                if number_of_winners > 0:  # 如果有胜利者
                    path[i].w += (path[i - 1].item in winners) / number_of_winners  # 胜率加1
                path[i].n += 1  # 遍历次数加1
            path[-1].has_outcome = True  # 标记结果

    def step(self) -> None:
        # 一次迭代
        # 选择、扩展、模拟、反向传播，一步一步地进行博弈。

        # 对于训练模式，我们需要进行模拟，即在游戏状态上随机选择一个动作，然后将它应用到游戏状态上，直到游戏结束。
        # 对于评估模式，我们需要选择最佳动作，即在游戏状态上采用UCB计算得到的最大的值的孩子节点，如此向下搜索，直到我们来到树的底部的叶子节点（没有孩子节点的节点），等待下一步操作。

        # 然后，我们需要进行模拟，即在游戏状态上随机选择一个动作，然后将它应用到游戏状态上，直到游戏结束。
        # 然后，我们需要更新它的胜率和遍历次数，并向上回溯，直到根节点。

        # 最后，我们需要进行一次迭代。

        if self.training is True:  # 训练模式
            self.backpropagation(self.simulation(self.expansion(self.selection(self.root))))
        else:
            node = self.root
            while not self.copied_game.has_outcome():
                self.copied_game.render()
                if len(node.children) > 0:
                    action = node.choose_best_action(self.training)  # 选择最佳动作
                    node = node.children[action]
                else:
                    action = random.choice(self.copied_game.possible_actions())  # 随机选择一个动作
                self.copied_game.take_action(action)  # 应用动作到游戏
            self.copied_game.render()  # 渲染游戏

        self.copied_game = deepcopy(self.game)  # 游戏副本
        gc.collect()  # 清理垃圾

    def self_play(self, iterations: int = 1) -> None:
        # 自我对弈
        # 我们需要进行多次迭代，每次迭代我们都要进行一次自我对弈，即我们需要在游戏状态上随机选择一个动作，然后将它应用到游戏状态上，直到游戏结束。
        # 然后，我们需要更新它的胜率和遍历次数，并向上回溯，直到根节点。
        # 最后，我们需要进行一次迭代。
        desc = "Training" if self.training is True else "Evaluating"
        for _ in tqdm(range(iterations), desc=desc):
            self.step()

    def save(self, file_path: Union[str, os.PathLike]) -> None:
        # 保存模型
        # 包括游戏、副本游戏、训练模式、根节点、缓存表。

        game, copied_game, training = self.game, self.copied_game, self.training
        del self.game, self.copied_game, self.training
        with open(file_path, "wb") as handle:
            pickle.dump(self, handle, protocol=-1)
            handle.close()
        self.game, self.copied_game, self.training = game, copied_game, training

    def load(self, file_path: Union[str, os.PathLike]) -> None:
        # 加载模型
        # 包括游戏、副本游戏、训练模式、根节点、缓存表。

        with open(file_path, "rb") as handle:
            self.__dict__.update(pickle.load(handle).__dict__)
            handle.close()
        if self.transposition_table is not None:
            self.root = self.transposition_table[(self.game.current_player(), str(self.game.get_state()))]
        assert self.game.current_player() == self.root.player and str(self.game.get_state()) == self.root.state
