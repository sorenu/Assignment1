import sys
import redis
import networkx as nx
import json
import matplotlib.pyplot as plt
from twitter__util import getRedisIdByScreenName
from twitter__util import getRedisIdByUserId

r = redis.Redis()
graph = nx.Graph()

EGO = sys.argv[1]
EGO_ID = json.loads(r.get(getRedisIdByScreenName(EGO, 'info.json')))['id']
TEMP_UNION_KEY = 'temp$union'

# union EGO's friends and followers
r.sunionstore(TEMP_UNION_KEY, [getRedisIdByScreenName(EGO,'friend_ids'), getRedisIdByScreenName(EGO,'follower_ids')])
friend_follower_ids = list(r.smembers(TEMP_UNION_KEY))

# for each friend/follower :
for friend_follower_id in friend_follower_ids:
	# intersect friend/follower's friends with ego's union
	# NB: the getFriends function used for mining only uses screen_name keys
	try:
		screen_name = json.loads(r.get(getRedisIdByUserId(friend_follower_id, 'info.json')))['screen_name']
	except:
		continue
	intersecting_ids = list(r.sinter(TEMP_UNION_KEY, getRedisIdByScreenName(screen_name, 'friend_ids')))
	# add edge between EGO and the current friend/follower
	graph.add_edge(EGO_ID, friend_follower_id)
	# add edges between each id in the intersection and the id of the current friend/follower
	for intersecting_id in intersecting_ids:
		graph.add_edge(friend_follower_id, intersecting_id)

# cleanup
r.delete(TEMP_UNION_KEY)

# plot the graph
plt.figure(1)
nx.draw_spring(graph,node_size=65, node_color='#7FA8FF', node_shape='o',edge_color='.1',with_labels=False,width=1.3)
plt.show()