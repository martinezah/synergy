import json
import os

source_auth_url = os.getenv('SYNERGY_SOURCE_AUTH_URL', 'http://localhost:8000/')
source_redirect_url = os.getenv('SYNERGY_SOURCE_REDIRECT_URL', 'http://localhost:8001/_sso/chk')
source_redirect_key = os.getenv('SYNERGY_SOURCE_REDIRECT_KEY', '__key__')
source_cookies = os.getenv('SYNERGY_SOURCE_COOKIES', 'PHPSESSID').split(',')
source_timeout = int(os.getenv('SYNERGY_SOURCE_TIMEOUT', '10'))
source_success_codes = list(map(int, os.getenv('SYNERGY_SOURCE_SUCCESS_CODES', '200').split(',')))

dest_url = os.getenv('SYNERGY_DEST_URL', 'http://localhost:8001/')
dest_cookies = os.getenv('SYNERGY_DEST_COOKIES', 'PHPSESSID').split(',')
dest_timeout = int(os.getenv('SYNERGY_DEST_TIMEOUT', '10'))

redis_host = os.getenv('SYNERGY_REDIS_HOST', 'localhost')
redis_port = int(os.getenv('SYNERGY_REDIS_PORT', '6379'))
redis_db = int(os.getenv('SYNERGY_REDIS_DB', '0'))
redis_prefix = os.getenv('SYNERGY_REDIS_PREFIX', 'sso:')
redis_timeout = int(os.getenv('SYNERGY_REDIS_TIMEOUT', '10'))

logging_config = json.loads(os.getenv('SYNERGY_LOGGING_CONFIG', '{"version": 1, "loggers": {"quart.app": {"level": "DEBUG"}}}'))

