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
        'persons',
        'vehicles',
    ],
    'variables': [
    ],
    'when': {
        'any': [
        ],
        'all': [
            {
                'name': 'persons>>preference',
                'operator': 'equal_to',
                'value': '^^vehicles>>company'
            }
        ]},
    'then': [
        {
            'key': 'award_points',
            'trigger_type': 'print',
            'webhook_details': {},
            'params': [
                {
                    'name': 'vehicle_model',
                    'value': 'vehicles>>model'
                },
                {
                    'name': 'person_name',
                    'value': 'persons>>name'
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
# ....................................
# For ObjectNode: persons
# Items Processed: 4
# Items Passed: 4

# ....................................
# For ObjectNode: vehicles
# Items Processed: 5
# Items Passed: 5
# ...........................
# Data: {'persons': {u'_id': ObjectId('5a1bec38814511659779e534'), u'name': u'akshata', u'preference': u'Maruti'}, 'vehicles': {u'company': u'Maruti', u'_id': ObjectId('5a0422c6bae3828177788d49'), u'model': u'Omni'}}
# ...........................
# Data: {'persons': {u'_id': ObjectId('5a1bec38814511659779e534'), u'name': u'akshata', u'preference': u'Maruti'}, 'vehicles': {u'company': u'Maruti', u'_id': ObjectId('5a042309bae3828177788d4b'), u'model': u'Swift'}}
# ...........................
# Data: {'persons': {u'_id': ObjectId('5a1bec38814511659779e535'), u'name': u'Eshan', u'preference': u'Tesla'}, 'vehicles': {u'company': u'Tesla', u'_id': ObjectId('5a1d2759a81ea91853bc5411'), u'model': u'S3'}}
# ...........................
# Data: {'persons': {u'_id': ObjectId('5a1bec38814511659779e536'), u'name': u'Amy', u'preference': u'BMW'}, 'vehicles': {u'company': u'BMW', u'_id': ObjectId('5a0422eabae3828177788d4a'), u'model': u'BMW1'}}
