import redis

client = None


class RedisClient:
    __client = None

    @staticmethod
    def get():
        if RedisClient.__client is None:
            RedisClient.__client = redis.Redis('redis', 6379, db=0)
        return RedisClient.__client
