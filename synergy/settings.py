import json
import os

source_url = os.getenv('SYNERGY_SOURCE_URL', 'http://localhost:8000/')
source_cookies = os.getenv('SYNERGY_SOURCE_COOKIES', 'PHPSESSID').split(',')

dest_url = os.getenv('SYNERGY_DEST_URL', 'http://localhost:8001/')
dest_cookies = os.getenv('SYNERGY_DEST_COOKIES', 'PHPSESSID').split(',')

redis_host = os.getenv('SYNERGY_REDIS_HOST', 'localhost')
redis_port = int(os.getenv('SYNERGY_REDIS_PORT', '6379'))
redis_db = int(os.getenv('SYNERGY_REDIS_DB', '0'))
redis_prefix = os.getenv('SYNERGY_REDIS_PREFIX', 'sso:')

logging_config = json.loads(os.getenv('SYNERGY_LOGGING_CONFIG', '{"version": 1, "loggers": {"quart.app": {"level": "DEBUG"}}}'))