# -*- coding: utf-8 -*-

import sys
import functools
import twitter
import redis
import json
from twitter__login import login
from twitter__util import getUserInfo
from twitter__util import _getFriendsOrFollowersUsingFunc
from twitter__util import getRedisIdByScreenName
from twitter__util import getRedisIdByUserId

SCREEN_NAME = sys.argv[1]
MAXINT = sys.maxint

t = login()
r = redis.Redis()

# get info and friends for central user
getUserInfo(t,r,[SCREEN_NAME])
getFriends = functools.partial(_getFriendsOrFollowersUsingFunc, t.friends.ids, 'friend_ids', t, r)
getFollowers = functools.partial(_getFriendsOrFollowersUsingFunc, t.followers.ids, 'follower_ids', t, r)

# get friends and followers of central user
friend_ids = getFriends(SCREEN_NAME)
follower_ids = getFollowers(SCREEN_NAME)

# do union of friends and followers
ids = list(r.sunion(getRedisIdByScreenName(SCREEN_NAME,'friend_ids'), getRedisIdByScreenName(SCREEN_NAME,'follower_ids')))

# get user info for friends and followers
getUserInfo(t, r, user_ids=ids)

# get friends of friends and followers
for user_id in ids:
	screen_name = json.loads(r.get(getRedisIdByUserId(user_id, 'info.json')))['screen_name']
	try:
		getFriends(screen_name)
	except:
		continue





