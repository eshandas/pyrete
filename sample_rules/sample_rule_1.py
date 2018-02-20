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
    'key': 'sample_rule',
    'description': 'A sample rule',
    'collections': [
        'persons',
        'vehicles',
        'pets'
    ],
    'variables': [
        # {
        #     'name': '$email_order_count',
        #     'value': 'orders>>email__get_frequency::$email'
        # }
    ],
    'when': {
        'any': [
            {
                'name': 'persons>>gender',
                'operator': 'equal_to',
                'value': 'F'
            },
            {
                'name': 'vehicles>>wheels',
                'operator': 'greater_than',
                'value': 3
            },
            # {
            #     'name': 'persons>>preference',
            #     'operator': 'equal_to',
            #     'value': '^^vehicles>>company'
            # }
        ],
        'all': [
            {
                'name': 'persons>>preference',
                'operator': 'equal_to',
                'value': '^^vehicles>>company'
            },
            {
                'name': 'persons>>fav_color',
                'operator': 'equal_to',
                'value': '^^vehicles>>color'
            },
        ]},
    'then': [
        # {
        #     'key': 'create_order',
        #     'trigger_type': 'webhook',
        #     'webhook_details': {
        #         'url': 'https://www.google.co.in/',
        #         'method': 'POST'},
        #     'params': [
        #         {
        #             'name': 'email_str',
        #             'value': 'email__as_str'
        #         },
        #         {
        #             'name': 'price',
        #             'value': 'orders.total_price'
        #         },
        #         {
        #             'name': 'count',
        #             'value': 'orders.note_attributes__count'
        #         }
        #     ]
        # },
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
                    'value': 'customers>>orders_count'
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
