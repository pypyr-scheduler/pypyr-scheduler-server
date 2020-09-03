import threading
import logging
import re


class PipelineLoggingContext:
    def __init__(self, logger, loglevel=None, log_format=None, log_filename="", sensitive_keys=[]):
        self.logger = logger
        self.loglevel = loglevel
        self.lock = threading.Lock()

        self.handler = logging.FileHandler(log_filename)
        self.handler.setFormatter(SensitiveValueFormatter(fmt=log_format, sensitive_keys=sensitive_keys))

    def __enter__(self):
        self.lock.acquire()
        if self.loglevel is not None:
            self._old_level = self.logger.level
            self.logger.setLevel(self.loglevel)
        if self.handler:
            self.logger.addHandler(self.handler)

    def __exit__(self, et, ev, tb):
        self.lock.release()
        if self.loglevel is not None:
            self.logger.setLevel(self._old_level)
        if self.handler:
            self.logger.removeHandler(self.handler)


class SensitiveValueFormatter(logging.Formatter):
    """
    Logging formatter which censors sensitive information.

    The fitler checks if the log message containssensitive key-value-pairs.
    These pairs have to occure in the message in the form "'<key>': '<value>'". 
    This does not have to be a string representation of a dictionary, but will be in most cases.

    Then the value will be replaced with the string '*****' and the log message will be emitted
    by its handler.
    
    """    
    def __init__(self, fmt=None, datefmt=None, style='%', sensitive_keys=None):
        super().__init__(fmt, datefmt, style)
        self.sensitive_keys = sensitive_keys if sensitive_keys else []
        self.regex_list = []
        for key in self.sensitive_keys:            
            self.regex_list.append( re.compile(r"\'(?P<key>" + key + r")\':\s*\'.*?\'") )

    def format(self, record):
        formatted_record = super().format(record)
        for r in self.regex_list:
            formatted_record = r.sub("'\g<key>': '*****'", formatted_record)
        return formatted_record
