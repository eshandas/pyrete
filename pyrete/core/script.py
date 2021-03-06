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


rule = {
    'key': 'some_rule',
    'description': 'Some awesome description',
    'collections': [
        'orders'
    ],
    'variables': [
        {
            'name': '$email',
            'value': 'webhook>>email'
        },
        {
            'name': '$email_order_count',
            'value': 'orders>>email__get_frequency::$email'
        },
        {
            'name': '$first_order_date',
            'value': 'orders>>created_at__get_by_index::email=$email||0'
        },
        {
            'name': '$second_order_date',
            'value': 'orders>>created_at__get_by_index::email=$email||1'
        },
        {
            'name': '$days_difference',
            'value': '__days_diff::$second_order_date||$first_order_date'
        },
        {
            'name': '$total_price',
            'value': 'webhook>>total_price'
        },
        {
            'name': '$taxes',
            'value': 'webhook>>taxes'
        },
        {
            'name': '$grand_total',
            'value': '__add::$total_price||$taxes'
        }
    ],
    'when': {
        'any': [
        ],
        'all': [
            {
                'name': '$email_order_count',
                'operator': 'equal_to',
                'value': 2
            },
            {
                'name': '$days_difference',
                'operator': 'less_than_equal_to',
                'value': 15
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
                    'value': 'total_price'
                },
                {
                    'name': 'count',
                    'value': 'note_attributes__count'
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
                }
            ]
        }]}


graph = ReteGraph()
graph.load_rule(rule)


# ---------------------- Fetch data from DB
data = DataLayer().get_data(
    rules=[rule],
    filter={},
    limit=10)

data['webhook'] = {
    '_id': 'Webhook_data',
    'email': 'testar7@mailinator.com',
    'total_price': '57.00',
    'taxes': '12.50',
    'note_attributes': [1, 2, 3]}


# ---------------------- Rule variables
print('\n\nPROCESSING VARIABLES...')
VariableProcessor().eval_variables(
    data=data,
    variable_objs=rule['variables'])


# ---------------------- Initiate rule engine
print('\n\nPROCESSING RULES...')
engine = RuleEngine()
trigger = engine.run_efficiently(
    graphs=[graph],
    data=[webhook_data])
