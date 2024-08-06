
class Node:
    def __init__(self):
        raise NotImplementedError

    def eval(self, **kwargs) -> float:
        # 计算节点的胜率
        raise NotImplementedError

    def add_child(self, **kwargs) -> None:
        # 存入下一个玩家的状态和动作
        raise NotImplementedError

    def choose_best_action(self, **kwargs) -> int:
        # 选择最佳动作
        raise NotImplementedError

    def choose_random_action(self,**kwargs) -> int:
        # 随机选择动作
        raise NotImplementedError

    def update(self, **kwargs) -> None:
        # 更新节点的统计信息
        raise NotImplementedError
