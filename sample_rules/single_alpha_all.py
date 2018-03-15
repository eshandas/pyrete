from pyrete.core.nodes import (
    ReteGraph,
)
from pyrete.core.engine import (
    RuleEngine,
)
from pyrete.core.data_layer import (
    DataLayer,
)
from pyrete.core.variable_processor import (
    VariableProcessor,
)

from pyrete.core.graph_methods import get_all_alpha_nodes


rule = {
    'key': 'single_alpha_all',
    'description': 'A rule with only one alpha check in all',
    'collections': [
        'persons'
    ],
    'variables': [
    ],
    'when': {
        'any': [
        ],
        'all': [
            {
                'name': 'persons>>fav_color',
                'operator': 'equal_to',
                'value': 'red'
            }
        ]},
    'then': [
        {
            'key': 'award_points',
            'trigger_type': 'print',
            'webhook_details': {},
            'params': [
                {
                    'name': 'person_name',
                    'value': 'persons>>name'
                },
            ]
        }]}


graph = ReteGraph()
graph.load_rule(rule)


def print_details(node):
    print '..............................'
    print 'Id: %s' % node.id
    print 'Type: %s' % node.get_type()


def traverse_children(nodes):
    for node in nodes:
        node.print_details()
        traverse_children(node.children)


traverse_children(graph.root_node.children)

get_all_alpha_nodes(graph.root_node.children[0].children)

# ---------------------- Fetch data from DB
data = DataLayer().get_data(
    rules=[rule],
    filter={},
    limit=5)


# ---------------------- Rule variables
print '\n\nPROCESSING VARIABLES...'
VariableProcessor().process_variables(
    data=data,
    variable_objs=rule['variables'])


# ---------------------- Initiate rule engine
print '\n\nPROCESSING RULES...'
engine = RuleEngine()
trigger = engine.run_efficiently(
    graphs=[graph],
    data=data,
    key=rule['key'],
    email='test@mail.com')


# ---------------------- Expected Output
# ....................................
# For ObjectNode: persons
# Items Processed: 4
# Items Passed: 1
# ...........................
# Data: {'persons': {u'fav_color': u'red', u'_id': ObjectId('5a1bec38814511659779e534'), u'name': u'akshata'}}
