"""
Web UI 界面 - 基于 Flask 的 Web 应用
"""
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# 尝试导入 Flask
try:
    from flask import Flask, render_template, request, jsonify, redirect, url_for, session
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.warning("Flask 不可用，Web UI 将被禁用。安装: pip install flask flask-cors")


def create_web_app(debug: bool = False) -> Optional["Flask"]:
    """创建 Web 应用"""
    if not FLASK_AVAILABLE:
        logger.error("Flask 不可用，无法创建 Web UI")
        return None

    # 获取模板和静态文件目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')

    # 确保目录存在
    os.makedirs(template_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'css'), exist_ok=True)
    os.makedirs(os.path.join(static_dir, 'js'), exist_ok=True)

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.secret_key = 'vimaster_secret_key_2026'
    CORS(app)

    # ==================== 页面路由 ====================

    @app.route('/')
    def index():
        """首页"""
        return render_template('index.html')

    @app.route('/analyze')
    def analyze_page():
        """分析页面"""
        return render_template('analyze.html')

    @app.route('/portfolio')
    def portfolio_page():
        """投资组合页面"""
        return render_template('portfolio.html')

    @app.route('/history')
    def history_page():
        """历史记录页面"""
        return render_template('history.html')

    @app.route('/settings')
    def settings_page():
        """设置页面"""
        return render_template('settings.html')

    # ==================== API 路由 ====================

    @app.route('/api/analyze', methods=['POST'])
    def api_analyze():
        """分析股票 API"""
        try:
            data = request.get_json() or {}
            stock_code = data.get('stock_code', '').strip()

            if not stock_code:
                return jsonify({'success': False, 'error': '请输入股票代码'})

            # 导入分析模块
            from src.schedulers.workflow_scheduler import AnalysisManager

            manager = AnalysisManager()
            context = manager.analyze_single_stock(stock_code)

            if not context:
                return jsonify({'success': False, 'error': f'无法分析股票 {stock_code}'})

            # 构建结果
            result = {
                'success': True,
                'data': {
                    'stock_code': context.stock_code,
                    'overall_score': round(context.overall_score, 2),
                    'final_signal': context.final_signal.value if context.final_signal else 'N/A',
                    'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                }
            }

            # 财务指标
            if context.financial_metrics:
                fm = context.financial_metrics
                result['data']['financial'] = {
                    'current_price': fm.current_price,
                    'pe_ratio': fm.pe_ratio,
                    'pb_ratio': fm.pb_ratio,
                    'roe': round(fm.roe * 100, 2) if fm.roe else None,
                    'gross_margin': round(fm.gross_margin * 100, 2) if fm.gross_margin else None,
                    'debt_ratio': round(fm.debt_ratio * 100, 2) if fm.debt_ratio else None,
                }

            # 估值
            if context.valuation:
                val = context.valuation
                result['data']['valuation'] = {
                    'intrinsic_value': round(val.intrinsic_value, 2) if val.intrinsic_value else None,
                    'fair_price': round(val.fair_price, 2) if val.fair_price else None,
                    'margin_of_safety': round(val.margin_of_safety, 2) if val.margin_of_safety else None,
                    'valuation_score': round(val.valuation_score, 1) if val.valuation_score else None,
                }

            # 护城河
            if context.competitive_moat:
                moat = context.competitive_moat
                result['data']['moat'] = {
                    'overall_score': round(moat.overall_score, 1),
                    'brand_strength': round(moat.brand_strength, 2),
                    'cost_advantage': round(moat.cost_advantage, 2),
                    'network_effect': round(moat.network_effect, 2),
                    'switching_cost': round(moat.switching_cost, 2),
                }

            # 风险评估
            if context.risk_assessment:
                risk = context.risk_assessment
                result['data']['risk'] = {
                    'risk_level': risk.overall_risk_level.value if risk.overall_risk_level else 'N/A',
                    'leverage_risk': round(risk.leverage_risk, 2),
                    'industry_risk': round(risk.industry_risk, 2),
                    'company_risk': round(risk.company_risk, 2),
                }

            # 投资决策
            if context.investment_decision:
                dec = context.investment_decision
                result['data']['decision'] = {
                    'action': dec.decision.value if dec.decision else 'N/A',
                    'position_size': round(dec.position_size * 100, 1) if dec.position_size else None,
                    'stop_loss': round(dec.stop_loss_price, 2) if dec.stop_loss_price else None,
                    'take_profit': round(dec.take_profit_price, 2) if dec.take_profit_price else None,
                    'conviction': round(dec.conviction_level, 2) if dec.conviction_level else None,
                }

            # 买卖信号
            if context.buy_signal:
                result['data']['buy_signal'] = {
                    'signal': context.buy_signal.buy_signal.value if context.buy_signal.buy_signal else 'N/A',
                    'confidence': round(context.buy_signal.confidence_score, 2),
                }

            if context.sell_signal:
                result['data']['sell_signal'] = {
                    'signal': context.sell_signal.sell_signal.value if context.sell_signal.sell_signal else 'N/A',
                    'confidence': round(context.sell_signal.confidence_score, 2),
                }

            return jsonify(result)

        except Exception as e:
            logger.error(f"分析失败: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/analyze/batch', methods=['POST'])
    def api_analyze_batch():
        """批量分析 API"""
        try:
            data = request.get_json() or {}
            stock_codes = data.get('stock_codes', [])

            if not stock_codes:
                return jsonify({'success': False, 'error': '请输入股票代码'})

            from src.schedulers.workflow_scheduler import AnalysisManager

            manager = AnalysisManager()
            report = manager.analyze_portfolio(stock_codes)

            results = {
                'success': True,
                'data': {
                    'report_id': report.report_id,
                    'total_analyzed': report.total_stocks_analyzed,
                    'summary': {
                        'strong_buy': report.strong_buy_count,
                        'buy': report.buy_count,
                        'hold': report.hold_count,
                        'sell': report.sell_count,
                        'strong_sell': report.strong_sell_count,
                    },
                    'stocks': []
                }
            }

            for stock in report.stocks:
                stock_data = {
                    'stock_code': stock.stock_code,
                    'overall_score': round(stock.overall_score, 2),
                    'signal': stock.final_signal.value if stock.final_signal else 'N/A',
                }

                if stock.financial_metrics:
                    stock_data['current_price'] = stock.financial_metrics.current_price

                if stock.valuation:
                    stock_data['fair_price'] = round(stock.valuation.fair_price, 2) if stock.valuation.fair_price else None
                    stock_data['margin_of_safety'] = round(stock.valuation.margin_of_safety, 2) if stock.valuation.margin_of_safety else None

                if stock.investment_decision:
                    stock_data['position_size'] = round(stock.investment_decision.position_size * 100, 1) if stock.investment_decision.position_size else None

                results['data']['stocks'].append(stock_data)

            return jsonify(results)

        except Exception as e:
            logger.error(f"批量分析失败: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/history')
    def api_history():
        """获取分析历史"""
        try:
            stock_code = request.args.get('stock_code', '')
            limit = request.args.get('limit', 20, type=int)

            from src.storage import AnalysisRepository

            repo = AnalysisRepository()

            if stock_code:
                records = repo.get_history(stock_code, limit)
            else:
                records = repo.get_all_latest()

            data = []
            for record in records:
                data.append({
                    'id': record.id,
                    'stock_code': record.stock_code,
                    'analysis_date': record.analysis_date,
                    'overall_score': record.overall_score,
                    'final_signal': record.final_signal,
                    'current_price': record.current_price,
                })

            return jsonify({'success': True, 'data': data})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/stats')
    def api_stats():
        """获取统计信息"""
        try:
            from src.storage import AnalysisRepository

            repo = AnalysisRepository()
            stats = repo.get_stats()

            return jsonify({'success': True, 'data': stats})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    # 错误处理
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    return app


def run_web_server(host: str = "0.0.0.0", port: int = 8080, debug: bool = False):
    """运行 Web 服务器"""
    app = create_web_app(debug=debug)
    if app:
        print(f"\n{'='*60}")
        print("🎯 VIMaster Web UI")
        print(f"{'='*60}")
        print(f"🌐 地址: http://{host}:{port}")
        print(f"📊 分析: http://{host}:{port}/analyze")
        print(f"📈 组合: http://{host}:{port}/portfolio")
        print(f"{'='*60}\n")
        app.run(host=host, port=port, debug=debug)
    else:
        print("无法启动 Web UI，请安装 Flask: pip install flask flask-cors")
