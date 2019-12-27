import os
import logging
import uuid
from logging import Handler, FileHandler, StreamHandler
from confluent_kafka import Producer

class KafkaLoggingHandler(logging.Handler):

    def __init__(self,host,kafka_topic_name=None):
        logging.Handler.__init__(self)

        self.kafka_topic_name = kafka_topic_name
        if self.kafka_topic_name is None:
            self.kafka_topic_name = 'sharp_logger'

        self.producer = Producer({'bootstrap.servers':'{}'.format(host)})

        self.log_count = 0

    def delivery_report(self, err, msg):
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    def emit(self, record):
        # 忽略kafka的日志，以免导致无限递归。
        if 'kafka' in record.name:
            return
        try:
            # 格式化日志并指定编码为utf-8
            msg = self.format(record)

            # kafka生产者，发送消息到broker。
            self.producer.produce('test', str(msg),callback=self.delivery_report)
            self.log_count += 1

            if self.log_count >= 1000:
                self.producer.poll(10)
                self.producer.flush()

        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    def close(self):
        self.producer.poll(10)
        self.producer.flush()

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
            level='debug',
            fmt='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s',
            file = False,
            filename='{uid}.log'.format(uid=uuid.uuid4()),
            log_dir='log',
            kafaka=False,
            kafaka_host='',
            kafka_topic_name=None
    ):
        # 设置日志格式
        format_str = logging.Formatter(fmt)
        # 是否文件保存
        if file:
            self.logger = logging.getLogger(filename)
            # 设置日志级别
            self.logger.setLevel(self.level_relations.get(level))
            # 屏幕打印
            self._console_log(format_str)
            # 文件打印
            self._file_log(format_str, filename, log_dir)

        elif kafaka:
            self.logger = logging.getLogger()
            self.logger.addHandler(KafkaLoggingHandler)
            # 屏幕打印
            self._console_log(format_str)
            self._kafaka_log(self,  format_str, kafaka_host, kafka_topic_name)

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

    def _kafaka_log(self,  format_str, kafaka_host, kafka_topic_name):
        kafaka_handler = KafkaLoggingHandler(kafaka_host,kafka_topic_name)
        kafaka_handler.setFormatter(format_str)
        self.logger.addHandler(kafaka_handler)