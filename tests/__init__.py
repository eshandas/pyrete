def print_details(node):
    print('..............................')
    print('Id: %s' % node.id)
    print('Type: %s' % node.get_type())


def traverse_children(nodes):
    for node in nodes:
        node.print_details()
        traverse_children(node.children)


def hello():
    print('hello')


__all__ = ['print_details', 'traverse_children', 'hello']
