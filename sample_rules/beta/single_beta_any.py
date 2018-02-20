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
            {
                'name': 'vehicles>>color',
                'operator': 'equal_to',
                'value': '^^persons>>fav_color'
            }
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
# ...........................
# Data: {'persons': {u'fav_color': u'red', u'_id': ObjectId('5a1bec38814511659779e534'), u'name': u'akshata'}, 'vehicles': {u'color': u'red', u'model': u'Omni', u'_id': ObjectId('5a0422c6bae3828177788d49')}}
# ...........................
# Data: {'persons': {u'fav_color': u'red', u'_id': ObjectId('5a1bec38814511659779e534'), u'name': u'akshata'}, 'vehicles': {u'color': u'red', u'model': u'Swift', u'_id': ObjectId('5a042309bae3828177788d4b')}}
# ...........................
# Data: {'persons': {u'fav_color': u'black', u'_id': ObjectId('5a1bec38814511659779e535'), u'name': u'Eshan'}, 'vehicles': {u'color': u'black', u'model': u'BMW1', u'_id': ObjectId('5a0422eabae3828177788d4a')}}
# ...........................
# Data: {'persons': {u'fav_color': u'black', u'_id': ObjectId('5a1bec38814511659779e535'), u'name': u'Eshan'}, 'vehicles': {u'color': u'black', u'model': u'S3', u'_id': ObjectId('5a1d2759a81ea91853bc5411')}}
# ...........................
# Data: {'persons': {u'fav_color': u'black', u'_id': ObjectId('5a1bec38814511659779e536'), u'name': u'Amy'}, 'vehicles': {u'color': u'black', u'model': u'BMW1', u'_id': ObjectId('5a0422eabae3828177788d4a')}}
# ...........................
# Data: {'persons': {u'fav_color': u'black', u'_id': ObjectId('5a1bec38814511659779e536'), u'name': u'Amy'}, 'vehicles': {u'color': u'black', u'model': u'S3', u'_id': ObjectId('5a1d2759a81ea91853bc5411')}}
# ...........................
# Data: {'persons': {u'fav_color': u'black', u'_id': ObjectId('5a1bec38814511659779e537'), u'name': u'Rory'}, 'vehicles': {u'color': u'black', u'model': u'BMW1', u'_id': ObjectId('5a0422eabae3828177788d4a')}}
# ...........................
# Data: {'persons': {u'fav_color': u'black', u'_id': ObjectId('5a1bec38814511659779e537'), u'name': u'Rory'}, 'vehicles': {u'color': u'black', u'model': u'S3', u'_id': ObjectId('5a1d2759a81ea91853bc5411')}}
