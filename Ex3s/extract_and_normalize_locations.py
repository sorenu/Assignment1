import sys
import redis
import json
from twitter__util import getRedisIdByScreenName
from twitter__util import getRedisIdByUserId

EGO = sys.argv[1]

r = redis.Redis()
normalized_locations = []

friend_ids = list(r.smembers(getRedisIdByScreenName(EGO, 'friend_ids')))
ego_id = json.loads(r.get(getRedisIdByScreenName(EGO, 'info.json')))['id']

ids = [ego_id] + friend_ids

for user_id in ids:
	redis_id = getRedisIdByUserId(str(user_id), 'info.json')
	location_json = r.get(redis_id)
	if 	location_json:
		location = json.loads(location_json)['location']
		if location:
			normalized_location = location.lower().encode("utf-8")
			normalized_locations.append(normalized_location)
	
unique_locations = set(normalized_locations)

for ul in unique_locations:
	print ul