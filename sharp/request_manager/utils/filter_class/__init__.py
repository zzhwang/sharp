
def get_redis_queue_cls(cls_name):
    if cls_name == 'bloom':
        from sharp.request_manager.utils.filter_class.bloomfilter import BloomFilter
        return BloomFilter

    elif cls_name == 'memory':
        from sharp.request_manager.utils.filter_class.information_summary_filter.memory_filter import MemoryFilter
        return MemoryFilter

    elif cls_name == 'mysql':
        from sharp.request_manager.utils.filter_class.information_summary_filter.mysql_filter import MySQLFilter
        return MySQLFilter

    elif cls_name == 'redis':
        from sharp.request_manager.utils.filter_class.information_summary_filter.redis_filter import RedisFilter
        return RedisFilter
