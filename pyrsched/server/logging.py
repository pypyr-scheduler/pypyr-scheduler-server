import threading
import logging
import re


class PipelineLoggingContext:
    def __init__(self, logger, loglevel=None, handler=None, filter_list=None):
        self.logger = logger
        self.handler = handler
        self.filter_list = filter_list
        self.loglevel = loglevel
        self.lock = threading.Lock()

    def __enter__(self):
        self.lock.acquire()
        if self.loglevel is not None:
            self._old_level = self.logger.level
            self.logger.setLevel(self.loglevel)
        if self.handler:
            for f in self.filter_list:
                self.handler.addFilter(f)
            self.logger.addHandler(self.handler)

    def __exit__(self, et, ev, tb):
        self.lock.release()
        if self.loglevel is not None:
            self.logger.setLevel(self._old_level)
        if self.handler:
            for f in self.filter_list:
                self.handler.removeFilter(f)
            self.logger.removeHandler(self.handler)


class SensitiveValueFilter(logging.Filter):
    """
    Logging filter which censors sensitive information.

    The fitler checks if the log message containssensitive key-value-pairs.
    These pairs have to occure in the message in the form "'<key>': '<value>'". 
    This does not have to be a string representation of a dictionary, but will be in most cases.

    Then the value will be replaced with the string '*****' and the log message will be emitted
    by its handler.
    
    """
    def __init__(self, name='', sensitive_keys=None):
        super().__init__(name)
        self.sensitive_keys = sensitive_keys if sensitive_keys else []
        self.regex_list = []
        for key in self.sensitive_keys:            
            self.regex_list.append( re.compile(r"\'(?P<key>" + key + r")\':\s*\'.*?\'") )

    def filter(self, record):
        for r in self.regex_list:
           record.msg = r.sub("'\g<key>': '*****'", record.msg)
        return True
