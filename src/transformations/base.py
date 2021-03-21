# pylint: disable=protected-access,dangerous-default-value
import time
import threading
import sys

from src.ir.visitors import DefaultVisitorUpdate


def timeout_function(log, entity, timeouted):
    log("{}: took too long (timeout)".format(entity))
    sys.stderr.flush() # Python 3 stderr is likely buffered.
    timeouted[0] = True


def visitor_logging_and_timeout_with_args(*args):
    def wrap_visitor_func(visitor_func):
        def wrapped_visitor(self, node):
            if len(args) > 0:
                self.log(*args)
            transformation_name = self.__class__.__name__
            visitor_name = visitor_func.__name__
            entity = transformation_name + "-" + visitor_name
            self.log("{}: Begin".format(entity))

            timeouted = [False]
            start = time.time()
            try:
                timer = threading.Timer(
                    self.timeout, timeout_function,
                    args=[self.log, entity, timeouted])
                timer.start()
                new_node = visitor_func(self, node)
            finally:
                timer.cancel()
            end = time.time()
            if timeouted[0]:
                new_node = node
            self.log("{}: {} elapsed time".format(entity, str(end - start)))
            self.log("{}: End".format(entity))
            return new_node
        return wrapped_visitor
    return wrap_visitor_func


def change_namespace(visit):
    def inner(self, node):
        initial_namespace = self._namespace
        self._namespace += (node.name,)
        new_node = visit(self, node)
        self._namespace = initial_namespace
        return new_node
    return inner


def change_depth(visit):
    def inner(self, node):
        initial_depth = self.depth
        self.depth += 1
        new_node = visit(self, node)
        self.depth = initial_depth
        return new_node
    return inner


class Transformation(DefaultVisitorUpdate):
    CORRECTNESS_PRESERVING = None

    def __init__(self, program, language, logger=None, options={}):
        assert program is not None, 'The given program must not be None'
        self.is_transformed = False
        self.language = language
        self.program = program
        self.types = self.program.get_types()
        self.logger = logger
        self.options = options
        self.timeout = options.get("timeout", 600)
        if self.logger:
            self.logger.log_info()

    def transform(self):
        self.program = self.visit(self.program)

    def result(self):
        return self.program

    def log(self, msg):
        if self.logger is None:
            pass
        else:
            self.logger.log(msg)

    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    def preserve_correctness(cls):
        return cls.CORRECTNESS_PRESERVING

    @visitor_logging_and_timeout_with_args()
    def visit_program(self, node):
        return super().visit_program(node)
