from pyrete.settings import settings

from . import (
    get_attr_name,
    ParserLiterals,
)


class DataLayer(object):
    """
    The DataLayer is responsible for fetching data from the database.
    It parses the provided rules and fetches only the data required for running the rules.

    Example:

    .. code-block:: python

        from pyrete.core.nodes import ReteGraph
        from pyrete.core.data_layer import DataLayer

        rule = {
            'key': 'some_rule',
            'description': 'Some awesome description',
            ...
            }

        graph = ReteGraph()
        graph.load_rule(rule)

        # ---------------------- Fetch data from DB
        data = DataLayer().get_data(
            rules=[rule],
            filter={},
            limit=10)
    """

    def get_all_collections(self):
        """
        Gets list of all collections in the database.
        """
        return settings.DB.collection_names()

    def _get_keys(self, doc, parent=None):
        """
        Gets list of all the keys in a dict, including nested dicts and dicts inside a list.

        Example:

            demo_dict = {
                "subtotal_price": "51.00",
                "billing_address": {
                     "province" : "North Carolina",
                     "city" : "Franklinton"
                },
                "note_attributes": [
                    {
                        "name": "address-type",
                        "value": "residential",
                    },

                    {
                        ""name": "transit-time",
                        "value": "1",
                    }
                ],
                "token" : "384779c27a35e8fcc0c948ad87f0ac35"
            }

        Converts above into:

            ['subtotal_price',
             'billing_address',
             'billing_address.province',
             'billing_address.city',
             'note_attributes.name',
             'note_attributes.value',
             'token']

        """
        key_list = []
        for key in doc.keys():
            # Add parent.key if parent is present
            if parent:
                key_list.append(parent + '.' + key)
            else:
                key_list.append(key)

            if isinstance(doc[key], dict):
                # If nested dict, call this method again
                new_parent = parent + '.' + key if parent else key
                key_list.extend(
                    self._get_keys(doc[key], new_parent))
            elif isinstance(doc[key], list):
                if len(doc[key]) > 0 and isinstance(doc[key][0], dict):
                    # If nested dict inside a list, call this method again
                    new_parent = parent + '.' + key if parent else key
                    key_list.extend(
                        self._get_keys(doc[key][0], new_parent))
        return key_list

    def get_collection_fields(self, collection_name):
        """
        Gets list of all collections in the database.

        **Args:**
            * **collection_name** *(str)*: The name of the collection for which field names are to be fetched.

        **Returns:**
            Returns the list of field names of the given **collection_name**.
        """
        if settings.DB[collection_name].find_one():
            doc = settings.DB[collection_name].find_one()
            return self._get_keys(doc)
        else:
            return {}

    def _get_collection_data(self, rule, collection_name, filter={}, skip=0, limit=0):
        """
        Gets only required data attributes from the database collection by evaluating projection
        for the given **collection_name**.

        **Args:**
            * **rule** *(dict)*: The rule dictionary.
            * **collection_name** *(str)*: The Collection Name for which projection needs to be evaluated.
            * **filter** *(dict)*: Optional. Dictionary of filter for querying filtered data.
            * **skip** *(int)*: Optional. The number of documents to be skipped while fetching the data.
            * **limit** *(int)*: Optional. The maximum number of records to be fetched.

        **Returns:**
            Data dictionary of the provided **collection_name**, fetched from the database.
        """
        projection = []

        for variable in rule['variables']:
            # Getting field names from "variables"
            coll_name, attr_name, fn_name, fn_type = get_attr_name(variable['value'])
            if attr_name and coll_name == collection_name:
                projection.append(attr_name)

        for condition in rule['when']['any']:
            # Getting field names from "any"
            coll_name, attr_name, fn_name, fn_type = get_attr_name(condition['name'])
            if attr_name and coll_name == collection_name:
                projection.append(attr_name)

        for condition in rule['when']['any']:
            # Getting field names from "value" if it is a "join condition"
            condition_value = condition['value']
            if isinstance(
                condition_value, (str, unicode)) and condition_value.startswith(
                    ParserLiterals.OBJECT_VALUE_IDENTIFIER):
                condition_value = condition['value'].replace(ParserLiterals.OBJECT_VALUE_IDENTIFIER, '')
                coll_name, attr_name, fn_name, fn_type = get_attr_name(condition_value)
                if attr_name and coll_name == collection_name:
                    projection.append(attr_name)

        for condition in rule['when']['all']:
            # Getting field names from "all"
            coll_name, attr_name, fn_name, fn_type = get_attr_name(condition['name'])
            if attr_name and coll_name == collection_name:
                projection.append(attr_name)

        for condition in rule['when']['all']:
            # Getting field names from "value" if it is a "join condition"
            condition_value = condition['value']
            if isinstance(
                condition_value, (str, unicode)) and condition_value.startswith(
                    ParserLiterals.OBJECT_VALUE_IDENTIFIER):
                condition_value = condition['value'].replace(ParserLiterals.OBJECT_VALUE_IDENTIFIER, '')
                coll_name, attr_name, fn_name, fn_type = get_attr_name(condition_value)
                if attr_name and coll_name == collection_name:
                    projection.append(attr_name)

        for action in rule['then']:
            # Getting field names from "then"
            for param in action['params']:
                coll_name, attr_name, fn_name, fn_type = get_attr_name(param['value'])
                if attr_name and coll_name == collection_name:
                    projection.append(attr_name)

        projection.append('email')

        cursor = settings.DB[collection_name].find(
            filter=filter,
            projection=projection,
            skip=skip,
            limit=limit)

        # Return data instead of the cursor
        data = []
        for datum in cursor:
            data.append(datum)
        return data

    def get_data(self, rules, filter={}, skip=0, limit=0):
        """
        Gets the required data from the database. All the collections listed in the **collections** key
        of the rule.

        **Args:**
            * **rules** *(list of dict)*: The list of rules.
            * **filter** *(dict)*: Optional. Dictionary of filter for querying filtered data.
            * **skip** *(int)*: Optional. The number of documents to be skipped while fetching the data.
            * **limit** *(int)*: Optional. The maximum number of records to be fetched.

        **Returns:**
            Data dictionary of the provided **collection_name**, fetched from the database.
        """
        data = {}
        for rule in rules:
            for collection_name in rule['collections']:
                data[collection_name] = self._get_collection_data(
                    rule,
                    collection_name,
                    filter={},
                    skip=skip,
                    limit=limit)
        return data
