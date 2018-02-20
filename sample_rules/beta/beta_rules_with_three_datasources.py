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
    'key': 'sample_rule',
    'description': 'A sample rule',
    'collections': [
        'vehicles',
        'persons',
        'companies',
    ],
    'variables': [
        # {
        #     'name': '$male_count',
        #     'value': 'persons>>gender__get_frequency::M'
        # },
        # {
        #     'name': '$persons_price',
        #     'value': 'persons>>total_price'
        # },
        # {
        #     'name': '$persons_sample',
        #     'value': '__add::$persons_price||10'
        # }
    ],
    'when': {
        'any': [
        ],
        'all': [
            # {
            #     'name': '$male_count',
            #     'operator': 'equal_to',
            #     'value': 1
            # },
            {
                'name': 'persons>>fav_color',
                'operator': 'equal_to',
                'value': 'red'
            },
            {
                'name': 'vehicles>>wheels',
                'operator': 'equal_to',
                'value': 4
            },
            {
                'name': 'persons>>fav_color',
                'operator': 'equal_to',
                'value': '^^vehicles>>color'
            },
            {
                'name': 'persons>>budget',
                'operator': 'greater_than_equal_to',
                'value': '^^vehicles>>price'
            },
            {
                'name': 'companies>>name',
                'operator': 'equal_to',
                'value': '^^vehicles>>company'
            },
        ]},
    'then': [
        {
            'key': 'award_points',
            'trigger_type': 'print',
            'params': [
                {
                    'name': 'vehicle_model',
                    'value': 'vehicles>>model'
                },
                {
                    'name': 'person_name',
                    'value': 'persons>>name'
                },
                {
                    'name': 'company_name',
                    'value': 'companies>>name'
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
# data['webhook'] = [{
#     "_id": "1234",
#     "gender": "F",
#     "name": "akshata",
#     "preference": "Maruti",
#     "fav_color": "red"}]


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
# For ObjectNode: vehicles
# Items Processed: 5
# Items Passed: 3

# ....................................
# For ObjectNode: persons
# Items Processed: 4
# Items Passed: 1

# ....................................
# For ObjectNode: companies
# Items Processed: 3
# Items Passed: 3
# ...........................
# Data: {'persons': {u'fav_color': u'red', u'_id': ObjectId('5a1bec38814511659779e534'), u'name': u'akshata', u'budget': 50000000.0}, 'vehicles': {u'model': u'Omni', u'color': u'red', u'company': u'Maruti', u'wheels': 4.0, u'_id': ObjectId('5a0422c6bae3828177788d49'), u'price': 500000.0}, 'companies': {u'_id': ObjectId('5a1d26db4e6bc7ebf228ab9a'), u'name': u'Maruti'}}
# ...........................
# Data: {'persons': {u'fav_color': u'red', u'_id': ObjectId('5a1bec38814511659779e534'), u'name': u'akshata', u'budget': 50000000.0}, 'vehicles': {u'model': u'Swift', u'color': u'red', u'company': u'Maruti', u'wheels': 4.0, u'_id': ObjectId('5a042309bae3828177788d4b'), u'price': 6500000.0}, 'companies': {u'_id': ObjectId('5a1d26db4e6bc7ebf228ab9a'), u'name': u'Maruti'}}
