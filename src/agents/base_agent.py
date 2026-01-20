"""
Agent 基类定义 - 所有 Agent 都继承自此基类
"""
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
import logging
from src.models.data_models import StockAnalysisContext

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Agent 基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.execution_time: Optional[float] = None
        self.last_execution: Optional[datetime] = None

    @abstractmethod
    def analyze(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        执行分析
        Args:
            context: 股票分析上下文
        Returns:
            更新后的分析上下文
        """
        pass

    def execute(self, context: StockAnalysisContext) -> StockAnalysisContext:
        """
        执行 Agent 的标准入口
        Args:
            context: 股票分析上下文
        Returns:
            更新后的分析上下文
        """
        import time
        start_time = time.time()

        try:
            logger.info(f"执行 Agent: {self.name}")
            result = self.analyze(context)

            self.execution_time = time.time() - start_time
            self.last_execution = datetime.now()

            logger.info(f"Agent {self.name} 执行完成，耗时: {self.execution_time:.2f}s")
            return result
        except Exception as e:
            logger.error(f"Agent {self.name} 执行失败: {str(e)}")
            raise

    def __str__(self) -> str:
        return f"Agent({self.name})"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
