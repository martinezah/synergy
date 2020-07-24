import aioredis
import json
import logging.config
import sys

from aiohttp_requests import requests
from quart import Quart, request

# setup
import settings
logging.config.dictConfig(settings.logging_config)
app = Quart(__name__)

# api
@app.route('/go')
async def go():
    # When called, app grabs cookies, checks for a logged in user, extracts org name, makes hash of (user|org|timestamp|nonce) and stores all in redis for TIMEOUT seconds, sends user to redirect with hash as URL param /_sso/chk?_h={hash}
    redis_pool = await aioredis.create_pool((settings.redis_host, settings.redis_port), db=settings.redis_db)
    cookies = {}
    for kk in settings.dest_cookies:
        vv = request.cookies.get(kk) 
        if vv: cookies[kk] = vv
    resp = await requests.get(settings.dest_url, cookies=cookies)
    return "go"

@app.route('/chk')
async def check():
    # When called , grabs url param from request, looks up hash, if valid and in scope, logs int, extracts cookies, sends them to user, and redirects to a URL
    redis_pool = await aioredis.create_pool((settings.redis_host, settings.redis_port), db=settings.redis_db)
    return "check"
    
# for dev use only    
if __name__ == '__main__': 
    app.run()