"""
商业化 API 服务 - RESTful API 接口
"""
import logging
import json
import time
import uuid
import hashlib
import hmac
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict, fields
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
import threading
import os

logger = logging.getLogger(__name__)

# 尝试导入 Flask（可选依赖）
try:
    from flask import Flask, request, jsonify, g
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.warning("Flask 不可用，API 服务将被禁用。安装: pip install flask flask-cors")


class PlanType(Enum):
    """订阅计划类型"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class RateLimitType(Enum):
    """限流类型"""
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"


@dataclass
class ApiKey:
    """API 密钥"""
    key_id: str
    api_key: str
    secret_key: str
    user_id: str
    plan: PlanType = PlanType.FREE
    created_at: str = ""
    expires_at: Optional[str] = None
    enabled: bool = True

    # 配额
    daily_quota: int = 100
    used_today: int = 0
    last_reset_date: str = ""

    # 权限
    permissions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["plan"] = self.plan.value
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ApiKey":
        data = data.copy()
        if "plan" in data:
            data["plan"] = PlanType(data["plan"])
        # 获取 ApiKey 的所有字段名
        valid_fields = {f.name for f in fields(ApiKey)}
        return ApiKey(**{k: v for k, v in data.items() if k in valid_fields})


@dataclass
class UsageRecord:
    """使用记录"""
    record_id: str
    key_id: str
    endpoint: str
    method: str
    timestamp: str
    response_time_ms: float
    status_code: int
    request_size: int = 0
    response_size: int = 0
    ip_address: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlanConfig:
    """计划配置"""
    plan_type: PlanType
    name: str
    daily_quota: int
    rate_limit_per_minute: int
    max_stocks_per_request: int
    features: List[str] = field(default_factory=list)
    price_monthly: float = 0.0
    price_yearly: float = 0.0


# 计划配置
PLAN_CONFIGS = {
    PlanType.FREE: PlanConfig(
        plan_type=PlanType.FREE,
        name="免费版",
        daily_quota=100,
        rate_limit_per_minute=10,
        max_stocks_per_request=5,
        features=["基础分析", "单股分析"],
        price_monthly=0,
        price_yearly=0,
    ),
    PlanType.BASIC: PlanConfig(
        plan_type=PlanType.BASIC,
        name="基础版",
        daily_quota=1000,
        rate_limit_per_minute=60,
        max_stocks_per_request=20,
        features=["基础分析", "单股分析", "组合分析", "历史数据"],
        price_monthly=99,
        price_yearly=999,
    ),
    PlanType.PRO: PlanConfig(
        plan_type=PlanType.PRO,
        name="专业版",
        daily_quota=10000,
        rate_limit_per_minute=300,
        max_stocks_per_request=50,
        features=["全部分析", "实时数据", "导出报告", "API优先支持"],
        price_monthly=299,
        price_yearly=2999,
    ),
    PlanType.ENTERPRISE: PlanConfig(
        plan_type=PlanType.ENTERPRISE,
        name="企业版",
        daily_quota=100000,
        rate_limit_per_minute=1000,
        max_stocks_per_request=200,
        features=["全部功能", "专属支持", "SLA保障", "私有部署"],
        price_monthly=999,
        price_yearly=9999,
    ),
}


class ApiKeyManager:
    """API 密钥管理器"""

    def __init__(self, data_dir: str = "data/api"):
        self.data_dir = data_dir
        self.keys: Dict[str, ApiKey] = {}
        self._lock = threading.Lock()
        os.makedirs(data_dir, exist_ok=True)
        self._load_keys()

    def _load_keys(self) -> None:
        """加载密钥"""
        keys_file = os.path.join(self.data_dir, "api_keys.json")
        if os.path.exists(keys_file):
            with open(keys_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key_data in data.get("keys", []):
                    key = ApiKey.from_dict(key_data)
                    self.keys[key.api_key] = key

    def _save_keys(self) -> None:
        """保存密钥"""
        keys_file = os.path.join(self.data_dir, "api_keys.json")
        data = {"keys": [k.to_dict() for k in self.keys.values()]}
        with open(keys_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_key(self, user_id: str, plan: PlanType = PlanType.FREE) -> ApiKey:
        """创建 API 密钥"""
        key_id = str(uuid.uuid4())[:8]
        api_key = f"vk_{uuid.uuid4().hex[:24]}"
        secret_key = hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:32]

        plan_config = PLAN_CONFIGS[plan]

        key = ApiKey(
            key_id=key_id,
            api_key=api_key,
            secret_key=secret_key,
            user_id=user_id,
            plan=plan,
            created_at=datetime.now().isoformat(),
            daily_quota=plan_config.daily_quota,
            last_reset_date=datetime.now().strftime("%Y-%m-%d"),
            permissions=plan_config.features,
        )

        with self._lock:
            self.keys[api_key] = key
            self._save_keys()

        logger.info(f"API 密钥已创建: {key_id} (用户: {user_id})")
        return key

    def get_key(self, api_key: str) -> Optional[ApiKey]:
        """获取密钥"""
        return self.keys.get(api_key)

    def validate_key(self, api_key: str) -> tuple[bool, str]:
        """验证密钥"""
        key = self.keys.get(api_key)

        if not key:
            return False, "无效的 API 密钥"

        if not key.enabled:
            return False, "API 密钥已禁用"

        if key.expires_at:
            if datetime.fromisoformat(key.expires_at) < datetime.now():
                return False, "API 密钥已过期"

        # 检查配额
        today = datetime.now().strftime("%Y-%m-%d")
        if key.last_reset_date != today:
            key.used_today = 0
            key.last_reset_date = today
            self._save_keys()

        if key.used_today >= key.daily_quota:
            return False, "已超出每日配额"

        return True, "OK"

    def increment_usage(self, api_key: str) -> None:
        """增加使用次数"""
        key = self.keys.get(api_key)
        if key:
            key.used_today += 1
            self._save_keys()

    def revoke_key(self, api_key: str) -> bool:
        """撤销密钥"""
        key = self.keys.get(api_key)
        if key:
            key.enabled = False
            self._save_keys()
            return True
        return False

    def upgrade_plan(self, api_key: str, new_plan: PlanType) -> bool:
        """升级计划"""
        key = self.keys.get(api_key)
        if key:
            plan_config = PLAN_CONFIGS[new_plan]
            key.plan = new_plan
            key.daily_quota = plan_config.daily_quota
            key.permissions = plan_config.features
            self._save_keys()
            return True
        return False


class RateLimiter:
    """API 限流器"""

    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def check_rate_limit(self, key: str, limit: int, window_seconds: int = 60) -> tuple[bool, int]:
        """
        检查限流

        Returns:
            (是否允许, 剩余配额)
        """
        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            if key not in self.requests:
                self.requests[key] = []

            # 清理过期请求
            self.requests[key] = [t for t in self.requests[key] if t > window_start]

            current_count = len(self.requests[key])

            if current_count >= limit:
                return False, 0

            self.requests[key].append(now)
            return True, limit - current_count - 1


class UsageTracker:
    """使用量追踪器"""

    def __init__(self, data_dir: str = "data/api"):
        self.data_dir = data_dir
        self.records: List[UsageRecord] = []
        self._lock = threading.Lock()
        os.makedirs(data_dir, exist_ok=True)

    def record(self, record: UsageRecord) -> None:
        """记录使用"""
        with self._lock:
            self.records.append(record)

            # 定期保存
            if len(self.records) % 100 == 0:
                self._save_records()

    def _save_records(self) -> None:
        """保存记录"""
        today = datetime.now().strftime("%Y%m%d")
        file_path = os.path.join(self.data_dir, f"usage_{today}.json")

        data = {"records": [r.to_dict() for r in self.records]}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def get_usage_stats(self, key_id: str, days: int = 30) -> Dict[str, Any]:
        """获取使用统计"""
        cutoff = datetime.now() - timedelta(days=days)

        key_records = [r for r in self.records
                      if r.key_id == key_id and
                      datetime.fromisoformat(r.timestamp) > cutoff]

        if not key_records:
            return {"total_requests": 0}

        total_time = sum(r.response_time_ms for r in key_records)

        return {
            "total_requests": len(key_records),
            "avg_response_time_ms": total_time / len(key_records),
            "success_rate": sum(1 for r in key_records if r.status_code == 200) / len(key_records),
            "endpoints": list(set(r.endpoint for r in key_records)),
        }


def create_api_app(debug: bool = False) -> Optional["Flask"]:
    """创建 API 应用"""
    if not FLASK_AVAILABLE:
        logger.error("Flask 不可用，无法创建 API 服务")
        return None

    app = Flask(__name__)
    CORS(app)

    # 初始化管理器
    key_manager = ApiKeyManager()
    rate_limiter = RateLimiter()
    usage_tracker = UsageTracker()

    # 认证装饰器
    def require_api_key(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            api_key = request.headers.get("X-API-Key")

            if not api_key:
                return jsonify({"error": "缺少 API 密钥", "code": "MISSING_API_KEY"}), 401

            valid, message = key_manager.validate_key(api_key)
            if not valid:
                return jsonify({"error": message, "code": "INVALID_API_KEY"}), 401

            key = key_manager.get_key(api_key)

            # 检查限流
            plan_config = PLAN_CONFIGS[key.plan]
            allowed, remaining = rate_limiter.check_rate_limit(
                api_key, plan_config.rate_limit_per_minute
            )

            if not allowed:
                return jsonify({"error": "请求过于频繁", "code": "RATE_LIMITED"}), 429

            g.api_key = key
            g.remaining_quota = remaining

            return f(*args, **kwargs)
        return decorated

    # 请求计时中间件
    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(g, 'api_key') and hasattr(g, 'start_time'):
            elapsed = (time.time() - g.start_time) * 1000

            record = UsageRecord(
                record_id=str(uuid.uuid4())[:8],
                key_id=g.api_key.key_id,
                endpoint=request.path,
                method=request.method,
                timestamp=datetime.now().isoformat(),
                response_time_ms=elapsed,
                status_code=response.status_code,
                ip_address=request.remote_addr or "",
            )
            usage_tracker.record(record)
            key_manager.increment_usage(g.api_key.api_key)

            # 添加响应头
            response.headers["X-Remaining-Quota"] = str(g.remaining_quota)
            response.headers["X-Response-Time"] = f"{elapsed:.2f}ms"

        return response

    # ==================== API 路由 ====================

    @app.route("/api/v1/health", methods=["GET"])
    def health_check():
        """健康检查"""
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
        })

    @app.route("/api/v1/plans", methods=["GET"])
    def list_plans():
        """获取订阅计划列表"""
        plans = []
        for plan_type, config in PLAN_CONFIGS.items():
            plans.append({
                "type": plan_type.value,
                "name": config.name,
                "daily_quota": config.daily_quota,
                "rate_limit_per_minute": config.rate_limit_per_minute,
                "max_stocks_per_request": config.max_stocks_per_request,
                "features": config.features,
                "price_monthly": config.price_monthly,
                "price_yearly": config.price_yearly,
            })
        return jsonify({"plans": plans})

    @app.route("/api/v1/keys", methods=["POST"])
    def create_api_key():
        """创建 API 密钥"""
        data = request.get_json() or {}
        user_id = data.get("user_id")
        plan = data.get("plan", "free")

        if not user_id:
            return jsonify({"error": "缺少 user_id"}), 400

        try:
            plan_type = PlanType(plan)
        except ValueError:
            return jsonify({"error": "无效的计划类型"}), 400

        key = key_manager.create_key(user_id, plan_type)

        return jsonify({
            "key_id": key.key_id,
            "api_key": key.api_key,
            "secret_key": key.secret_key,
            "plan": key.plan.value,
            "daily_quota": key.daily_quota,
            "message": "请妥善保存密钥，secret_key 仅显示一次",
        }), 201

    @app.route("/api/v1/keys/info", methods=["GET"])
    @require_api_key
    def get_key_info():
        """获取密钥信息"""
        key = g.api_key
        plan_config = PLAN_CONFIGS[key.plan]

        return jsonify({
            "key_id": key.key_id,
            "plan": key.plan.value,
            "plan_name": plan_config.name,
            "daily_quota": key.daily_quota,
            "used_today": key.used_today,
            "remaining_today": key.daily_quota - key.used_today,
            "features": key.permissions,
            "created_at": key.created_at,
        })

    @app.route("/api/v1/keys/usage", methods=["GET"])
    @require_api_key
    def get_key_usage():
        """获取使用统计"""
        days = request.args.get("days", 30, type=int)
        stats = usage_tracker.get_usage_stats(g.api_key.key_id, days)
        return jsonify(stats)

    @app.route("/api/v1/analyze/<stock_code>", methods=["GET"])
    @require_api_key
    def analyze_stock(stock_code: str):
        """分析单只股票"""
        try:
            from src.schedulers.workflow_scheduler import AnalysisManager

            manager = AnalysisManager()
            context = manager.analyze_single_stock(stock_code)

            if not context:
                return jsonify({"error": f"无法分析股票 {stock_code}"}), 404

            result = {
                "stock_code": context.stock_code,
                "overall_score": context.overall_score,
                "final_signal": context.final_signal.value if context.final_signal else None,
            }

            if context.financial_metrics:
                fm = context.financial_metrics
                result["financial_metrics"] = {
                    "current_price": fm.current_price,
                    "pe_ratio": fm.pe_ratio,
                    "pb_ratio": fm.pb_ratio,
                    "roe": fm.roe,
                    "gross_margin": fm.gross_margin,
                    "debt_ratio": fm.debt_ratio,
                }

            if context.valuation:
                val = context.valuation
                result["valuation"] = {
                    "intrinsic_value": val.intrinsic_value,
                    "fair_price": val.fair_price,
                    "margin_of_safety": val.margin_of_safety,
                    "valuation_score": val.valuation_score,
                }

            if context.competitive_moat:
                moat = context.competitive_moat
                result["moat"] = {
                    "overall_score": moat.overall_score,
                    "brand_strength": moat.brand_strength,
                    "cost_advantage": moat.cost_advantage,
                }

            if context.investment_decision:
                dec = context.investment_decision
                result["decision"] = {
                    "action": dec.decision.value if dec.decision else None,
                    "position_size": dec.position_size,
                    "stop_loss": dec.stop_loss_price,
                    "take_profit": dec.take_profit_price,
                }

            return jsonify(result)
        except Exception as e:
            logger.error(f"分析失败: {str(e)}")
            return jsonify({"error": "分析失败", "detail": str(e)}), 500

    @app.route("/api/v1/analyze/batch", methods=["POST"])
    @require_api_key
    def analyze_batch():
        """批量分析股票"""
        data = request.get_json() or {}
        stock_codes = data.get("stock_codes", [])

        if not stock_codes:
            return jsonify({"error": "缺少 stock_codes"}), 400

        # 检查数量限制
        plan_config = PLAN_CONFIGS[g.api_key.plan]
        if len(stock_codes) > plan_config.max_stocks_per_request:
            return jsonify({
                "error": f"超出单次请求限制 ({plan_config.max_stocks_per_request})",
                "limit": plan_config.max_stocks_per_request,
            }), 400

        try:
            from src.schedulers.workflow_scheduler import AnalysisManager

            manager = AnalysisManager()
            report = manager.analyze_portfolio(stock_codes)

            results = {
                "report_id": report.report_id,
                "total_analyzed": report.total_stocks_analyzed,
                "summary": {
                    "strong_buy": report.strong_buy_count,
                    "buy": report.buy_count,
                    "hold": report.hold_count,
                    "sell": report.sell_count,
                    "strong_sell": report.strong_sell_count,
                },
                "stocks": [],
            }

            for stock in report.stocks:
                results["stocks"].append({
                    "stock_code": stock.stock_code,
                    "overall_score": stock.overall_score,
                    "signal": stock.final_signal.value if stock.final_signal else None,
                })

            return jsonify(results)
        except Exception as e:
            logger.error(f"批量分析失败: {str(e)}")
            return jsonify({"error": "分析失败", "detail": str(e)}), 500

    @app.route("/api/v1/quote/<stock_code>", methods=["GET"])
    @require_api_key
    def get_quote(stock_code: str):
        """获取股票行情"""
        try:
            from src.data.akshare_provider import AkshareDataProvider

            metrics = AkshareDataProvider.get_financial_metrics(stock_code)

            if not metrics:
                return jsonify({"error": f"无法获取 {stock_code} 行情"}), 404

            return jsonify({
                "stock_code": stock_code,
                "current_price": metrics.current_price,
                "pe_ratio": metrics.pe_ratio,
                "pb_ratio": metrics.pb_ratio,
                "roe": metrics.roe,
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # 错误处理
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "接口不存在"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "服务器内部错误"}), 500

    return app


def run_api_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """运行 API 服务器"""
    app = create_api_app(debug=debug)
    if app:
        print(f"\n{'='*60}")
        print("VIMaster API 服务")
        print(f"{'='*60}")
        print(f"地址: http://{host}:{port}")
        print(f"文档: http://{host}:{port}/api/v1/health")
        print(f"{'='*60}\n")
        app.run(host=host, port=port, debug=debug)
    else:
        print("无法启动 API 服务，请安装 Flask: pip install flask flask-cors")
