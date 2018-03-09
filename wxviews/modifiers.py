'''wxviews default modifiers'''

from wxviews.node import ControlNode

def call(node, key, value):
    '''calls control method'''
    args = value if isinstance(value, list) or isinstance(value, tuple) else [value]
    getattr(node.control, key)(*args)

def set_sizer_args(node: ControlNode, key, value):
    '''Modifier - sets argument for sizer add method'''
    node.sizer_args.append(value)

def set_sizer_kwargs(node: ControlNode, key, value):
    '''Modifier - sets option argument for sizer add method'''
    node.sizer_kwargs[key] = value
