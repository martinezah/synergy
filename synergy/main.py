import aioredis
import json
import logging.config
import sys
import time
import uuid

from aiohttp_requests import requests
from hashlib import sha256
from quart import Quart, request, redirect

# setup
import settings
logging.config.dictConfig(settings.logging_config)
app = Quart(__name__)

# api
@app.route('/go')
async def go():
    redis_pool = await aioredis.create_pool((settings.redis_host, settings.redis_port), db=settings.redis_db)
    cookies = {}
    for kk in settings.source_cookies:
        vv = request.cookies.get(kk) 
        if vv: cookies[kk] = vv
    #app.logger.debug(f"cookies: {cookies}")
    resp = await requests.get(settings.source_auth_url, cookies=cookies, timeout=settings.source_timeout)
    _data = await resp.text()
    #app.logger.debug(f"resp: {resp.status} {_data}")
    if resp.status in settings.source_success_codes:
        key = request.args.get('_k')
        if key:
            nonce = str(uuid.uuid4())
            ts = time.gmtime()
            data = json.dumps({
                'nonce': nonce,
                'key': key,
                'ts': ts,
            })
            ticket = sha256(data.encode()).hexdigest()
            await redis_pool.execute("setex", f"{settings.redis_prefix}{ticket}", settings.redis_timeout, data) 
            redirect_url = settings.source_redirect_url.replace(settings.source_redirect_key, key)
            return redirect(f"{redirect_url}?_t={ticket}")
    app.logger.warn(json.dumps({"message": "Synergy auth error"}))
    return ('', 403)

@app.route('/chk')
async def check():
    # When called , grabs url param from request, looks up hash, if valid and in scope, logs int, extracts cookies, sends them to user, and redirects to a URL
    redis_pool = await aioredis.create_pool((settings.redis_host, settings.redis_port), db=settings.redis_db)
    return "check"
    
# for dev use only    
if __name__ == '__main__': 
    app.run()
