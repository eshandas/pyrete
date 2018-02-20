import iso8601


AGGREGATION_FUNCTION_NAMES = (
    'count',
    'sum',
    'avg',
)


COLLECTION_AGGREGATION_FUNCTION_NAMES = (
    'get_frequency',
    'get_by_index',
    'days_diff',
)

CONVERSION_FUNCTION_NAMES = (
    'as_str',
)


class ParserLiterals(object):
    COLLECTION_LITERAL = '>>'
    FUNCTION_LITERAL = '__'
    PARAM_LITERAL = '::'
    MULTI_PARAMS_LITERAL = '||'
    VARIABLE_IDENTIFIER = '$'
    OBJECT_VALUE_IDENTIFIER = '^^'


def compare_values(left_value, right_value, operator):
    # if isinstance(value, list):
    #     return self._eval_list(value, self.condition['operator'])

    if operator == 'equal_to':
        return left_value == right_value
    if operator == 'not_equal_to':
        return left_value != right_value
    if operator == 'greater_than':
        return left_value > right_value
    if operator == 'less_than':
        return left_value < right_value
    if operator == 'greater_than_equal_to':
        return left_value >= right_value
    if operator == 'less_than_equal_to':
        return left_value <= right_value


def get_object_name(key):
    """
    Gets the name of the object of a key
    """
    components = key.split(ParserLiterals.COLLECTION_LITERAL, 1)
    if len(components) > 1:
        return components[0]
    else:
        return None


def get_attr_name(key):
    """
    Identifies the collection_name and functions

    **Args:**
        key(string): The key from rule

    **Returns:**
        The collection_name, key, fn_name and fn_type after identifying the aggregation function
    """
    # Trying to find the collection name
    key = key.split(ParserLiterals.COLLECTION_LITERAL, 1)
    if len(key) > 1:
        # If COLLECTION_LITERAL is present, 0th is the collection name
        collection_name = key[0]
        key = key[1]
    else:
        collection_name = None
        key = key[0]
    strs = key.split(ParserLiterals.FUNCTION_LITERAL)

    # Remove params from function
    if len(strs) > 1:
        strs[1] = strs[1].split(ParserLiterals.PARAM_LITERAL)[0]

    try:
        if strs[1] in AGGREGATION_FUNCTION_NAMES:
            # If has aggregation function, return the field name
            return collection_name, strs[0], strs[1], DocumentFunctions.TYPE
        elif strs[1] in COLLECTION_AGGREGATION_FUNCTION_NAMES:
            # If has conversion function, return the field name
            return collection_name, strs[0], strs[1], ConversionFunctions.TYPE
        elif strs[1] in CONVERSION_FUNCTION_NAMES:
            # If has conversion function, return the field name
            return collection_name, strs[0], strs[1], ConversionFunctions.TYPE
        else:
            return collection_name, None, None, None
    except IndexError:
        # If there aren't any function associated and is not a variable, send as it is
        if ParserLiterals.VARIABLE_IDENTIFIER in strs[0]:
            return collection_name, None, None, None
        else:
            return collection_name, strs[0], None, None


class ConversionFunctions(object):
    TYPE = 'conversion_fn'

    @staticmethod
    def eval_conversion(fn_name, value):
        """
        Converts the passed value to a given data type
        **Args:**
            * **fn_name**(string): the function name
            * **value**(string): the key whose value needs to be fetched

        **Returns:**
            converts string into its respective datatype based on the 'conversion_fn'
        """
        if fn_name == 'as_str':
            return str(value)
        if fn_name == 'as_int':
            return int(value)
        if fn_name == 'as_float':
            return float(value)
        if fn_name == 'as_bool':
            return bool(value)


class DocumentFunctions(object):
    TYPE = 'aggregation_fn'

    @staticmethod
    def aggregate(fn_name, value_list):
        """
        Executes aggregate functions on a given list.
        For egs: average, count etc
        **Args:**
            * **fn_name**(string): the function name
            * **value_list**(list): list of values on which aggregation fn needs to be performed
        **Returns:**
            returns the aggregated value of the list

        """
        if fn_name == 'count':
            return len(value_list)
        elif fn_name == 'avg':
            print reduce(lambda x, y: x + y, value_list) / len(value_list)


def get_dict_value(datum, key_chain, collection_name, collection=None):
    """
    Gets the required collection's data and calls get_value with the appropriate data
    **Args:**
        * **datum**(dict): the datum whose value needs to be fetched
        * **key_chain**(string): the key whose value needs to be fetched
        * **collection_name**(string): the collection_name from the key_chain
        * **collection**(string): the collection which it belongs to which is passed during 'run'

    **Returns:**
        o/p of get_value(datum, key_chain)
    For egs:
    if key in the rule was : 'users.name', and the collection is 'users', the method accepts:
        datum
        split key_chain: i.e., 'name' in this case
        the collection_name from the key_chain : 'users'
        the collection which it belongs to which is passed during 'run' : 'users'

    """
    if collection_name == collection or collection is None:
        return get_value(datum, key_chain)
    else:
        return None


def get_value(datum, key_chain):
    """
    Gets the value from datum based on dot notation key_chain
    **Args:**
        * **datum**(dict): the datum whose value needs to be fetched
        * **key_chain**(string): the key whose value needs to be fetched. For embedded keys, it is notated by '>>'. Refer egs below

    **Returns:**
        Either a value or a list depending upon the the value
    For egs:
    1. key = 'address>>city', datum = {'address': {'city': 'NY'}}
    the function returns 'NY'
    2. key = 'users>>banks>>name', datum = {'users': {'banks': [{'id': 1, 'name': 'HDFC'}, {{'id': 2, 'name': 'SBI'}}]}}
    the function returns: ['HDFC', 'SBI']
    3. None if key does not exist
    """
    keys = key_chain.split(ParserLiterals.COLLECTION_LITERAL)
    key = keys[0]

    if key not in datum:
        # If the key doesn't exist, return None
        return None

    if len(keys) == 1:
        # If level 0 in dictionary
        return datum[key]

    if isinstance(datum[key], dict):
        # if value is a dict, pass the dict and remove parent key_chain from key_chain
        return get_value(datum[key], ParserLiterals.COLLECTION_LITERAL.join(keys[1:]))

    elif isinstance(datum[key], list):
        # if value is a list of dict
        if len(datum[key]) > 0 and isinstance(datum[key][0], dict):
            values = []
            for inner_dict in datum[key]:
                # if isinstance(inner_dict[keys[1]], list) and isinstance(inner_dict[keys[1]][0], dict):
                ret_val = get_value(inner_dict, ParserLiterals.COLLECTION_LITERAL.join(keys[1:]))
                if isinstance(ret_val, list):
                    values.extend(ret_val)
                else:
                    values.append(ret_val)
            return values
        else:
            # If the key doesn't exist, return None
            return None


class CollectionFunctions(object):
    TYPE = 'collection_aggregation_fn'

    @staticmethod
    def aggregate(fn_name, data, *args):
        """
        Executes aggregate functions on given data.
        For egs: average, count etc
        **Args:**
            * **fn_name**(string): the function name
            * **data**(dict): data on which aggregation fn needs to be performed
            * **args**(list)

        **Returns:**
            returns the aggregated value of the data
        """
        if 'None' in args:
            return None
        if fn_name == 'get_frequency':
            return CollectionFunctions.get_frequency(data, args[0], args[1])
        if fn_name == 'get_by_index':
            return CollectionFunctions.get_by_index(data, args[0], args[1], args[2])
        if fn_name == 'days_diff':
            return CollectionFunctions.days_diff(args[1], args[2])
        if fn_name == 'add':
            return CollectionFunctions.add(args[1], args[2])
        if fn_name == 'sub':
            return CollectionFunctions.sub(args[1], args[2])
        if fn_name == 'mul':
            return CollectionFunctions.mul(args[1], args[2])
        if fn_name == 'div':
            return CollectionFunctions.div(args[1], args[2])

    @staticmethod
    def get_frequency(data, field, value):
        """
        Find frequency of "field" with "value" in the "data"
        **Args:**
            * **data**(dict): data on which aggregation fn needs to be performed
            * **field**(string): the field
            * **value**(string): No. of occurences of this value

        **Returns:**
            returns the count
        """
        counter = 0
        for datum in data:
            if datum[field] == value:
                counter += 1

        return counter

    @staticmethod
    def get_by_index(data, field, value, index):
        """
        Get the index'th item from data[field] if data[field] is a list
        **Args:**
            * **data**(list): data on which aggregation fn needs to be performed
            * **field**(string): the field
            * **value**(string): the value
            * **index**(int)

        **Returns:**
            returns the count
        """
        try:
            index = int(index)
            value = value.split('=')
            sorted_data = [datum for datum in data if datum[value[0]] == value[1]]
            sorted_data = sorted(sorted_data, key=lambda k: k[field])
            return sorted_data[index][field]
        except IndexError:
            return None

    @staticmethod
    def days_diff(first_date, second_date):
        """
        Get days_difference between two dates
        **Args:**
            * **first_date**(string)
            * **second_date**(string)

        **Returns:**
            returns the days difference
        """
        first_date = iso8601.parse_date(first_date).date()
        second_date = iso8601.parse_date(second_date).date()
        return (first_date - second_date).days

    @staticmethod
    def add(first_number, second_number):
        return float(first_number) + float(second_number)

    @staticmethod
    def sub(first_number, second_number):
        return float(first_number) - float(second_number)

    @staticmethod
    def mul(first_number, second_number):
        return float(first_number) * float(second_number)

    @staticmethod
    def div(first_number, second_number):
        return float(first_number) / float(second_number)
