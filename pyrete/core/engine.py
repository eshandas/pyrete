"""
This is the main engine.
"""
import datetime

import logging

import os

from pyrete.settings import settings

from .variable_processor import eval_variables


class NodeStack(object):
    """
    Used for parsing the dict based "whens" and "thens" to Rete Graph.
    """
    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def push_all(self, items):
        for item in reversed(items):
            self.push(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)

    def print_stack(self):
        for item in self.items:
            print 'item %s with id %d' % (type(item), item.id)


class RuleEngine(object):
    """
    The Rule Engine which processes all the graphs on the complete dataset.
    """
    def __init__(self):
        self.node_stack = NodeStack()
        self.any_pointer = None
        self.all_pointer = None
        self.curr_pointer = 0

    def clear_engine_meta(self):
        """
        Clears all data from the engine

        """
        self.node_stack = NodeStack()
        self.any_pointer = None
        self.all_pointer = None
        self.curr_pointer = 0

    def run(self, graphs, data):
        """
        For each data:
            Clears the engine
            Initializes the engine and atack
            Checks if datum is valid against the rule
            Executes the trigger if datum is valid

        """
        for graph in graphs:
            items_processed = 0
            for datum in data:
                self.clear_engine_meta()
                # Initialize node stack for the graph
                self.init_node_stack(graph)

                items_processed += 1
                if self.check_rules(graph, datum):
                    # If rules succeed, execute trigger node
                    self.exec_trigger_node(graph, datum)

    def check_file_size(self, path):
        print 'here'
        if os.path.exists(path):
            statinfo = os.stat(path)
            statinfo_mb = statinfo.st_size >> 20
            if statinfo_mb >= 5:
                open(path, 'w').close()

    def _eval_alpha_nodes(self, alpha_nodes, datum, collection_name):
        """
        Returns:

            Reference of the MemoryAdapter of the current ObjectNode if data passes through
            all the AlphaNodes, else returns None
        """
        for node in alpha_nodes:
            if node.name == 'alpha_node':
                if node.literal_checks(datum, collection_name):
                    ret_node = self._eval_alpha_nodes(node.children, datum, collection_name)
                    return ret_node
            elif node.name == 'memory_adapter':
                return node
        return None

    def _process_alpha_network(self, alpha_nodes, data, object_type):
        """
        Generator which loops through each datum
        The graph is first loaded
        Each Data is then checked against each rule in "check_rules" to get valid data
        Each valid data will be triggered through "exec_trigger_node"
        """
        memory_adapter = None
        items_processed = 0
        items_passed = 0
        for datum in data[object_type]:
            ret_obj = self._eval_alpha_nodes(alpha_nodes, datum, object_type)
            if ret_obj is not None:
                # If rules succeed, pass the data on to AlphaMemoryAdapter
                memory_adapter = ret_obj
                memory_adapter.data.append({object_type: datum})
                items_passed += 1
            items_processed += 1
        print '\n....................................'
        print 'For ObjectNode: %s' % object_type
        print 'Items Processed: %d' % items_processed
        print 'Items Passed: %d' % items_passed
        data_info = {
            'object': object_type,
            'items_processed': items_processed,
            'items_passed': items_passed
        }
        return data_info

    def merge_two_dicts(self, x, y):
        """Given two dicts, merge them into a new dict as a shallow copy."""
        z = x.copy()
        z.update(y)
        return z

    def _eval_beta_node(self, left_memory_adapter, right_memory_adapter, graph):
        """
        Processes the BetaNode attached to the Left and Right MemoryAdapters.
        """
        # Get the BetaNode, datum from Left and Right MemoryAdapters and then eval BetaNode
        items_processed = 0
        items_passed = 0
        beta_node = left_memory_adapter.children[0]
        for left_datum in left_memory_adapter.data:
            for right_datum in right_memory_adapter.data:
                items_processed += 1
                # Eval the BetaNode
                if beta_node.eval_node(left_datum, right_datum, graph.variables):
                    # If eval is successful, merge the data
                    items_passed += 1
                    new_datum = self.merge_two_dicts(left_datum, right_datum)
                    if beta_node.children[0].name == 'trigger_node':
                        # If BetaNode has TriggerNode as child, execute it by passing merged data
                        beta_node.children[0].exec_triggers(new_datum)
                    else:
                        # If BetaNode has MemoryAdapter as child, populate its data
                        beta_node.children[0].data.append(new_datum)
        data_info = {
            'items_processed': items_processed,
            'items_passed': items_passed
        }

        return beta_node.children[0], data_info

    def process_beta_network(self, graph):
        """
        Processes the Beta Network by popping each MemoryAdapter from the stack
        """
        # Iterate for each node in stack
        items_processed = 0
        items_passed = 0
        while self.node_stack.size() >= 1:
            # While the stack is not empty,
            left_memory_adapter = self.node_stack.pop()
            right_memory_adapter = self.node_stack.pop()
            # Eval the BetaNode
            return_node, beta_data_info = self._eval_beta_node(
                left_memory_adapter, right_memory_adapter, graph)
            if return_node.name == 'memory_adapter':
                self.node_stack.push(return_node)
            items_processed += beta_data_info['items_processed']
            items_passed += beta_data_info['items_passed']
        return {
            'items_processed': items_processed,
            'items_passed': items_passed
        }

    def run_efficiently(self, graphs, data, key, email):
        """
        Uses a generator to iterate over the data values
        """
        # Check the size of the file, if greater than 5MB, erase the contents
        print 'before checking file size'
        self.check_file_size(settings.LOG_FILE)

        # Log the rule key and time into a file
        logging.basicConfig(filename=settings.LOG_FILE, level=logging.INFO)
        logging.info('--------------------------------------')
        logging.info(key)
        logging.info(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # Process all the graphs
        alpha_data_info = {}
        beta_data_info = {}
        for graph in graphs:
            # Start by evaluating the variables used in the rule first. Exit if it fails
            if not eval_variables(graph.rule):
                break

            # Then process each ObjectNode and then evaluate the Alpha Network
            for object_node in graph.root_node.children:
                if len(object_node.children) == 0:
                    # If AlphaNodes are empty, pass all data to respective MemoryAdapter
                    for memory_adapter in graph.alpha_memory_adapters:
                        if memory_adapter.object_type == object_node.object_type:
                            for datum in data[object_node.object_type]:
                                memory_adapter.data.append({object_node.object_type: datum})
                else:
                    # Process the Alpha Network
                    alpha_data_info = self._process_alpha_network(
                        object_node.children, data, object_node.object_type)

            # Push all the memory adapters into the stack
            self.init_node_stack(graph)

            # Evaluate the Beta Network
            if len(graph.alpha_memory_adapters) == 1:
                # Execute the TriggerNode
                memory_adapter = graph.alpha_memory_adapters[0]
                for datum in memory_adapter.data:
                    memory_adapter.children[0].exec_triggers(datum)
            else:
                beta_data_info = self.process_beta_network(graph)
        summary = {
            'alpha_data_info': alpha_data_info,
            'beta_data_info': beta_data_info
        }
        return summary

    def init_node_stack(self, graph):
        """
        Initializer Node Stack, which will be used to process the Graph
        """
        self.node_stack.push_all(graph.alpha_memory_adapters)

    def check_rules(self, graph, datum, collection_name):
        """
        Executes the rules for each data (datum) and prepares for trigger if the data is valid against all rules

        """
        stack_value = False  # The boolean value of the stack
        stack_size = self.node_stack.size()

        # Iterate for each node in stack
        while self.curr_pointer < stack_size:
            # Calculate stack value for current node
            if self.curr_pointer == 0:
                stack_value = self.node_stack.items[
                    self.curr_pointer].eval_node(datum, graph.variables, collection_name)
            else:
                if self.curr_pointer < self.all_pointer or self.all_pointer is None:
                    stack_value = stack_value or self.node_stack.items[
                        self.curr_pointer].eval_node(datum, graph.variables, collection_name)
                else:
                    stack_value = stack_value and self.node_stack.items[
                        self.curr_pointer].eval_node(datum, graph.variables, collection_name)

            if stack_value and self.curr_pointer < self.all_pointer:
                # If stack value is True for 'any', skip all 'any' nodes
                self.curr_pointer = self.all_pointer
            elif stack_value and self.all_pointer is None:
                # If stack value is True and 'all' is empty, skip all 'any' nodes
                break
            elif stack_value is False and self.all_pointer is not None and self.curr_pointer >= self.all_pointer:
                # If stack value is False for 'all', skip all 'all' nodes
                break
            else:
                # Increment current pointer
                self.curr_pointer += 1

        return stack_value

    def exec_trigger_node(self, graph, datum):
        return graph.trigger_node.exec_triggers(datum)

    # def _eval_alpha_nodes(self, nodes, datum, collection_name, any_flag=False):
    #     for node in nodes:
    #         if node.name == 'alpha_node':
    #             if node.child_operator == 'all':
    #                 if node.literal_checks(datum, collection_name):
    #                     ret_node = self._eval_alpha_nodes(node.children, datum, collection_name, False)
    #                     return ret_node
    #                 else:
    #                     return None
    #             elif node.child_operator == 'any' and not any_flag:
    #                 if node.literal_checks(datum, collection_name):
    #                     ret_node = self._eval_alpha_nodes(node.children, datum, collection_name, True)
    #                     return ret_node
    #                 else:
    #                     ret_node = self._eval_alpha_nodes(node.children, datum, collection_name, False)
    #                     return ret_node
    #         elif node.name == 'memory_adapter':
    #             return node
