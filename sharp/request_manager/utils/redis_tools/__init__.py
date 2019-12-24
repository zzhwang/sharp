
def get_redis_queue_cls(queue_type):

    if queue_type == 'fifo':
        from .fifo_redis_queue import FifoReisQueue
        return FifoReisQueue
    elif queue_type == 'lifo':
        from .lifo_redis_queue import LifoResisQueue
        return LifoResisQueue
    elif queue_type == 'priority':
        from .priority_redis_queue import PriorityRedisQueue
        return PriorityRedisQueue
