"""
Flask web application for monitoring the Reddit Trading Bot
Real-time dashboard with LLM monitoring, sentiment tracking, and trading signals
"""

import logging
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from database import MongoDBConnection
from llm_processor import LLMProcessor
from config_loader import get_config
import json

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Initialize database connection
try:
    db = MongoDBConnection()
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    db = None

# Initialize config
config = get_config()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_db():
    """Get database connection"""
    global db
    if db is None:
        try:
            db = MongoDBConnection()
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
    return db

def get_collections():
    """Get all collections from database"""
    database = get_db()
    if database is None:
        return {}
    return database.collections if database.collections is not None else {}

def safe_count(collection, query=None):
    """Safely count documents in a collection"""
    if collection is None:
        return 0
    try:
        return collection.count_documents(query or {})
    except Exception as e:
        logger.error(f"Error counting documents: {e}")
        return 0

# ============================================================================
# API ENDPOINTS - DASHBOARD DATA
# ============================================================================

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get overall dashboard statistics"""
    collections = get_collections()

    posts_col = collections.get('posts')
    comments_col = collections.get('comments')
    sentiment_col = collections.get('sentiment_analysis')
    prices_col = collections.get('stock_prices')
    patterns_col = collections.get('patterns')
    llm_col = collections.get('llm_responses')

    try:
        stats = {
            'posts': safe_count(posts_col),
            'comments': safe_count(comments_col),
            'sentiments_analyzed': safe_count(sentiment_col),
            'stock_prices': safe_count(prices_col),
            'patterns_detected': safe_count(patterns_col),
            'llm_calls': safe_count(llm_col),
            'timestamp': datetime.utcnow().isoformat()
        }

        # Get unique stocks mentioned
        if sentiment_col is not None:
            try:
                stocks = sentiment_col.distinct('stock_symbol')
                stats['unique_stocks'] = len(stocks) if stocks else 0
            except Exception as e:
                logger.error(f"Error getting unique stocks: {e}")
                stats['unique_stocks'] = 0
        else:
            stats['unique_stocks'] = 0

        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment/summary', methods=['GET'])
def get_sentiment_summary():
    """Get sentiment distribution summary"""
    collections = get_collections()
    sentiment_col = collections.get('sentiment_analysis')

    if sentiment_col is None:
        return jsonify({'bullish': 0, 'neutral': 0, 'bearish': 0, 'total': 0})

    try:
        # Unwind sentiments array and count by sentiment
        pipeline = [
            {
                '$project': {
                    'sentiments': {'$objectToArray': '$sentiments'}
                }
            },
            {
                '$unwind': '$sentiments'
            },
            {
                '$group': {
                    '_id': '$sentiments.v.sentiment',
                    'count': {'$sum': 1}
                }
            }
        ]

        results = list(sentiment_col.aggregate(pipeline))

        summary = {
            'bullish': 0,
            'neutral': 0,
            'bearish': 0,
            'total': 0
        }

        for result in results:
            sentiment = result['_id'].lower() if result['_id'] else 'neutral'
            count = result['count']
            if sentiment in summary:
                summary[sentiment] = count
            summary['total'] += count

        return jsonify(summary)
    except Exception as e:
        logger.error(f"Error getting sentiment summary: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/top', methods=['GET'])
def get_top_stocks():
    """Get top mentioned stocks with sentiment"""
    collections = get_collections()
    sentiment_col = collections.get('sentiment_analysis')

    if sentiment_col is None:
        return jsonify({'stocks': []})

    try:
        limit = request.args.get('limit', 10, type=int)

        # Process all records to extract and aggregate sentiment by stock
        all_docs = list(sentiment_col.find({}))
        stock_data = {}

        for doc in all_docs:
            sentiments = doc.get('sentiments', {})
            if isinstance(sentiments, dict):
                for symbol, sentiment_info in sentiments.items():
                    if symbol not in stock_data:
                        stock_data[symbol] = {
                            'mentions': 0,
                            'bullish': 0,
                            'bearish': 0,
                            'neutral': 0,
                            'scores': []
                        }

                    stock_data[symbol]['mentions'] += 1
                    sentiment_type = sentiment_info.get('sentiment', 'NEUTRAL').upper()
                    score = sentiment_info.get('score', 0)

                    if sentiment_type == 'BULLISH':
                        stock_data[symbol]['bullish'] += 1
                    elif sentiment_type == 'BEARISH':
                        stock_data[symbol]['bearish'] += 1
                    else:
                        stock_data[symbol]['neutral'] += 1

                    stock_data[symbol]['scores'].append(score)

        # Sort by mentions and get top N
        sorted_stocks = sorted(stock_data.items(), key=lambda x: x[1]['mentions'], reverse=True)[:limit]

        stocks = []
        for symbol, data in sorted_stocks:
            total = data['mentions']
            bullish_ratio = data['bullish'] / total if total > 0 else 0
            avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0

            stocks.append({
                'symbol': symbol,
                'mentions': total,
                'bullish': data['bullish'],
                'bearish': data['bearish'],
                'neutral': data['neutral'],
                'bullish_ratio': round(bullish_ratio, 2),
                'avg_sentiment_score': round(float(avg_score), 2)
            })

        return jsonify({'stocks': stocks})
    except Exception as e:
        logger.error(f"Error getting top stocks: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# API ENDPOINTS - LLM MONITORING
# ============================================================================

@app.route('/api/llm/stats', methods=['GET'])
def get_llm_stats():
    """Get LLM call statistics"""
    collections = get_collections()
    llm_col = collections.get('llm_responses')

    if llm_col is None:
        return jsonify({
            'total_calls': 0,
            'success': 0,
            'errors': 0,
            'exceptions': 0,
            'success_rate': 0
        })

    try:
        pipeline = [
            {
                '$group': {
                    '_id': '$status',
                    'count': {'$sum': 1}
                }
            }
        ]

        results = list(llm_col.aggregate(pipeline))

        stats = {
            'total_calls': 0,
            'success': 0,
            'errors': 0,
            'exceptions': 0
        }

        for result in results:
            status = result['_id']
            count = result['count']
            stats['total_calls'] += count

            if status == 'success':
                stats['success'] = count
            elif status == 'error':
                stats['errors'] = count
            elif status == 'exception':
                stats['exceptions'] = count

        stats['success_rate'] = round(
            (stats['success'] / stats['total_calls'] * 100)
            if stats['total_calls'] > 0 else 0,
            2
        )

        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting LLM stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/llm/recent', methods=['GET'])
def get_recent_llm_calls():
    """Get recent LLM calls"""
    collections = get_collections()
    llm_col = collections.get('llm_responses')

    if llm_col is None:
        return jsonify({'calls': []})

    try:
        limit = request.args.get('limit', 20, type=int)

        calls = list(
            llm_col.find(
                {},
                {
                    'timestamp': 1,
                    'model': 1,
                    'status': 1,
                    'prompt_length': 1,
                    'response_length': 1,
                    'error': 1
                }
            )
            .sort('timestamp', -1)
            .limit(limit)
        )

        # Convert ObjectId to string and format data
        formatted_calls = []
        for call in calls:
            formatted_calls.append({
                'id': str(call['_id']),
                'timestamp': call['timestamp'].isoformat() if hasattr(call['timestamp'], 'isoformat') else str(call['timestamp']),
                'model': call.get('model', 'unknown'),
                'status': call.get('status', 'unknown'),
                'prompt_length': call.get('prompt_length', 0),
                'response_length': call.get('response_length', 0),
                'error': call.get('error', None)
            })

        return jsonify({'calls': formatted_calls})
    except Exception as e:
        logger.error(f"Error getting recent LLM calls: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/llm/errors', methods=['GET'])
def get_llm_errors():
    """Get LLM error details"""
    collections = get_collections()
    llm_col = collections.get('llm_responses')

    if llm_col is None:
        return jsonify({'errors': []})

    try:
        errors = list(
            llm_col.find(
                {'status': {'$in': ['error', 'exception']}},
                {
                    'timestamp': 1,
                    'status': 1,
                    'error': 1,
                    'prompt': 1
                }
            )
            .sort('timestamp', -1)
            .limit(10)
        )

        formatted_errors = []
        for error in errors:
            formatted_errors.append({
                'id': str(error['_id']),
                'timestamp': error['timestamp'].isoformat() if hasattr(error['timestamp'], 'isoformat') else str(error['timestamp']),
                'status': error.get('status', 'unknown'),
                'error': error.get('error', 'Unknown error'),
                'prompt': error.get('prompt', '')[:100] + '...'  # First 100 chars
            })

        return jsonify({'errors': formatted_errors})
    except Exception as e:
        logger.error(f"Error getting LLM errors: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# API ENDPOINTS - TRADING PATTERNS
# ============================================================================

@app.route('/api/patterns/latest', methods=['GET'])
def get_latest_patterns():
    """Get latest detected trading patterns"""
    collections = get_collections()
    patterns_col = collections.get('patterns')

    if patterns_col is None:
        return jsonify({'patterns': []})

    try:
        limit = request.args.get('limit', 10, type=int)

        patterns = list(
            patterns_col.find({})
            .sort('timestamp', -1)
            .limit(limit)
        )

        formatted_patterns = []
        for pattern in patterns:
            formatted_patterns.append({
                'id': str(pattern['_id']),
                'symbol': pattern.get('symbol', 'N/A'),
                'pattern_type': pattern.get('pattern_type', 'unknown'),
                'confidence': round(pattern.get('confidence', 0), 2),
                'timestamp': pattern.get('timestamp', '').isoformat() if hasattr(pattern.get('timestamp'), 'isoformat') else str(pattern.get('timestamp', '')),
                'description': pattern.get('description', '')
            })

        return jsonify({'patterns': formatted_patterns})
    except Exception as e:
        logger.error(f"Error getting patterns: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# API ENDPOINTS - HISTORICAL DATA
# ============================================================================

@app.route('/api/data/timeline', methods=['GET'])
def get_data_timeline():
    """Get data collection timeline"""
    collections = get_collections()
    posts_col = collections.get('posts')

    if posts_col is None:
        return jsonify({'timeline': []})

    try:
        days = request.args.get('days', 7, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)

        pipeline = [
            {
                '$match': {
                    'created_at': {'$gte': start_date}
                }
            },
            {
                '$group': {
                    '_id': {
                        '$dateToString': {'format': '%Y-%m-%d', 'date': '$created_at'}
                    },
                    'posts': {'$sum': 1}
                }
            },
            {
                '$sort': {'_id': 1}
            }
        ]

        results = list(posts_col.aggregate(pipeline))

        timeline = []
        for result in results:
            timeline.append({
                'date': result['_id'],
                'posts': result['posts']
            })

        return jsonify({'timeline': timeline})
    except Exception as e:
        logger.error(f"Error getting timeline: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PAGE ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/test')
def test_page():
    """Test API page"""
    return render_template('test.html')

@app.route('/debug')
def debug_page():
    """Debug page for troubleshooting"""
    return render_template('debug.html')

@app.route('/llm-monitor')
def llm_monitor():
    """LLM monitoring page"""
    return render_template('llm_monitor.html')

@app.route('/stocks')
def stocks_page():
    """Stocks and sentiment page"""
    return render_template('stocks.html')

@app.route('/patterns')
def patterns_page():
    """Trading patterns page"""
    return render_template('patterns.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    database = get_db()

    return jsonify({
        'status': 'healthy' if database is not None else 'unhealthy',
        'database': 'connected' if database is not None else 'disconnected',
        'timestamp': datetime.utcnow().isoformat()
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    import logging.config

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("Starting Reddit Trading Bot Web Dashboard")
    logger.info("Dashboard available at http://localhost:5000")

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
