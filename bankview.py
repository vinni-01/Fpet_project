from aiohttp import web
from bson import ObjectId
import hashlib
import json
import jwt

bank_card = {}
users = {}

def convert_objectid(document):
    if isinstance(document, list):
        return [convert_objectid(item) for item in document]
    elif isinstance(document, dict):
        for key, value in document.items():
            if isinstance(value, ObjectId):
                document[key] = str(value)
            elif isinstance(value, (dict, list)):
                document[key] = convert_objectid(value)
    return document

def hash_string_sha256(input_string):
    hash_object = hashlib.sha256()
    hash_object.update(input_string.encode())
    hashed_string = hash_object.hexdigest()
    return hashed_string


class AppCardsV1(web.View):
	async def get(self) :
		card_id = self.request.query.get('id', None)
		db = self.request.config_dict['db']
		card_data = await db.Bank_Cards.find_one({"id": card_id})
		card_data = convert_objectid(card_data)

		if card_data:
			return web.json_response(card_data, status=200)
		else:
			return web.json_response({'message': "Card not found"}, status=404)

	async def post(self):
		try:
			card_data = await self.request.json()
			card_data['number'] = hash_string_sha256(card_data['number'])
			card_data['date'] = hash_string_sha256(card_data['date'])
			db = self.request.config_dict['db']
			result = await db.Bank_Cards.insert_one(card_data)
			card = await db.Bank_Cards.find_one({"_id": result.inserted_id})
			card = convert_objectid(card)

			return web.json_response(card, status=200)
		except Exception as e:
			responce_object = {'status': 'failed', 'reason': str(e)}

			return web.json_response(responce_object, status=500)

	async def put(self):
		try:
			card_id = self.request.query.get('id', None)
			db = self.request.config_dict['db']
			card_data = await self.request.json()
			card_data['number'] = hash_string_sha256(card_data['number'])
			card_data['date'] = hash_string_sha256(card_data['date'])
			await db.Bank_Cards.update_one({"id": card_id}, {"$set": card_data})
			card = await db.Bank_Cards.find_one({"id": card_id})
			card = convert_objectid(card)

			return web.json_response({'message': "Card updated successfully"}, status=200)
		except Exception as e:
			responce_object = {'status': 'failed', 'reason': str(e)}

			return web.json_response(responce_object, status=500)

	async def delete(self):
		card_id = self.request.query.get('id', None)
		# object_id = ObjectId(card_id)
		db = self.request.config_dict['db']
		await db.Bank_Cards.delete_one({"id": card_id})
		return web.json_response({'message': 'Card deleted successfully'}, status=200)


class AppUsersV1(web.View):
	async def get(self):
		user_id = self.request.query.get('id', None)
		# object_id = ObjectId(user_id)
		db = self.request.config_dict['db']
		user_data = await db.Users.find_one({"id": user_id})
		user_data = convert_objectid(user_data)

		if user_data:
			return web.json_response(user_data, status=200)
		else:
			return web.json_response({'message': "User not found"}, status=404)

	async def post(self):
		try:
			user_data = await self.request.json()
			config = self.request.config_dict['config']
			user_data['password'] = hash_string_sha256(user_data['password'])
			db = self.request.config_dict['db']
			result = await db.Users.insert_one(user_data)
			user = await db.Users.find_one({"_id": result.inserted_id})
			user = convert_objectid(user)

			return web.json_response(user, status=200)
		except Exception as e:
			return web.json_response({'message': "Failed", 'reason': str(e)}, status=500)

	async def put(self):
		try:
			db = self.request.config_dict['db']
			user_id = self.request.query.get('id', None)
			user_data = await self.request.json()
			data = await db.Users.find_one({"id": user_id})
			data = convert_objectid(data)
			if (hash_string_sha256(user_data['password']) != data['password'] ):
				return web.json_response({'message': "Wrong password"}, status=500)
			user_data['id'] = user_id
			user_data['password'] = hash_string_sha256(user_data['password'])
			await db.Users.update_one({"id": user_id}, {"$set": user_data})

			return web.json_response({'message': "User updated successfully"}, status=200)
		except Exception as e:
			return web.json_response({'message': "Failed", 'reason': str(e)}, status=500)

	async def delete(self):
		user_id = self.request.query.get('id', None)
		db = self.request.config_dict['db']
		await db.Users.delete_one({"id": user_id})
		return web.json_response({'message': "User deleted successfully"}, status=200)
		