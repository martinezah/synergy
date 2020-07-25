import aiohttp
import aioredis
import json
import logging.config
import sys
import time
import uuid

from aiohttp_requests import requests
from hashlib import sha256
from quart import Quart, request, redirect, make_response

# setup
import settings
logging.config.dictConfig(settings.logging_config)
app = Quart(__name__)

# api
@app.route('/go')
async def go():
    cookies = {}
    for kk in settings.source_cookies:
        vv = request.cookies.get(kk) 
        if vv: cookies[kk] = vv
    resp = await requests.get(settings.source_auth_url, cookies=cookies, timeout=settings.source_timeout)
    if resp.status in settings.source_success_codes:
        key = request.args.get('_k')
        if key:
            nonce = str(uuid.uuid4())
            ts = time.time()
            data = json.dumps({
                'nonce': nonce,
                'key': key,
                'ts': ts,
            })
            ticket = sha256(data.encode()).hexdigest()
            redis_pool = await aioredis.create_pool((settings.redis_host, settings.redis_port), db=settings.redis_db)
            await redis_pool.execute('setex', f'{settings.redis_prefix}{ticket}', settings.ticket_timeout, data) 
            redirect_url = settings.source_redirect_url.replace(settings.source_redirect_key, key)
            app.logger.info(json.dumps({'msg': 'Authentication success', 'redirect': redirect_url, 'ticket': ticket, 'ts': ts}))
            return redirect(f'{redirect_url}?_t={ticket}')
    app.logger.warn(json.dumps({'msg': 'Failed to authenticate', 'status': resp.status, 'cookies': cookies}))
    return ('', 403)

@app.route('/chk')
async def check():
    ts = time.time()
    ticket = request.args.get('_t')
    if ticket:
        redis_pool = await aioredis.create_pool((settings.redis_host, settings.redis_port), db=settings.redis_db)
        data = await redis_pool.execute('get', f'{settings.redis_prefix}{ticket}')
        if data:
            data = json.loads(data)
            ticket_ts = data.get('ts')
            key = data.get('key')
            if ts - ticket_ts <= settings.ticket_timeout:
                async with aiohttp.ClientSession() as session:
                    headers = { 'kbn-xsrf': 'kibana' }
                    login_url = settings.dest_auth_url.replace(settings.dest_auth_key, key)
                    if settings.dest_auth_sub:
                        login_url = login_url.replace(settings.dest_auth_sub, settings.dest_auth_with)
                    auth_json = settings.dest_auth_creds.get(key, settings.dest_auth_creds.get('default'))
                    resp = await session.post(login_url, json=auth_json, headers=headers)
                    if resp.status in settings.dest_success_codes:
                        response = await make_response(redirect(settings.dest_redirect_url))
                        for kk in settings.dest_cookies:
                            vv = resp.cookies.get(kk)
                            if vv:
                                response.set_cookie(kk, vv.value)
                            else:
                                app.logger.warn(json.dumps({'msg': 'Cookie not found', 'cookie': kk}))
                        app.logger.info(json.dumps({'msg': 'Validation success', 'redirect': settings.dest_redirect_url}))
                        return response
    app.logger.warn(json.dumps({'msg': 'Failed to validate login', 'ticket': ticket, 'ts': ts, 'ticket_data': data}))
    return redirect(settings.dest_login_url)

    
# for dev use only    
if __name__ == '__main__': 
    app.run()
