
# -*- coding: utf-8 -*-

import sys
import locale
import time
import functools
import twitter
import json
import redis
from twitter__login import login
from twitter__util import _getFriendsOrFollowersUsingFunc
from twitter__util import getRedisIdByScreenName
from twitter__util import getRedisIdByUserId
from twitter__util import getUserInfo

SCREEN_NAME = ['NASA','CERN']

# For nice number formatting
locale.setlocale(locale.LC_ALL, '')  

# You may need to setup your OAuth settings in twitter__login.py

t = login()

# Connect using default settings for localhost
r = redis.Redis()  

# Some wrappers around _getFriendsOrFollowersUsingFunc 
# that bind the first two arguments

getFriends = functools.partial(_getFriendsOrFollowersUsingFunc, 
                               t.friends.ids, 'friend_ids', t, r, limit=200)

getFollowers = functools.partial(_getFriendsOrFollowersUsingFunc,
                                 t.followers.ids, 'follower_ids', t, r, limit=200)

screen_names = SCREEN_NAME
friends_ids = []
followers_ids = []
union = []
# get the data
for screen_name in screen_names:
	if screen_name != None:

		print >> sys.stderr, 'Getting friends for %s...' % (screen_name, )
		friends_ids = getFriends(screen_name, limit=200)
		print >> sys.stderr, 'Getting followers for %s...' % (screen_name, )
		followers_ids = getFollowers(screen_name, limit=200)
		# make union of friends and followers
		union = r.sunion([getRedisIdByScreenName(screen_name,'friends_ids'),getRedisIdByScreenName(screen_name, 'follower_ids')])
		# convert from set to list
		union = list(union)
		# we need just 200 of them
		union = union[1:200]

		# get info for all 200; needed for the location
		friends_info = getUserInfo(t, r, user_ids=union, sample=1.0)
		

		print "Now harvesting ", screen_name,"'s friends subgraphs"
		for current_friend in friends_info:
			if current_friend != None:

				print "+",current_friend['screen_name']," From ",
				if current_friend['location'] != None and current_friend['location']!= "" :
					print current_friend['location'].encode('utf-8')
				else:
					print " "
				
				friend_ids = getFriends(current_friend['screen_name'], limit=200)

