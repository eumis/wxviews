'''wxviews default modifiers'''

def call(node, key, value):
    '''calls control method'''
    args = value if isinstance(value, list) or isinstance(value, tuple) else [value]
    getattr(node.control, key)(*args)
