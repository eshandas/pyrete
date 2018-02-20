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
    'key': 'first_order',
    'description': 'As a user, I would like to be credited with 1000 points on performing the First Purchase',
    'collections': [
        'orders',
        'webhook',
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
    ],
    'when': {
        'any': [],
        'all': [
            {
                'name': '$email_order_count',
                'operator': 'equal_to',
                'value': 1
            },
            {
                'name': 'webhook>>email',
                'operator': 'equal_to',
                'value': '^^orders>>email'
            },
        ]},
    'then': [
        {
            'key': 'create_order',
            'trigger_type': 'webhook',
            'webhook_details': {
                'url': 'https://requestb.in/18xz2ux1',
                'method': 'POST'},
            'params': [
                {
                    'name': 'customer_email',
                    'value': 'webhook>>email'
                },
                {
                    'name': 'event_key',
                    'value': 'first_purchase__as_str'
                }
            ],
        },
        # {
        #     'key': 'award_points',
        #     'trigger_type': 'method',
        #     'method': 'events.tasks.loyalty_event',
        #     'params': [
        #         {
        #             'name': 'customer_email',
        #             'value': 'webhook>>email'
        #         },
        #         {
        #             'name': 'event_key',
        #             'value': 'first_purchase__as_str'
        #         }
        #     ]
        # }
        ]}


graph = ReteGraph()
graph.load_rule(rule)


# ---------------------- Fetch data from DB
data = DataLayer().get_data(
    rules=[rule],
    filter={},
    limit=10)

data['webhook'] = [{
    '_id': 'Webhook_data',
    'email': 'test28@mailinator.com',
    'total_price': '57.00',
    'note_attributes': [1, 2, 3]}]


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
