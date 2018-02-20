_screen_width = 120


def _print_upper_line(length):
    _offset = (_screen_width / 2) - (length / 2)
    _ = ' ' * _offset
    _ += '_' * (length + 4)
    print(_ + '\n')


def _print_lower_line(length):
    _offset = (_screen_width / 2) - (length / 2)
    _ = ' ' * _offset
    _ += '_' * (length + 4)
    print(_)


def _print_node(node):
    pass


def _print_children(nodes):
    _
    _gap = ' ' * (_screen_width / 2)
    print(_gap + '|')
    print('_' * (count * 20))


class GraphPrinter(object):
    def print_graph(self, graph):
        self._print_root(graph.root_node)
        self._print_alpha_network(graph.root_node)

    def _print_root(self, root_node):
        length = len(root_node.id)
        _print_upper_line(length)
        _offset = (_screen_width / 2) - (length / 2) - 1
        _ = ' ' * _offset
        _ += '|  %s  |' % root_node.id
        print(_)
        _print_lower_line(length)

    def _print_alpha_network(self, root_node):
        child_count = len(root_node.children)
        _print_edges(child_count)
