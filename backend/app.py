"""
E-commerce Price Tracker - Flask Backend
Main application with API endpoints, caching, and scheduled scraping
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_caching import Cache
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import logging
import atexit
from datetime import datetime

from config import Config
from scraper.flipkart_scraper import scrape_flipkart
from database import init_db, insert_price, get_price_history, get_latest_prices
from performance_monitor import timing_decorator, get_performance_stats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate configuration
try:
    Config.validate()
    logger.info("[CONFIG] Configuration validated successfully")
except ValueError as e:
    logger.error(f"[CONFIG] Configuration validation failed: {e}")
    exit(1)

# Initialize Flask app
app = Flask(__name__)

# CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": Config.CORS_ORIGINS,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize caching and compression
cache = Cache(app, config={
    'CACHE_TYPE': Config.CACHE_TYPE,
    'CACHE_DEFAULT_TIMEOUT': Config.CACHE_DEFAULT_TIMEOUT
})
compress = Compress(app)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[Config.RATE_LIMIT_DEFAULT] if Config.RATE_LIMIT_ENABLED else [],
    storage_uri="memory://"
)

# Initialize database
init_db(Config.DB_PATH)


# ==================== API ENDPOINTS ====================

@app.route("/", methods=["GET"])
def index():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "service": "E-commerce Price Tracker API",
        "version": "1.0.0"
    })


@app.route("/track", methods=["POST"])
@limiter.limit("20 per minute")
@timing_decorator("/track")
def track():
    """
    Track product prices
    Request body: {"product": "product_name"}
    """
    try:
        data = request.get_json(force=True)
        product_name = data.get("product")
        
        if not product_name:
            return jsonify({"error": "No product name provided"}), 400
        
        if not isinstance(product_name, str) or len(product_name.strip()) == 0:
            return jsonify({"error": "Invalid product name"}), 400
        
        product_name = product_name.strip()
        
        # Check cache first
        cache_key = f"scrape_{product_name}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.info(f"[CACHE HIT] Using cached data for '{product_name}'")
            flipkart_data = cached_data
        else:
            logger.info(f"[CACHE MISS] Scraping fresh data for '{product_name}'")
            flipkart_data = scrape_flipkart(
                product_name,
                timeout=Config.SCRAPER_TIMEOUT,
                max_retries=Config.SCRAPER_MAX_RETRIES,
                retry_delay=Config.SCRAPER_RETRY_DELAY
            )
            
            if flipkart_data:
                cache.set(cache_key, flipkart_data, timeout=Config.CACHE_SCRAPER_TIMEOUT)
        
        # Save to database
        if flipkart_data:
            for item in flipkart_data:
                insert_price(
                    product=product_name,
                    name=item.get("name"),
                    price=item.get("price"),
                    db_path=Config.DB_PATH
                )
            
            return jsonify({
                "success": True,
                "product": product_name,
                "results": flipkart_data,
                "count": len(flipkart_data)
            })
        else:
            return jsonify({
                "success": False,
                "product": product_name,
                "message": "No results found or scraping failed",
                "results": []
            }), 404
    
    except Exception as e:
        logger.error(f"[ERROR] /track endpoint: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@app.route("/history/<product>", methods=["GET"])
@cache.cached(timeout=Config.CACHE_DB_TIMEOUT, query_string=True)
@timing_decorator("/history/<product>")
def get_history(product):
    """Get full price history for a product"""
    try:
        limit = request.args.get('limit', type=int)
        
        history = get_price_history(
            product=product,
            db_path=Config.DB_PATH,
            limit=limit
        )
        
        return jsonify({
            "product": product,
            "history": history,
            "count": len(history)
        })
    
    except Exception as e:
        logger.error(f"[ERROR] /history endpoint: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@app.route("/latest", methods=["GET"])
@cache.cached(timeout=Config.CACHE_DB_TIMEOUT)
@timing_decorator("/latest")
def get_latest():
    """Get latest tracked products"""
    try:
        limit = request.args.get('limit', default=10, type=int)
        
        if limit < 1 or limit > 100:
            return jsonify({"error": "Limit must be between 1 and 100"}), 400
        
        latest = get_latest_prices(
            db_path=Config.DB_PATH,
            limit=limit
        )
        
        return jsonify({
            "latest": latest,
            "count": len(latest)
        })
    
    except Exception as e:
        logger.error(f"[ERROR] /latest endpoint: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@app.route("/performance", methods=["GET"])
def performance_stats():
    """Get performance statistics"""
    try:
        stats = get_performance_stats()
        return jsonify({
            "performance": stats,
            "cache_config": {
                "type": Config.CACHE_TYPE,
                "scraper_timeout": Config.CACHE_SCRAPER_TIMEOUT,
                "db_timeout": Config.CACHE_DB_TIMEOUT
            }
        })
    except Exception as e:
        logger.error(f"[ERROR] /performance endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500


# ==================== SCHEDULED TASKS ====================

def scheduled_scrape():
    """Background task to scrape products periodically"""
    try:
        logger.info("[SCHEDULER] Running scheduled scrape...")
        
        for product in Config.SCHEDULER_PRODUCTS:
            product = product.strip()
            if not product:
                continue
            
            logger.info(f"[SCHEDULER] Scraping '{product}'")
            
            data = scrape_flipkart(
                product,
                timeout=Config.SCRAPER_TIMEOUT,
                max_retries=Config.SCRAPER_MAX_RETRIES,
                retry_delay=Config.SCRAPER_RETRY_DELAY
            )
            
            if data:
                for item in data:
                    insert_price(
                        product=product,
                        name=item.get("name"),
                        price=item.get("price"),
                        db_path=Config.DB_PATH
                    )
                logger.info(f"[SCHEDULER] Saved {len(data)} items for '{product}'")
            else:
                logger.warning(f"[SCHEDULER] No data found for '{product}'")
        
        logger.info("[SCHEDULER] Scrape completed successfully")
        
    except Exception as e:
        logger.error(f"[SCHEDULER ERROR] {e}")


# Initialize background scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    scheduled_scrape,
    "interval",
    hours=Config.SCHEDULER_INTERVAL_HOURS,
    id="scheduled_scrape",
    replace_existing=True
)
scheduler.start()
logger.info(f"[SCHEDULER] Started with interval: {Config.SCHEDULER_INTERVAL_HOURS} hours")


# Graceful shutdown
def shutdown_scheduler():
    """Shutdown scheduler gracefully"""
    try:
        if scheduler.running:
            scheduler.shutdown(wait=False)
            logger.info("[SCHEDULER] Shutdown completed")
    except Exception as e:
        logger.error(f"[SCHEDULER] Error during shutdown: {e}")

atexit.register(shutdown_scheduler)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded", "message": str(e.description)}), 429


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ==================== MAIN ====================

if __name__ == "__main__":
    logger.info(f"[APP] Starting E-commerce Price Tracker on {Config.HOST}:{Config.PORT}")
    logger.info(f"[APP] Debug mode: {Config.DEBUG}")
    logger.info(f"[APP] CORS origins: {Config.CORS_ORIGINS}")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
