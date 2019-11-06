from redis import StrictRedis
from pickle import dumps, loads
import sys, os
sys.path.append(os.getcwd())
from spider.config import REDIS_HOST, REDIS_PORT, REDIS_PASS, REDIS_KEY_REQ

class RedisQueue():

    def __init__(self):
        self.db = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS)

    def push(self, key, value):
        self.db.rpush(key, dumps(value))

    """
    "Remove and return the first item of the list ``name``"
    """
    def pop(self, key):
        print(self.db.llen(key))
        if self.db.llen(key):
            return loads(self.db.lpop(key))

    """
    "Delete one or more keys specified by ``names``"
    """
    def delete(self, *keys):
        self.db.delete(*keys)

    def get_key_isempty(self, key):
        return self.db.llen(key)

if __name__ == "__main__":
    queue = RedisQueue()
    queue.push(REDIS_KEY_REQ, '5G')
    queue.push('400', 'server')
    queue.delete(REDIS_KEY_REQ, '400')
    # queue.empty(REDIS_KEY_REQ)
    # print(queue.db.llen(REDIS_KEY_REQ))
    # print(queue.pop(REDIS_KEY_REQ))