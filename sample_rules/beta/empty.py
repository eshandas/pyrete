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
    'key': 'alpha_two_all_one_any',
    'description': 'A rule with only one alpha check in all',
    'collections': [
    ],
    'variables': [
    ],
    'when': {
        'any': [
        ],
        'all': [

        ]},
    'then': [
        {
            'key': 'award_points',
            'trigger_type': 'print',
            'webhook_details': {},
            'params': [
                {
                    'name': 'points',
                    'value': '1000__as_str'
                },
                {
                    'name': 'orders_count',
                    'value': 'persons>>fav_color'
                }
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
# PROCESSING VARIABLES...


# PROCESSING RULES...
# before checking file size
# here

# ....................................
# For ObjectNode: persons
# Items Processed: 4
# Items Passed: 1

# ....................................
# For ObjectNode: vehicles
# Items Processed: 5
# Items Passed: 1
# ...........................
# Data: {'persons': {u'gender': u'F', u'fav_color': u'black', u'_id': ObjectId('5a2784fe713fb58fa40830f3'), u'preference': u'BMW'}, 'vehicles': {u'color': u'black', u'company': u'Tesla', u'_id': ObjectId('5a27857979bb8b8f50d25d5f')}}
# Executing the following triggers:
# Key: award_points, Trigger Type: print
