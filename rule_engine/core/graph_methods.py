
def get_all_alpha_nodes(nodes):
    """
    Gets all alpha nodes for object node

    """
    alpha_nodes = []
    for node in nodes:
        if node.name == 'alpha_node':
            print node.name
            print node.id
            alpha_nodes.append(node)
            node = get_all_alpha_nodes(node.children)
            # if isinstance(ret_obj, list):
            #     alpha_nodes.extend(ret_obj)
            return node

        elif node.name == 'memory_adapter':
            print node.name
            return node
