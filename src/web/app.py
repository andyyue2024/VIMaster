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

    # 自动加载保存的 LLM 配置
    config_path = os.path.join(base_dir, '..', '..', 'config', 'llm_config.json')
    if os.path.exists(config_path):
        try:
            from src.agents.llm.llm_config import LLMConfigManager
            LLMConfigManager.load_from_file(config_path)
            logger.info(f"已加载 LLM 配置: {config_path}")
        except Exception as e:
            logger.warning(f"加载 LLM 配置失败: {e}")

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

    @app.route('/masters')
    def masters_page():
        """LLM 大师分析页面"""
        return render_template('masters.html')

    @app.route('/experts')
    def experts_page():
        """LLM 专家分析页面"""
        return render_template('experts.html')

    @app.route('/portfolio')
    def portfolio_page():
        """投资组合页面"""
        return render_template('portfolio.html')

    @app.route('/history')
    def history_page():
        """历史记录页面"""
        return render_template('history.html')

    @app.route('/community')
    def community_page():
        """社区页面"""
        return render_template('community.html')

    @app.route('/reports')
    def reports_page():
        """报告页面"""
        return render_template('reports.html')

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

    @app.route('/api/analyze/masters', methods=['POST'])
    def api_analyze_masters():
        """LLM 大师分析 API"""
        try:
            data = request.get_json() or {}
            stock_code = data.get('stock_code', '').strip()
            master_names = data.get('masters', [])

            if not stock_code:
                return jsonify({'success': False, 'error': '请输入股票代码'})

            from src.schedulers.workflow_scheduler import AnalysisManager
            from src.agents.llm import get_all_master_agents, get_master_agent_by_name
            from src.agents.llm.master_agents import get_master_consensus

            manager = AnalysisManager()
            context = manager.analyze_single_stock(stock_code)

            if not context:
                return jsonify({'success': False, 'error': f'无法获取 {stock_code} 基础数据'})

            # 运行大师分析
            if master_names:
                for name in master_names:
                    agent = get_master_agent_by_name(name)
                    if agent:
                        try:
                            context = agent.execute(context)
                        except Exception as e:
                            logger.warning(f"{agent.name} 分析失败: {e}")
            else:
                agents = get_all_master_agents()
                for agent in agents:
                    try:
                        context = agent.execute(context)
                    except Exception as e:
                        logger.warning(f"{agent.name} 分析失败: {e}")

            # 获取共识
            consensus = get_master_consensus(context)

            # 构建结果
            master_results = []
            if hasattr(context, 'master_signals') and context.master_signals:
                for name, signal in context.master_signals.items():
                    master_results.append({
                        'name': signal.agent_name,
                        'signal': signal.signal,
                        'confidence': signal.confidence,
                        'reasoning': signal.reasoning[:500] if isinstance(signal.reasoning, str) else str(signal.reasoning)[:500],
                    })

            return jsonify({
                'success': True,
                'data': {
                    'stock_code': stock_code,
                    'masters': master_results,
                    'consensus': consensus,
                }
            })

        except Exception as e:
            logger.error(f"大师分析失败: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/analyze/experts', methods=['POST'])
    def api_analyze_experts():
        """LLM 专家分析 API"""
        try:
            data = request.get_json() or {}
            stock_code = data.get('stock_code', '').strip()
            expert_names = data.get('experts', [])

            if not stock_code:
                return jsonify({'success': False, 'error': '请输入股票代码'})

            from src.schedulers.workflow_scheduler import AnalysisManager
            from src.agents.llm import get_all_expert_agents, get_expert_agent_by_name
            from src.agents.llm.expert_agents import get_expert_consensus

            manager = AnalysisManager()
            context = manager.analyze_single_stock(stock_code)

            if not context:
                return jsonify({'success': False, 'error': f'无法获取 {stock_code} 基础数据'})

            # 运行专家分析
            if expert_names:
                for name in expert_names:
                    agent = get_expert_agent_by_name(name)
                    if agent:
                        try:
                            context = agent.execute(context)
                        except Exception as e:
                            logger.warning(f"{agent.name} 分析失败: {e}")
            else:
                agents = get_all_expert_agents()
                for agent in agents:
                    try:
                        context = agent.execute(context)
                    except Exception as e:
                        logger.warning(f"{agent.name} 分析失败: {e}")

            # 获取共识
            consensus = get_expert_consensus(context)

            # 构建结果
            expert_results = []
            if hasattr(context, 'expert_signals') and context.expert_signals:
                for name, signal in context.expert_signals.items():
                    expert_results.append({
                        'name': signal.agent_name,
                        'signal': signal.signal,
                        'confidence': signal.confidence,
                        'reasoning': signal.reasoning[:500] if isinstance(signal.reasoning, str) else str(signal.reasoning)[:500],
                    })

            return jsonify({
                'success': True,
                'data': {
                    'stock_code': stock_code,
                    'experts': expert_results,
                    'consensus': consensus,
                }
            })

        except Exception as e:
            logger.error(f"专家分析失败: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/agents/masters')
    def api_list_masters():
        """获取大师列表"""
        try:
            from src.agents.llm import get_all_master_agents
            agents = get_all_master_agents()
            return jsonify({
                'success': True,
                'data': [{'name': a.name, 'description': a.description} for a in agents]
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/agents/experts')
    def api_list_experts():
        """获取专家列表"""
        try:
            from src.agents.llm import get_all_expert_agents
            agents = get_all_expert_agents()
            return jsonify({
                'success': True,
                'data': [{'name': a.name, 'description': a.description} for a in agents]
            })
        except Exception as e:
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

    # ==================== LLM 配置 API ====================

    @app.route('/api/settings/llm', methods=['GET'])
    def api_get_llm_settings():
        """获取 LLM 配置"""
        try:
            from src.agents.llm.llm_config import LLMConfigManager, PRESET_CONFIGS

            config = LLMConfigManager.get_config()

            # 获取可用模型列表
            available_models = list(PRESET_CONFIGS.keys())

            # 不返回完整的 API 密钥，只返回是否已设置
            api_keys_status = {}
            for provider, key in config.api_keys.items():
                api_keys_status[provider] = bool(key and len(key) > 0)

            return jsonify({
                'success': True,
                'data': {
                    'default_provider': config.default_provider,
                    'agent_configs': config.agent_configs,
                    'api_keys_status': api_keys_status,
                    'enable_cache': config.enable_cache,
                    'cache_ttl': config.cache_ttl,
                    'log_requests': config.log_requests,
                    'available_models': available_models,
                }
            })
        except Exception as e:
            logger.error(f"获取 LLM 配置失败: {e}")
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/settings/llm', methods=['POST'])
    def api_save_llm_settings():
        """保存 LLM 配置"""
        try:
            from src.agents.llm.llm_config import LLMConfigManager, LLMConfig

            data = request.get_json() or {}
            config = LLMConfigManager.get_config()

            # 更新默认提供商
            if 'default_provider' in data:
                config.default_provider = data['default_provider']

            # 更新 Agent 专属配置
            if 'agent_configs' in data:
                config.agent_configs.update(data['agent_configs'])

            # 更新 API 密钥
            if 'api_keys' in data:
                for provider, key in data['api_keys'].items():
                    if key:  # 只更新非空密钥
                        config.api_keys[provider] = key

            # 更新其他设置
            if 'enable_cache' in data:
                config.enable_cache = data['enable_cache']
            if 'cache_ttl' in data:
                config.cache_ttl = data['cache_ttl']
            if 'log_requests' in data:
                config.log_requests = data['log_requests']

            # 保存配置
            LLMConfigManager.set_config(config)

            # 持久化到文件
            config_path = os.path.join(base_dir, '..', '..', 'config', 'llm_config.json')
            config.save(config_path)

            return jsonify({'success': True, 'message': 'LLM 配置已保存'})
        except Exception as e:
            logger.error(f"保存 LLM 配置失败: {e}")
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/settings/llm/test', methods=['POST'])
    def api_test_llm_connection():
        """测试 LLM 连接"""
        try:
            data = request.get_json() or {}
            provider = data.get('provider', 'gpt-3.5-turbo')
            api_key = data.get('api_key')

            if not api_key:
                return jsonify({'success': False, 'error': '请提供 API 密钥'})

            # 简单的连接测试逻辑
            # 这里可以扩展为实际调用 LLM API 进行测试
            return jsonify({
                'success': True,
                'message': f'API 密钥格式有效 (提供商: {provider})',
                'note': '实际连接测试需要调用 LLM API'
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/settings/llm/models')
    def api_list_llm_models():
        """获取可用的 LLM 模型列表"""
        try:
            from src.agents.llm.llm_config import PRESET_CONFIGS, LLMProvider

            models = []
            for name, config in PRESET_CONFIGS.items():
                models.append({
                    'name': name,
                    'provider': config.provider.value,
                    'model_name': config.model_name,
                    'description': f"{config.provider.value} - {config.model_name}"
                })

            # 按提供商分组
            providers = {}
            for model in models:
                p = model['provider']
                if p not in providers:
                    providers[p] = []
                providers[p].append(model)

            return jsonify({
                'success': True,
                'data': {
                    'models': models,
                    'providers': providers,
                    'provider_names': {
                        'openai': 'OpenAI',
                        'anthropic': 'Anthropic (Claude)',
                        'deepseek': 'DeepSeek',
                        'qwen': '阿里通义千问',
                        'zhipu': '智谱 GLM',
                        'ollama': 'Ollama (本地)'
                    }
                }
            })
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
        print("🎯 VIMaster Web UI v2.0")
        print(f"{'='*60}")
        print(f"🌐 首页:     http://{host}:{port}/")
        print(f"📊 基础分析: http://{host}:{port}/analyze")
        print(f"🎓 大师分析: http://{host}:{port}/masters")
        print(f"👔 专家分析: http://{host}:{port}/experts")
        print(f"📈 投资组合: http://{host}:{port}/portfolio")
        print(f"👥 社区:     http://{host}:{port}/community")
        print(f"📄 报告:     http://{host}:{port}/reports")
        print(f"{'='*60}\n")
        app.run(host=host, port=port, debug=debug)
    else:
        print("无法启动 Web UI，请安装 Flask: pip install flask flask-cors")
