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
    'key': 'alpha_two',
    'description': 'A rule with only one alpha check in all',
    'collections': [
        'persons',
        'vehicles',
    ],
    'variables': [
    ],
    'when': {
        'any': [
            {
                'name': 'vehicles>>color',
                'operator': 'equal_to',
                'value': 'black'
            },
            {
                'name': 'persons>>preference',
                'operator': 'equal_to',
                'value': 'BMW'
            },
        ],
        'all': [
            {
                'name': 'persons>>gender',
                'operator': 'equal_to',
                'value': 'F'
            },
            {
                'name': 'vehicles>>company',
                'operator': 'equal_to',
                'value': 'Tesla'
            },

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
                {
                    'name': 'vehicle_model',
                    'value': 'vehicles>>model'
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
# Data: {'persons': {u'gender': u'F', u'_id': ObjectId('5a1bec38814511659779e536'), u'name': u'Amy', u'preference': u'BMW'}, 'vehicles': {u'color': u'black', u'company': u'Tesla', u'_id': ObjectId('5a1d2759a81ea91853bc5411'), u'model': u'S3'}}
# Executing the following triggers:
# Key: award_points, Trigger Type: print
