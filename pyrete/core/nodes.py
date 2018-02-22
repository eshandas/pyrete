# import the logging library
import logging

import importlib

from pyrete.settings import settings

from . import (
    compare_values,
    get_attr_name,
    DocumentFunctions,
    ConversionFunctions,
    get_object_name,
    get_dict_value,
    get_value,
    ParserLiterals,
)

import requests

from pyrete.core.constants import (
    TriggerType,
)


class Node(object):
    """
    Basic node object
    """
    def __init__(self, id):
        self.id = id
        self.children = []
        self.name = 'basic_node'

    def has_children(self):
        if len(self.children) > 0:
            return True
        else:
            return False

    def get_type(self):
        return str(type(self))

    def get_parents(self):
        pass

    def get_children(self):
        pass

    def get_leaf_node(self):
        pass

    def print_details(self):
        print '..................'
        print 'Id: %s' % self.id
        print 'Type: %s' % str(type(self))

    def get_name(self):
        return self.name


class EvaluableNode(object):
    def _eval_list(self, lst, operator):
        """
        Returns true if the value, compared using the operator is valid against any of the values in the list(lst)
        """
        if operator == 'equal_to':
            return any(value == self.condition['value'] for value in lst)
        if operator == 'not_equal_to':
            return any(value != self.condition['value'] for value in lst)
        if operator == 'greater_than':
            return any(value > self.condition['value'] for value in lst)
        if operator == 'less_than':
            return any(value < self.condition['value'] for value in lst)
        if operator == 'greater_than_equal_to':
            return any(value >= self.condition['value'] for value in lst)
        if operator == 'less_than_equal_to':
            return any(value <= self.condition['value'] for value in lst)

    def literal_checks(self, datum, collection_name):
        """
        Performs Aggregation methods on the given data
        Returns true if the value, compared using the operator against the data is valid
        """
        # If object type comparison:
        if str(self.condition['value']).startswith(ParserLiterals.OBJECT_VALUE_IDENTIFIER):
            return True
        # If condition is not a variable, evaluate from the data
        collection, key, fn_name, fn_type = get_attr_name(self.condition['name'])
        if fn_type == DocumentFunctions.TYPE:
            value = DocumentFunctions.aggregate(
                fn_name=fn_name,
                value_list=get_dict_value(datum, key, collection_name, collection))
        elif fn_type == ConversionFunctions.TYPE:
            value = ConversionFunctions.eval_conversion(
                fn_name=fn_name,
                value=get_dict_value(datum, key, collection_name, collection))
        else:
            value = get_dict_value(datum, key, collection_name, collection)

        if isinstance(value, list):
            return self._eval_list(value, self.condition['operator'])

        if self.condition['operator'] == 'equal_to':
            return value == self.condition['value']
        if self.condition['operator'] == 'not_equal_to':
            return value != self.condition['value']
        if self.condition['operator'] == 'greater_than':
            return value > self.condition['value']
        if self.condition['operator'] == 'less_than':
            return value < self.condition['value']
        if self.condition['operator'] == 'greater_than_equal_to':
            return value >= self.condition['value']
        if self.condition['operator'] == 'less_than_equal_to':
            return value <= self.condition['value']

    def _eval_value(self, datum, value_str, variables, collection_name):
        if ParserLiterals.VARIABLE_IDENTIFIER in value_str:
            # Check if condition is a variable
            # Find the variable from variables list
            var = [var for var in variables if var['name'] == value_str]
            # If found, get the variable value
            value = var[0] if len(var) == 1 else None
            value = value['value']
        else:
            # If condition is not a variable, evaluate from the data
            collection, key, fn_name, fn_type = get_attr_name(value_str)
            if fn_type == DocumentFunctions.TYPE:
                value = DocumentFunctions.aggregate(
                    fn_name=fn_name,
                    value_list=get_dict_value(datum, key, collection_name, collection))
            elif fn_type == ConversionFunctions.TYPE:
                value = ConversionFunctions.eval_conversion(
                    fn_name=fn_name,
                    value=get_dict_value(datum, key, collection_name, collection))
            else:
                value = get_dict_value(datum, key, collection_name, collection)
        return value


class ReteGraph(object):
    """
    The actual graph data structure which contains all the nodes.
    """
    def __init__(self):
        self.root_node = None

    def load_rule(self, rule):
        """
        Initializes the root node. Creates the Alpha and Beta Network. Attaches TriggerNodes
        """
        self.rule = rule
        self.variables = rule['variables']

        # Create Root node
        # Creating RootNode instantiates all ObjectNodes and AlphaNodes and thus
        # prepares the Alpha Network
        self.root_node = RootNode(rule)

        # Extract list of all MemoryAdapters present in the Alpha Network
        self.alpha_memory_adapters = []
        self.beta_conditions = []
        for object_node in self.root_node.children:
            self.alpha_memory_adapters.append(
                object_node.memory_adapter)
            self.beta_conditions.extend(object_node.beta_conditions)

        # Create the Beta Network
        self._create_beta_network(rule, self.alpha_memory_adapters, self.beta_conditions)

    def get_beta_nodes(self):
        def populate(nodes):
            beta_nodes = []
            for node in nodes:
                for node_child in node.children:
                    if node_child.name == 'beta_node':
                        beta_nodes.append(node_child)
                        populate(node_child.children)
            return beta_nodes

        return populate(self.alpha_memory_adapters)

    def _create_beta_network(self, rule, memory_adapters, conditions):
        """
        Creates the Beta Network from the MemoryAdapters from the Alpha Network

        If there is only one MemoryAdapter in the Alpha Network, a TriggerNode is
        directly attached to it. If there are more, new sets of MemoryAdapter and
        BetaNode are created.
        """
        memory_adapters_count = len(memory_adapters)
        if memory_adapters_count == 1:
            # If only one MemoryAdapter, directly attach a TriggerNode
            memory_adapters[0].children.append(
                TriggerNode(
                    id='%s_t_1' % memory_adapters[0].id,
                    thens=rule['then']))

        else:
            # For multiple MemoryAdapters
            for idx in range(memory_adapters_count):
                if idx == 0:
                    # Always create a BetaNode for 1st and 2nd MemoryAdapters
                    beta_node = self._create_beta_node(
                        idx=(idx + 1),
                        left_memory_adapter=memory_adapters[idx],
                        right_memory_adapter=memory_adapters[idx + 1])
                    if memory_adapters_count == 2:
                        # Attach TriggerNode if there are only two MemoryAdapters
                        beta_node.children.append(
                            TriggerNode(
                                id='%s_t_1' % memory_adapters[idx].id,
                                thens=rule['then']))
                        break
                    else:
                        # Else create a MemoryAdapter and make it a child of the new BetaNode
                        _memory_adapter = MemoryAdapter(
                            id='bn_ma_%d' % idx,
                            object_type='%s__%s' % (beta_node.left_object_type, beta_node.right_object_type))
                        beta_node.children.append(_memory_adapter)

                elif idx == (memory_adapters_count - 2):
                    # If current iteration is for the last but one adapter, create the final
                    # BetaNode and attach a TriggerNode as child.
                    beta_node = self._create_beta_node(
                        idx=(idx + 1),
                        left_memory_adapter=_memory_adapter,
                        right_memory_adapter=memory_adapters[idx + 1])
                    beta_node.children.append(
                        TriggerNode(
                            id='%s_t_1' % memory_adapters[idx].id,
                            thens=rule['then']))
                    break

                else:
                    # Apart from the first and last MemoryAdapter, create a child BetaNode and
                    # attach a new MemoryAdapter to it
                    beta_node = self._create_beta_node(
                        idx=(idx + 1),
                        left_memory_adapter=_memory_adapter,
                        right_memory_adapter=memory_adapters[idx + 1])
                    _memory_adapter = MemoryAdapter(
                        id='bn_ma_%d' % idx,
                        object_type='%s__%s' % (beta_node.left_object_type, beta_node.right_object_type))
                    beta_node.children.append(_memory_adapter)

    def _create_beta_node(self, idx, left_memory_adapter, right_memory_adapter):
        """
        Creates a BetaNode and attaches it to the Left and Right MemoryAdapters
        """
        beta_node_conditions = []
        for condition in self.beta_conditions:
            name_obj_type = get_attr_name(condition['name'])[0]
            value_obj_type = get_attr_name(condition['value'].replace(
                ParserLiterals.OBJECT_VALUE_IDENTIFIER, ''))[0]

            _left_object_check = (
                name_obj_type in left_memory_adapter.object_type or value_obj_type in left_memory_adapter.object_type)
            _right_object_check = (
                name_obj_type in right_memory_adapter.object_type or value_obj_type in right_memory_adapter.object_type)
            if _left_object_check and _right_object_check:
                beta_node_conditions.append(condition)

        beta_node = BetaNode(
            id='bn_b_%d' % idx,
            left_object_type=left_memory_adapter.object_type,
            right_object_type=right_memory_adapter.object_type,
            conditions=beta_node_conditions)
        left_memory_adapter.children.append(beta_node)
        right_memory_adapter.children.append(beta_node)
        return beta_node


class RootNode(Node):
    """
    The root node of a graph. There can be only one root node per graph.
    The rule dict needs to be provided to instantiate the RootNode
    """
    def __init__(self, rule):
        super(RootNode, self).__init__(id=rule['key'])
        # Instantiate ObjectNodes
        idx = 1
        for collection in rule['collections']:
            self.children.append(
                ObjectNode(
                    id='o_%d' % idx,
                    rule=rule,
                    object_type=collection))
            idx += 1

    def __str__(self):
        return self.key


class ObjectNode(Node):
    """
    The ObjectNode is responsible for handling its AlphaNodes and providing the correct data
    """
    def __init__(self, id, rule, object_type):
        super(ObjectNode, self).__init__(id=id)
        self.object_type = object_type

        # Instantiate Memory Adapter for this data-type
        self.memory_adapter = MemoryAdapter(
            id='%s_ma_%d' % (self.id, 1),
            object_type=object_type)

        # store the beta conditions somewhere
        self.beta_conditions = []

        # Instantiate AlphaNodes
        self.children = []
        self.name = 'object_node'
        # Add "all" conditions node chain
        idx = 1
        _last_child_node = self
        for condition in rule['when']['all']:
            if get_object_name(condition['name']) == object_type:
                if str(condition['value']).startswith(ParserLiterals.OBJECT_VALUE_IDENTIFIER):
                    self.beta_conditions.append(condition)
                else:
                    if idx == 1:
                        # Make the first condition the child
                        _last_child_node.children.append(
                            AlphaNode(
                                id='%s_a_%d' % (self.id, idx),
                                condition=condition,
                                child_operator='all',
                                object_type=object_type))
                        _last_child_node = _last_child_node.children[0]
                    else:
                        _last_child_node.children.append(
                            AlphaNode(
                                id='%s_a_%d' % (self.id, idx),
                                condition=condition,
                                child_operator='all',
                                object_type=object_type))
                        _last_child_node = _last_child_node.children[0]
                    idx += 1

        # Add "any" conditions node chain
        _any_counter = 0
        for condition in rule['when']['any']:
            if get_object_name(condition['name']) == object_type:
                _any_counter += 1
                if str(condition['value']).startswith(ParserLiterals.OBJECT_VALUE_IDENTIFIER):
                    self.beta_conditions.append(condition)
                else:
                    node = AlphaNode(
                        id='%s_a_%d' % (self.id, idx),
                        condition=condition,
                        child_operator='any',
                        object_type=object_type)
                    idx += 1
                    # Connect all "any" alpha nodes to MemoryAdapter
                    # TODO: Make sure Python doesn't replicate the MemoryAdapter. It needs to be same
                    node.children.append(self.memory_adapter)
                    _last_child_node.children.append(node)
        if _any_counter == 0:
            _last_child_node.children.append(self.memory_adapter)

    def print_details(self):
        super(ObjectNode, self).print_details()
        print 'Object Type: %s' % self.object_type

    def __str__(self):
        return self.id


class AlphaNode(Node, EvaluableNode):
    """
    Alpha node is always a child of Root node. It holds one "when" condition. There will be
    one alpha node per condition in the "when" section.
    """
    def __init__(self, id, condition, child_operator, object_type=None):
        super(AlphaNode, self).__init__(id=id)
        self.condition = condition
        self.child_operator = child_operator
        self.name = 'alpha_node'
        self.object_type = object_type

    def instantiate_child_node(self):
        """
        Child can be either another alpha node or a memory adapter
        """
        pass

    def eval_node(self, datum, variables, collection_name):
        """
        Performs Aggregation methods on the given data
        Returns true if the value, compared using the operator against the data is valid
        """
        value = self._eval_value(datum, self.condition['name'], variables, collection_name)
        return compare_values(value, self.condition['value'], self.condition['operator'])

    def print_details(self):
        super(AlphaNode, self).print_details()
        print 'Condition Name: %s' % self.condition['name']

    def __str__(self):
        return '%s - %s' % (self.id, self.condition['name'])


class MemoryAdapter(Node):
    """
    Memory adapter simply holds a list of one type of objects
    """
    def __init__(self, id, object_type):
        super(MemoryAdapter, self).__init__(id=id)
        self.data = []
        self.name = 'memory_adapter'
        self.object_type = object_type


class BetaNode(Node):
    """
    Beta node will either have a memory adapter or a trigger node as its child.
    It will evaluate the inter object relationships (if any), pack all the different objects into
    one entity and forward it further.
    """
    def __init__(self, id, left_object_type=None, right_object_type=None, conditions=[]):
        super(BetaNode, self).__init__(id=id)
        self.name = 'beta_node'
        self.left_object_type = left_object_type
        self.right_object_type = right_object_type
        self.conditions = conditions
        self.gamma_nodes = []
        self._create_gamma_network()

    def _create_gamma_network(self):
        for idx, condition in enumerate(self.conditions):
            self.gamma_nodes.append(
                GammaNode(
                    id='%s_g_%d' % (self.id, idx + 1),
                    condition=condition))

    def eval_node(self, left_datum, right_datum, variables):
        for gamma_node in self.gamma_nodes:
            # NOTE: Currenty all the nodes are being Anded
            # NOTE: Right and Left datum have been interchanged. Investigate later
            evaluation = gamma_node.eval_node(right_datum, left_datum, variables)
            if evaluation is False:
                return False
        return True


class GammaNode(Node, EvaluableNode):
    """
    GammaNodes live inside BetaNodes. These are used for literal checking the conditions.
    """
    def __init__(self, id, condition=None):
        super(GammaNode, self).__init__(id=id)
        self.name = 'gamma_node'
        self.condition = condition

    def eval_node(self, left_datum, right_datum, variables):
        """
        Evaluates the GammaNode's condtion['name'] and contion['value'] and then compares the values
        """
        _condition_name = self.condition['name']
        _condition_val = self.condition['value'].replace(ParserLiterals.OBJECT_VALUE_IDENTIFIER, '')

        _condition_name_coll = _condition_name.split('>>')[0]
        _condition_val_coll = _condition_val.split('>>')[0]

        # Evaluating condition['name']. Need to check both left and right datum
        if _condition_name_coll in left_datum.keys():
            # NOTE: Appending the collection name again as the Gamma data has {'collection': {}} structure
            _temp_condition_name = '%s%s%s' % (_condition_name_coll, ParserLiterals.COLLECTION_LITERAL, _condition_name)
            left_value = self._eval_value(left_datum, _temp_condition_name, variables, _condition_name_coll)
        elif _condition_name_coll in right_datum.keys():
            # NOTE: Appending the collection name again as the Gamma data has {'collection': {}} structure
            _temp_condition_name = '%s%s%s' % (_condition_name_coll, ParserLiterals.COLLECTION_LITERAL, _condition_name)
            left_value = self._eval_value(right_datum, _temp_condition_name, variables, _condition_name_coll)

        # Evaluating condition['value']. Need to check both left and right datum
        if _condition_val_coll in left_datum.keys():
            # NOTE: Appending the collection name again as the Gamma data has {'collection': {}} structure
            _temp_condition_val = '%s%s%s' % (_condition_val_coll, ParserLiterals.COLLECTION_LITERAL, _condition_val)
            right_value = self._eval_value(left_datum, _temp_condition_val, variables, _condition_val_coll)
        elif _condition_val_coll in right_datum.keys():
            # NOTE: Appending the collection name again as the Gamma data has {'collection': {}} structure
            _temp_condition_val = '%s%s%s' % (_condition_val_coll, ParserLiterals.COLLECTION_LITERAL, _condition_val)
            right_value = self._eval_value(right_datum, _temp_condition_val, variables, _condition_val_coll)

        return compare_values(left_value, right_value, self.condition['operator'])


class TriggerNode(Node):
    """
    The end-point of the Rete Graph.
    It is a child of one Beta node.
    Each trigger is executed against the data
    """
    def __init__(self, id, thens):
        super(TriggerNode, self).__init__(id=id)
        self.thens = thens
        self.name = 'trigger_node'

    def eval(self, datum, param_key):
        """
        Performs Aggregation methods on the given data
        Returns true if the value, compared using the operator against the data is valid
        """
        collection_name, key, fn_name, fn_type = get_attr_name(param_key)
        if collection_name:
            # If collection_name exists, add it again to the key chain for get_value()
            # to work perfectly
            key = collection_name + ParserLiterals.COLLECTION_LITERAL + key

        if fn_type == DocumentFunctions.TYPE:
            value = DocumentFunctions.aggregate(
                fn_name=fn_name,
                value_list=get_value(datum, key))
        elif fn_type == ConversionFunctions.TYPE:
            value = ConversionFunctions.eval_conversion(
                fn_name=fn_name,
                value=key)
        else:
            value = get_value(datum, key)
        return value

    def _webhook_dict(self, params, datum):
        """
        Prepares the params in the "then" part to be used by the trigger.

        For example, changes:
        'params': [
            {
                'name': 'points',
                'value': '1000__as_str'
            },
            {
                'name': 'vehicle_model',
                'value': 'vehicles>>model'
            }]

        To:
        'params':
            {
                'points': '1000',
                'vehicle_model': 'Tesla'
            }
        """
        rule_dict = {}
        for i in params:
            value = self.eval(datum, i['value'])
            rule_dict.update({i['name']: value})
        return rule_dict

    def _trigger_rule(self, then, datum):
        # Prepare the parameters by evaluating them
        param_dict = self._webhook_dict(then['params'], datum)

        if then['trigger_type'] == TriggerType.WEBHOOK:
            url = then['webhook_details']['url']
            method = then['webhook_details']['method']
            try:
                headers = then['webhook_details']['headers']
            except KeyError:
                headers = {}

            if method == 'GET':
                r = requests.get(url, headers=headers)
            elif method == 'POST':
                r = requests.post(url, data=param_dict, headers=headers)
            elif method == 'PUT':
                r = requests.put(url, data=param_dict, headers=headers)
            elif method == 'DELETE':
                r = requests.delete(url, headers=headers)

            print(r.url)

        elif then['trigger_type'] == TriggerType.METHOD:
            module_path = then['method'].split('.')
            method = module_path[-1]
            module = '.'.join(module_path[0:len(module_path) - 1])
            module = importlib.import_module(module)
            method = module.__dict__[method]
            method(**param_dict)

        elif then['trigger_type'] == TriggerType.PRINT:
            logging.basicConfig(filename=settings.LOG_FILE, level=logging.INFO)
            logging.info('--------------------------------------')
            logging.info(param_dict)

    def exec_triggers(self, data):

        """
        Execute all the triggers
        """
        print '...........................'
        # print 'Data: %s' % data[data.keys()[0]]['_id']
        print 'Data: %s' % data
        for then in self.thens:
            self._trigger_rule(then, data)
