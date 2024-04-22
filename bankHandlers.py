from aiohttp import web
from bankutils import headers
import jwt

async def auth_handler_v1(request):
	config = request.config_dict['config']
	if (request.query.get('key', None) == config.API_KEY):
		payload = {
			'iss': config.SECRET_NAME
		}
		return web.Response(status=200, text=jwt.encode(payload, config.SECRET_KEY, algorithm='HS256'), headers=headers)
	else:
		return web.Response(status=403, text='Forbidden', headers=headers)