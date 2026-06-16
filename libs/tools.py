from functools import wraps

def add_method(cls):
    '''Decorator to add a method to a class'''
    def decorator(func):
        @wraps(func) 
        def wrapper(self, *args, **kwargs): 
            return func(self,*args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        return func # returning func means func can still be used normally
    return decorator

def p_log(f):
    '''Decorator for logging function output'''
    def wrapped(*args, **kwargs):
        t = f(*args, **kwargs)
        print(t)
        return t
    return wrapped

def not_none(*args) -> bool:
    '''Tests all args to not None'''
    return not any(x is None for x in args)


def apply_valid_arg(func, x, default=None):
    '''Applies a function on a valid argument'''
    return func(x) if not_none(x) else default


def str2bool(s:str) -> bool:
    '''Converts a string to boolean'''
    return s.lower() in ("yes", "true", "t", "1")


