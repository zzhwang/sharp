import os
import logging
import uuid
from logging import Handler, FileHandler, StreamHandler

class PathFileHandler(FileHandler):
    def __init__(self, path, filename, mode='a', encoding=None, delay=False):

        filename = os.fspath(filename)
        if not os.path.exists(path):
            os.mkdir(path)
        self.baseFilename = os.path.join(path, filename)
        self.mode = mode
        self.encoding = encoding
        self.delay = delay
        if delay:
            Handler.__init__(self)
            self.stream = None
        else:
            StreamHandler.__init__(self, self._open())

class Loggers(object):
    # 日志级别关系映射
    level_relations = {
        'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING,
        'error': logging.ERROR, 'critical': logging.CRITICAL
    }

    def __init__(
            self,
            level='info',
            fmt='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s',
            storage = False,
            filename='{uid}.log'.format(uid=uuid.uuid4()),
            log_dir='log'
    ):
        # 设置日志格式
        format_str = logging.Formatter(fmt)
        # 是否文件保存
        if storage:
            self.logger = logging.getLogger(filename)
            # 设置日志级别
            self.logger.setLevel(self.level_relations.get(level))
            # 屏幕打印
            self._console_log(format_str)
            # 文件打印
            self._file_log(format_str, filename, log_dir)
        else:
            self.logger = logging.getLogger()
            # 设置日志级别
            self.logger.setLevel(self.level_relations.get(level))
            self._console_log(format_str)

    def _console_log(self, format_str):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(format_str)
        self.logger.addHandler(stream_handler)

    def _file_log(self,  format_str, filename, log_dir):
        abspath = os.getcwd()
        directory = os.path.join(abspath, log_dir)
        file_handler = PathFileHandler(path=directory, filename=filename, mode='a')
        file_handler.setFormatter(format_str)
        self.logger.addHandler(file_handler)

