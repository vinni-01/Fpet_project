from aiohttp import web
from bankConfig import configs
from bson import ObjectId
import pymongo
from bankview import AppCardsV1
from bankview import AppUsersV1
from bankMid import cors_Mid_v1
from bankMid import auth_Mid_v1
from bankHandlers import auth_handler_v1
from motor.motor_asyncio import AsyncIOMotorClient
import json
import jwt
import motor.motor_asyncio

config = configs['config']
app = web.Application()

if __name__=='__main__':
	app['config'] = config

	APIv1 = web.Application()
	APIv1.router.add_get('/auth', auth_handler_v1)
	APIv1.router.add_view('/ads_users', AppUsersV1)
	APIv1.router.add_view('/ads_cards', AppCardsV1)
	app.add_subapp('/api/rest/v1', APIv1)

	db = AsyncIOMotorClient('mongodb://localhost:27017').Users
	app['db'] = db

	app.middlewares.append(cors_Mid_v1)
	app.middlewares.append(auth_Mid_v1)

	if config.CONFIG_NAME == 'dev':
		web.run_app(app)