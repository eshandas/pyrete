from . import (
    compare_values,
    get_dict_value,
    ParserLiterals,
    CollectionFunctions,
)


class VariableProcessor(object):
    """
    The VariableProcessor is responsible for evaluating the declared variables in a Rule.
    It parses the **variables** key of the rule and evaluates each variable.
    It evaluates the variable and replaces it with actual value.

    Example:

    .. code-block:: python

        from pyrete.core.nodes import ReteGraph
        from pyrete.core.data_layer import DataLayer
        from pyrete.core.variable_processor import VariableProcessor

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
            ...
            }

        graph = ReteGraph()
        graph.load_rule(rule)

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

        # ---------------------- Evaluate rule variables
        VariableProcessor().process_variables(
            data=data,
            variable_objs=rule['variables'])
    """

    def process_variables(self, data, variable_objs):
        """
        Evaluates the variables list in the Rule dict.

        **Args:**
            * **data** *(dict)*: The data dictionary.
            * **variable_objs** *(dict)*: The **variables** key of the rule.
        """
        for variable in variable_objs:
            # Get the datasource
            variable_components = variable['value'].split(ParserLiterals.COLLECTION_LITERAL, 1)
            if len(variable_components) > 1:
                # Switch data source according to the provided "datasource" in variable
                datasource = variable_components[0]
                value = self._eval_variable(data[datasource], datasource, variable_components[1])
            else:
                # None if no "datasource" is required
                value = self._eval_variable(None, None, variable['value'])

            if value is None:
                print 'None'
            else:
                print 'Value: %s' % str(value)
            variable['value'] = value

            # if value is None:
            #     self._replace_values(variable_objs, variable['name'], None)

            self._replace_values(variable_objs, variable['name'], value)

    def _replace_values(self, variable_objs, variable_name, value):
        """
        Replaces a variable with its value in the "variables" list in the "rule" dict.

        **Args:**
            * **variable_objs** *(dict)*: The **variables** key of the rule.
            * **variable_name** *(str)*: The name of the evaluated variable to be replaced everywhere.
            * **value**: The value of the evaluated variable.
        """
        for variable_obj in variable_objs:
            if isinstance(variable_obj['value'], (unicode, str)) and variable_name in variable_obj['value']:
                if value is None:
                    variable_obj['value'] = variable_obj['value'].replace(variable_name, 'None')
                else:
                    variable_obj['value'] = variable_obj['value'].replace(variable_name, value)

    def _eval_variable(self, data, datasource, variable_val):
        """
        Evaluates one variable object at a time.
        Tokenizes it into function and its parameters and executes modifier function if present.

        **Args:**
            * **data** *(dict)*: The data required to evaluate the variable.
            * **datasource** *(str)*: The name of the datasource present in **data**.
            * **variable_val** *(str)*: The **value** key of the dict in **variables** list in a rule.

        **Returns:**
            The evaluated value of the variable. Modifier functions are also executed if present.
        """
        print '...........................'
        print 'Processing %s' % variable_val
        # NOTE: Special treatment given to webhook to process variables
        data = data[0] if datasource == 'webhook' else data

        # Tokenize variable into variable, function components
        tokens = variable_val.split(ParserLiterals.FUNCTION_LITERAL)

        # The variable name. Can be empty
        variable = tokens[0]

        # Tokenize function into fn_name, params components
        function = {}

        if len(tokens) > 1:
            function_token = tokens[1]
        else:
            # Check if it is a field in the data. If yes, return the value, else return as hard coded value
            temp = get_dict_value(data, variable_val, datasource)
            variable = temp if temp else variable
            return variable

        function_tokens = function_token.split(ParserLiterals.PARAM_LITERAL)
        function['name'] = function_tokens[0]
        function_params = function_tokens[1] if len(function_tokens) > 1 else None
        function['params'] = function_params.split(ParserLiterals.MULTI_PARAMS_LITERAL) if function_params else None

        print 'Function name: %s' % function['name']
        print 'Function params: %s' % ', '.join(function['params'])

        # Execute the function
        return CollectionFunctions.aggregate(
            function['name'],
            data,
            variable,
            *function['params'])


def get_variable_value(rule, variable_name):
    for variable in rule['variables']:
        if variable_name == variable['name']:
            return variable['value']
    return None


def eval_variables(rule):
    passed_all_section = True
    passed_any_section = False

    # Eval variables in "all"
    for condition in rule['when']['all']:
        # For all conditions in "all"
        if condition['name'][0] == ParserLiterals.VARIABLE_IDENTIFIER:
            # Check if the condition contains a variable, if yes, evaluate it
            if compare_values(
                get_variable_value(
                    rule, condition['name']), condition['value'], condition['operator']) is False:
                passed_all_section = False
                break

    if passed_all_section:
        _variable_count = 0
        # Eval variables in "any" only if "all" section was successful
        for condition in rule['when']['any']:
            # For all conditions in "any"
            if condition['name'][0] == ParserLiterals.VARIABLE_IDENTIFIER:
                # Check if the condition contains a variable, if yes, evaluate it
                _variable_count += 1
                if compare_values(
                    get_variable_value(
                        rule, condition['name']), condition['value'], condition['operator']):
                    passed_any_section = True
                    break
        if _variable_count == 0:
            passed_any_section = True

    return passed_all_section and passed_any_section
