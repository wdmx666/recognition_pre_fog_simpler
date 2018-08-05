# coding=utf8

from ..commons.common import MyConfig


# 相对静态的配置
class EventEvalConfig(MyConfig):
    @classmethod
    def strategyResult2(cls):
        from .core_algo import StrategyResult2
        return StrategyResult2()  # 策略是个参数传递进入

    def eventParameterProcessor(cls):
        from .processors import EventParameterProcessor
        EventParameterProcessor(cls.strategyResult2())





