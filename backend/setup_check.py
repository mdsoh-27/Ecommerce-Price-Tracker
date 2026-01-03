"""
Setup Validation Script for E-commerce Price Tracker
Verifies dependencies, configuration, and database setup
"""
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_python_version():
    """Check if Python version is compatible"""
    print("[*] Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   [OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   [FAIL] Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False


def check_dependencies():
    """Check if all required packages are installed"""
    print("\n[*] Checking dependencies...")
    
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'flask_caching': 'Flask-Caching',
        'flask_compress': 'Flask-Compress',
        'flask_limiter': 'Flask-Limiter',
        'bs4': 'BeautifulSoup4',
        'requests': 'Requests',
        'apscheduler': 'APScheduler',
        'dotenv': 'python-dotenv',
        'sqlite3': 'SQLite3 (built-in)'
    }
    
    missing = []
    
    for package, display_name in required_packages.items():
        try:
            __import__(package)
            print(f"   [OK] {display_name}")
        except ImportError:
            print(f"   [FAIL] {display_name} - NOT INSTALLED")
            missing.append(display_name)
    
    if missing:
        print(f"\n   [!] Missing packages: {', '.join(missing)}")
        print(f"   Run: pip install -r requirements.txt")
        return False
    
    return True


def check_config():
    """Check if configuration is valid"""
    print("\n[*] Checking configuration...")
    
    try:
        from config import Config
        
        # Validate config
        Config.validate()
        
        print(f"   [OK] Configuration loaded")
        print(f"      - Port: {Config.PORT}")
        print(f"      - Database: {Config.DB_PATH}")
        print(f"      - CORS Origins: {len(Config.CORS_ORIGINS)} configured")
        print(f"      - Cache Type: {Config.CACHE_TYPE}")
        print(f"      - Rate Limiting: {'Enabled' if Config.RATE_LIMIT_ENABLED else 'Disabled'}")
        
        return True
        
    except Exception as e:
        print(f"   [FAIL] Configuration error: {e}")
        return False


def check_database():
    """Check if database can be initialized"""
    print("\n[*] Checking database...")
    
    try:
        from database import init_db
        from config import Config
        
        result = init_db(Config.DB_PATH)
        
        if result:
            print(f"   [OK] Database initialized at {Config.DB_PATH}")
            
            # Check if database file exists
            if os.path.exists(Config.DB_PATH):
                size = os.path.getsize(Config.DB_PATH)
                print(f"      - File size: {size} bytes")
            
            return True
        else:
            print(f"   [FAIL] Database initialization failed")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Database error: {e}")
        return False


def check_scraper():
    """Check if scraper module can be imported"""
    print("\n[*] Checking scraper module...")
    
    try:
        from scraper.flipkart_scraper import scrape_flipkart
        print(f"   [OK] Scraper module loaded")
        return True
    except Exception as e:
        print(f"   [FAIL] Scraper error: {e}")
        return False


def check_env_file():
    """Check if .env file exists"""
    print("\n[*] Checking environment file...")
    
    if os.path.exists('.env'):
        print(f"   [OK] .env file found")
        return True
    else:
        print(f"   [!] .env file not found (using defaults)")
        print(f"      Copy .env.example to .env to customize settings")
        return True  # Not critical


def main():
    """Run all checks"""
    print("=" * 60)
    print("E-COMMERCE PRICE TRACKER - SETUP VALIDATION")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_env_file(),
        check_config(),
        check_database(),
        check_scraper()
    ]
    
    print("\n" + "=" * 60)
    
    if all(checks):
        print("[SUCCESS] ALL CHECKS PASSED!")
        print("\nYou can now start the server:")
        print("   python app.py")
        print("\nOr run the benchmark:")
        print("   python benchmark.py")
        return 0
    else:
        print("[FAILED] SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running the server.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

