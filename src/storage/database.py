"""
数据库存储模块 - 支持存储和查询分析结果
"""
import logging
import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from contextlib import contextmanager
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class AnalysisRecord:
    """分析记录数据模型"""
    id: Optional[int] = None
    stock_code: str = ""
    stock_name: str = ""
    analysis_date: str = ""

    # 财务指标
    current_price: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    gross_margin: Optional[float] = None
    debt_ratio: Optional[float] = None
    free_cash_flow: Optional[float] = None

    # 估值
    intrinsic_value: Optional[float] = None
    fair_price: Optional[float] = None
    margin_of_safety: Optional[float] = None
    valuation_score: Optional[float] = None

    # 护城河
    moat_score: Optional[float] = None
    brand_strength: Optional[float] = None
    cost_advantage: Optional[float] = None

    # 风险
    risk_level: str = ""
    leverage_risk: Optional[float] = None

    # 信号与评分
    buy_signal: str = ""
    sell_signal: str = ""
    final_signal: str = ""
    overall_score: Optional[float] = None
    ml_score: Optional[float] = None

    # 决策
    decision: str = ""
    position_size: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    # 元数据
    created_at: str = ""
    updated_at: str = ""
    raw_data: str = ""  # JSON 存储完整数据

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AnalysisRecord":
        return AnalysisRecord(**{k: v for k, v in data.items() if hasattr(AnalysisRecord, k)})


class BaseDatabase(ABC):
    """数据库抽象基类"""

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def create_tables(self) -> None:
        pass

    @abstractmethod
    def save_analysis(self, record: AnalysisRecord) -> int:
        pass

    @abstractmethod
    def get_analysis(self, stock_code: str, date: Optional[str] = None) -> Optional[AnalysisRecord]:
        pass

    @abstractmethod
    def get_analysis_history(self, stock_code: str, limit: int = 30) -> List[AnalysisRecord]:
        pass

    @abstractmethod
    def get_all_latest_analyses(self) -> List[AnalysisRecord]:
        pass

    @abstractmethod
    def delete_analysis(self, record_id: int) -> bool:
        pass


class SQLiteDatabase(BaseDatabase):
    """SQLite 数据库实现"""

    def __init__(self, db_path: str = "data/vimaster.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """连接数据库"""
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        logger.info(f"已连接数据库: {self.db_path}")

    def disconnect(self) -> None:
        """断开连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("数据库连接已关闭")

    @contextmanager
    def get_cursor(self):
        """获取游标上下文管理器"""
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    def create_tables(self) -> None:
        """创建数据表"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT,
                    analysis_date TEXT NOT NULL,
                    
                    -- 财务指标
                    current_price REAL,
                    pe_ratio REAL,
                    pb_ratio REAL,
                    roe REAL,
                    gross_margin REAL,
                    debt_ratio REAL,
                    free_cash_flow REAL,
                    
                    -- 估值
                    intrinsic_value REAL,
                    fair_price REAL,
                    margin_of_safety REAL,
                    valuation_score REAL,
                    
                    -- 护城河
                    moat_score REAL,
                    brand_strength REAL,
                    cost_advantage REAL,
                    
                    -- 风险
                    risk_level TEXT,
                    leverage_risk REAL,
                    
                    -- 信号与评分
                    buy_signal TEXT,
                    sell_signal TEXT,
                    final_signal TEXT,
                    overall_score REAL,
                    ml_score REAL,
                    
                    -- 决策
                    decision TEXT,
                    position_size REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    
                    -- 元数据
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    raw_data TEXT,
                    
                    UNIQUE(stock_code, analysis_date)
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_code 
                ON analysis_records(stock_code)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_analysis_date 
                ON analysis_records(analysis_date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_date 
                ON analysis_records(stock_code, analysis_date)
            """)

            logger.info("数据表已创建/验证")

    def save_analysis(self, record: AnalysisRecord) -> int:
        """保存分析记录"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record.updated_at = now
        if not record.created_at:
            record.created_at = now
        if not record.analysis_date:
            record.analysis_date = datetime.now().strftime("%Y-%m-%d")

        with self.get_cursor() as cursor:
            # 使用 REPLACE 实现 upsert
            cursor.execute("""
                INSERT OR REPLACE INTO analysis_records (
                    stock_code, stock_name, analysis_date,
                    current_price, pe_ratio, pb_ratio, roe, gross_margin, debt_ratio, free_cash_flow,
                    intrinsic_value, fair_price, margin_of_safety, valuation_score,
                    moat_score, brand_strength, cost_advantage,
                    risk_level, leverage_risk,
                    buy_signal, sell_signal, final_signal, overall_score, ml_score,
                    decision, position_size, stop_loss, take_profit,
                    created_at, updated_at, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.stock_code, record.stock_name, record.analysis_date,
                record.current_price, record.pe_ratio, record.pb_ratio, record.roe,
                record.gross_margin, record.debt_ratio, record.free_cash_flow,
                record.intrinsic_value, record.fair_price, record.margin_of_safety, record.valuation_score,
                record.moat_score, record.brand_strength, record.cost_advantage,
                record.risk_level, record.leverage_risk,
                record.buy_signal, record.sell_signal, record.final_signal, record.overall_score, record.ml_score,
                record.decision, record.position_size, record.stop_loss, record.take_profit,
                record.created_at, record.updated_at, record.raw_data
            ))

            record_id = cursor.lastrowid
            logger.info(f"分析记录已保存: {record.stock_code} @ {record.analysis_date}")
            return record_id

    def get_analysis(self, stock_code: str, date: Optional[str] = None) -> Optional[AnalysisRecord]:
        """获取分析记录"""
        with self.get_cursor() as cursor:
            if date:
                cursor.execute("""
                    SELECT * FROM analysis_records 
                    WHERE stock_code = ? AND analysis_date = ?
                """, (stock_code, date))
            else:
                cursor.execute("""
                    SELECT * FROM analysis_records 
                    WHERE stock_code = ? 
                    ORDER BY analysis_date DESC LIMIT 1
                """, (stock_code,))

            row = cursor.fetchone()
            if row:
                return self._row_to_record(row)
            return None

    def get_analysis_history(self, stock_code: str, limit: int = 30) -> List[AnalysisRecord]:
        """获取分析历史"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM analysis_records 
                WHERE stock_code = ? 
                ORDER BY analysis_date DESC 
                LIMIT ?
            """, (stock_code, limit))

            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

    def get_all_latest_analyses(self) -> List[AnalysisRecord]:
        """获取所有股票的最新分析"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM analysis_records 
                WHERE (stock_code, analysis_date) IN (
                    SELECT stock_code, MAX(analysis_date) 
                    FROM analysis_records 
                    GROUP BY stock_code
                )
                ORDER BY stock_code
            """)

            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

    def get_analyses_by_signal(self, signal: str) -> List[AnalysisRecord]:
        """按信号筛选分析"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM analysis_records 
                WHERE final_signal = ? 
                AND (stock_code, analysis_date) IN (
                    SELECT stock_code, MAX(analysis_date) 
                    FROM analysis_records 
                    GROUP BY stock_code
                )
                ORDER BY overall_score DESC
            """, (signal,))

            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

    def get_analyses_by_score(self, min_score: float) -> List[AnalysisRecord]:
        """按评分筛选分析"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM analysis_records 
                WHERE overall_score >= ? 
                AND (stock_code, analysis_date) IN (
                    SELECT stock_code, MAX(analysis_date) 
                    FROM analysis_records 
                    GROUP BY stock_code
                )
                ORDER BY overall_score DESC
            """, (min_score,))

            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

    def delete_analysis(self, record_id: int) -> bool:
        """删除分析记录"""
        with self.get_cursor() as cursor:
            cursor.execute("DELETE FROM analysis_records WHERE id = ?", (record_id,))
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"分析记录已删除: ID={record_id}")
            return deleted

    def delete_stock_analyses(self, stock_code: str) -> int:
        """删除股票的所有分析记录"""
        with self.get_cursor() as cursor:
            cursor.execute("DELETE FROM analysis_records WHERE stock_code = ?", (stock_code,))
            count = cursor.rowcount
            logger.info(f"已删除 {stock_code} 的 {count} 条分析记录")
            return count

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM analysis_records")
            total_records = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT stock_code) FROM analysis_records")
            total_stocks = cursor.fetchone()[0]

            cursor.execute("""
                SELECT final_signal, COUNT(*) as count 
                FROM analysis_records 
                WHERE (stock_code, analysis_date) IN (
                    SELECT stock_code, MAX(analysis_date) 
                    FROM analysis_records 
                    GROUP BY stock_code
                )
                GROUP BY final_signal
            """)
            signal_counts = {row[0]: row[1] for row in cursor.fetchall()}

            return {
                "total_records": total_records,
                "total_stocks": total_stocks,
                "signal_distribution": signal_counts,
            }

    def _row_to_record(self, row: sqlite3.Row) -> AnalysisRecord:
        """将数据库行转换为记录对象"""
        return AnalysisRecord(
            id=row["id"],
            stock_code=row["stock_code"],
            stock_name=row["stock_name"] or "",
            analysis_date=row["analysis_date"],
            current_price=row["current_price"],
            pe_ratio=row["pe_ratio"],
            pb_ratio=row["pb_ratio"],
            roe=row["roe"],
            gross_margin=row["gross_margin"],
            debt_ratio=row["debt_ratio"],
            free_cash_flow=row["free_cash_flow"],
            intrinsic_value=row["intrinsic_value"],
            fair_price=row["fair_price"],
            margin_of_safety=row["margin_of_safety"],
            valuation_score=row["valuation_score"],
            moat_score=row["moat_score"],
            brand_strength=row["brand_strength"],
            cost_advantage=row["cost_advantage"],
            risk_level=row["risk_level"] or "",
            leverage_risk=row["leverage_risk"],
            buy_signal=row["buy_signal"] or "",
            sell_signal=row["sell_signal"] or "",
            final_signal=row["final_signal"] or "",
            overall_score=row["overall_score"],
            ml_score=row["ml_score"],
            decision=row["decision"] or "",
            position_size=row["position_size"],
            stop_loss=row["stop_loss"],
            take_profit=row["take_profit"],
            created_at=row["created_at"] or "",
            updated_at=row["updated_at"] or "",
            raw_data=row["raw_data"] or "",
        )


class AnalysisRepository:
    """分析结果仓库 - 统一入口"""

    def __init__(self, db: Optional[BaseDatabase] = None, db_path: str = "data/vimaster.db"):
        self.db = db or SQLiteDatabase(db_path)
        self.db.connect()
        self.db.create_tables()

    def save_from_context(self, context) -> int:
        """从分析上下文保存记录"""
        record = self._context_to_record(context)
        return self.db.save_analysis(record)

    def save(self, record: AnalysisRecord) -> int:
        """保存分析记录"""
        return self.db.save_analysis(record)

    def get_latest(self, stock_code: str) -> Optional[AnalysisRecord]:
        """获取最新分析"""
        return self.db.get_analysis(stock_code)

    def get_by_date(self, stock_code: str, date: str) -> Optional[AnalysisRecord]:
        """获取指定日期的分析"""
        return self.db.get_analysis(stock_code, date)

    def get_history(self, stock_code: str, limit: int = 30) -> List[AnalysisRecord]:
        """获取历史分析"""
        return self.db.get_analysis_history(stock_code, limit)

    def get_all_latest(self) -> List[AnalysisRecord]:
        """获取所有股票的最新分析"""
        return self.db.get_all_latest_analyses()

    def get_by_signal(self, signal: str) -> List[AnalysisRecord]:
        """按信号筛选"""
        if isinstance(self.db, SQLiteDatabase):
            return self.db.get_analyses_by_signal(signal)
        return []

    def get_by_min_score(self, min_score: float) -> List[AnalysisRecord]:
        """按最低评分筛选"""
        if isinstance(self.db, SQLiteDatabase):
            return self.db.get_analyses_by_score(min_score)
        return []

    def delete(self, record_id: int) -> bool:
        """删除记录"""
        return self.db.delete_analysis(record_id)

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if isinstance(self.db, SQLiteDatabase):
            return self.db.get_statistics()
        return {}

    def close(self) -> None:
        """关闭连接"""
        self.db.disconnect()

    def _context_to_record(self, context) -> AnalysisRecord:
        """将分析上下文转换为记录"""
        record = AnalysisRecord(
            stock_code=context.stock_code,
            analysis_date=datetime.now().strftime("%Y-%m-%d"),
        )

        if context.financial_metrics:
            fm = context.financial_metrics
            record.current_price = fm.current_price
            record.pe_ratio = fm.pe_ratio
            record.pb_ratio = fm.pb_ratio
            record.roe = fm.roe
            record.gross_margin = fm.gross_margin
            record.debt_ratio = fm.debt_ratio
            record.free_cash_flow = fm.free_cash_flow

        if context.valuation:
            val = context.valuation
            record.intrinsic_value = val.intrinsic_value
            record.fair_price = val.fair_price
            record.margin_of_safety = val.margin_of_safety
            record.valuation_score = val.valuation_score

        if context.competitive_moat:
            moat = context.competitive_moat
            record.moat_score = moat.overall_score
            record.brand_strength = moat.brand_strength
            record.cost_advantage = moat.cost_advantage

        if context.risk_assessment:
            risk = context.risk_assessment
            record.risk_level = risk.overall_risk_level.value if risk.overall_risk_level else ""
            record.leverage_risk = risk.leverage_risk

        if context.buy_signal:
            record.buy_signal = context.buy_signal.buy_signal.value if context.buy_signal.buy_signal else ""

        if context.sell_signal:
            record.sell_signal = context.sell_signal.sell_signal.value if context.sell_signal.sell_signal else ""

        record.final_signal = context.final_signal.value if context.final_signal else ""
        record.overall_score = context.overall_score

        if context.investment_decision:
            dec = context.investment_decision
            record.decision = dec.decision.value if dec.decision else ""
            record.position_size = dec.position_size
            record.stop_loss = dec.stop_loss_price
            record.take_profit = dec.take_profit_price

        # 保存完整的原始数据（JSON）
        try:
            record.raw_data = json.dumps(context.__dict__, default=str, ensure_ascii=False)
        except Exception:
            record.raw_data = ""

        return record


# 便捷函数
def create_repository(db_path: str = "data/vimaster.db") -> AnalysisRepository:
    """创建分析仓库"""
    return AnalysisRepository(db_path=db_path)
