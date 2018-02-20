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
        'orders',
        'customers',
        'products',
    ],
    'variables': [
        # {
        #     'name': '$email_order_count',
        #     'value': 'orders>>email__get_frequency::$email'
        # }
    ],
    'when': {
        'any': [
            # {
            #     'name': 'orders>>total_price',
            #     'operator': 'less_than_equal_to',
            #     'value': '56.00'
            # },
            {
                'name': 'orders>>email',
                'operator': 'equal_to',
                'value': 'testan6@mailinator.com'
            },
            # {
            #     'name': 'products>>orders_count',
            #     'operator': 'greater_than',
            #     'value': 0
            # },
            {
                'name': 'customers>>email',
                'operator': 'equal_to',
                'value': '^^orders>>email'
            },
            {
                'name': 'customers>>default_address>>province_code',
                'operator': 'equal_to',
                'value': '^^orders>>customer>>default_address>>province_code'
            },
            {
                'name': 'products>>id',
                'operator': 'equal_to',
                'value': '^^orders>>line_items>>product_id'
            },
        ],
        'all': [
            # {
            #     'name': 'orders>>note_attributes__count',
            #     'operator': 'less_than_equal_to',
            #     'value': 5
            # },
            # {
            #     'name': 'orders>>customers>>default_address>>province_code',
            #     'operator': 'equal_to',
            #     'value': 'NC'
            # },
            # {
            #     'name': 'orders>>total_discounts',
            #     'operator': 'equal_to',
            #     'value': '0.00'
            # },
            # {
            #     'name': 'customers>>email',
            #     'operator': 'equal_to',
            #     'value': 'sonyapal@aol.com'
            # }
            {
                'name': 'customers>>first_name',
                'operator': 'equal_to',
                'value': '^^orders>>customers>>first_name'
            },
            {
                'name': 'customers>>last_name',
                'operator': 'equal_to',
                'value': '^^orders>>customers>>last_name'
            },
        ]},
    'then': [
        {
            'key': 'create_order',
            'trigger_type': 'webhook',
            'webhook_details': {
                'url': 'https://www.google.co.in/',
                'method': 'POST'},
            'params': [
                {
                    'name': 'email_str',
                    'value': 'email__as_str'
                },
                {
                    'name': 'price',
                    'value': 'orders>>total_price'
                },
                {
                    'name': 'count',
                    'value': 'orders>>note_attributes__count'
                }
            ]
        },
        {
            'key': 'award_points',
            'trigger_type': 'loyalty_event',
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
    limit=10)


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
