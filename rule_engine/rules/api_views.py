from django.http import Http404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rule_engine import settings
from appauth.api_authentications import (
    CompanyTokenAuthenticationAllMethods,
)
import redis
from celery.result import AsyncResult
from .constants import (
    Keys,
    FailMessages,
    RequestKeys,
    SuccessMessages,
    ResponseKeys
)
from .validations import (
    validate_rule_key,
    update_rule,
    pop_keys
)
import ast
import json

from kv_settings.models import KeyValueSetting
from .models import (
    Rule
)

from utils.response_handler import (
    ResponseHandler,
    generic_response,
)

from rule_engine.core.data_layer import DataLayer

from .serializers import (
    RuleSerializer,
)

from .tasks import (
    trigger_rule,
)

from utils.redis_store import RedisStore

from rule_engine.rules.models import TriggeredRules


class ActiveDatabase(APIView):
    authentication_classes = (CompanyTokenAuthenticationAllMethods, )

    def get_object(self):
        try:
            database_setting = KeyValueSetting.objects.get(key=Keys.DATABASE_CONNECTION)
        except KeyValueSetting.DoesNotExist:
            database_setting = KeyValueSetting(
                key=Keys.DATABASE_CONNECTION,
                value='{}')
            database_setting.save()
        return database_setting

    def get(self, request):
        """
        Gets the currently active database
        """
        database_setting = self.get_object()
        try:
            database_setting = json.loads(database_setting.value)
        except ValueError:
            database_setting = {}
        return Response(
             database_setting,
            status=status.HTTP_200_OK)

    def post(self, request):
        """
        Sets the connection to an active database. Only MongoDB is supported right now.

            {
                "name": "Staging",
                "databaseType": "MongoDB",
                "connection": {
                    "uri": ""
                }
            }
        """
        name = request.data.get(RequestKeys.NAME, None)
        database_type = request.data.get(RequestKeys.DATABASE_TYPE, None)
        connection = request.data.get(RequestKeys.CONNECTION, None)

        if name and database_type and connection:
            database_setting = self.get_object()
            database_setting.value = json.dumps({
                'name': name,
                'databaseType': database_type,
                'connection': connection
            })
            database_setting.save()
            return Response(
                ResponseHandler.get_result(SuccessMessages.DATABASE_DETAILS_SAVED),
                status=status.HTTP_200_OK)
        else:
            return Response(
                ResponseHandler.get_result(FailMessages.INVALID_DATABASE_DETAILS),
                status=status.HTTP_400_BAD_REQUEST)


class AcceptRulesAPI(APIView):
    """
    An API to accept rules
    """
    authentication_classes = (CompanyTokenAuthenticationAllMethods, )

    def post(self, request):
        """
        An API to accept rules

            {
                "key": "some_rule",
                "description": "Some awesome description",
                "collection":"orders",
                "variables": [
                    {
                        "name": "$email",
                        "value": "email",
                        "datasource": "webhook"
                    },
                    {
                        "name": "$email_order_count",
                        "value": "email__get_frequency::$email",
                        "datasource": "orders"
                    }
                    ],
                "when": {
                    "any": [{
                        "name": "total_price",
                        "operator": "equal_to",
                        "value": "29.00"
                    }],
                    "all": [{
                       "name": "$email_order_count",
                        "operator": "equal_to",
                        "value": 1
                    }]
                },
                "then": [{
                        "key": "create_order",
                        "trigger_type": "webhook",
                        "webhook_details": {
                            "url": "https://www.google.co.in/",
                            "method": "POST"
                        },
                       "params": [
                            {
                                "name": "email_str",
                                "value": "email__as_str"
                            },
                            {
                                "name": "price",
                                "value": "total_price"
                            },
                            {
                                "name": "count",
                                "value": "note_attributes__count"
                            }
                    ]
                    },
                    {
                        "key": "award_points",
                        "trigger_type": "loyalty_event",
                        "webhook_details": {},
                         "params": [
                            {
                                "name": "points",
                                 "value": "1000__as_str"

                            }
                        ]
                    }
                ]
            }
        """
        try:
            data_mapper = DataLayer()
            key = request.data.get(RequestKeys.KEY)
            description = request.data.get(RequestKeys.DESCRIPTION, None)
            collection = request.data.get(RequestKeys.COLLECTION, None)
            rule = request.data
            pop_keys(rule)
            collection_names = data_mapper.get_all_collections()
            if 'webhook' in collection:
                collection_names.append('webhook')
            if set(collection).issubset(set(collection_names)):
                rule = json.dumps(rule)
                rule_obj = validate_rule_key(key)
                if rule_obj:
                    rule = Rule(
                        rule=rule,
                        key=key,
                        description=description
                    )
                    rule.save()
                    rule.refresh_from_db()
                    data = {
                        'id': rule.id,
                        'key': rule.key
                    }
                    return Response(ResponseHandler.get_result(data),
                                    status=status.HTTP_200_OK)
                else:
                    return Response(
                        ResponseHandler.get_result(FailMessages.KEY_EXIST), status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    ResponseHandler.get_result(FailMessages.INVALID_COLLECTION), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(ResponseHandler.get_result(e.message), status=status.HTTP_400_BAD_REQUEST)


class RuleAPI(APIView):
    authentication_classes = (CompanyTokenAuthenticationAllMethods, )
    query_params = [{'name': RequestKeys.KEY, 'required': True}]
    serializer_class = RuleSerializer

    def get_object(self, key):
        try:
            rule = Rule.objects.get(key=key)
            return rule
        except Rule.DoesNotExist:
            raise Http404

    def get(self, request):
        """
        Gets the rule by key
        """
        key = request.GET.get(RequestKeys.KEY, None)
        rule = self.get_object(key)
        serializer = self.serializer_class(rule)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK)

    def post(self, request):
        """
        An API to update rule

            {
                "key": "some_rule",
                "description": "Some awesome description",
                "collection":"orders",
                "variables": [
                    {
                        "name": "$email",
                        "value": "email",
                        "datasource": "webhook"
                    },
                    {
                        "name": "$email_order_count",
                        "value": "email__get_frequency::$email",
                        "datasource": "orders"
                    }
                    ],
                "when": {
                    "any": [{
                        "name": "total_price",
                        "operator": "equal_to",
                        "value": "29.00"
                    }],
                    "all": [{
                        "name": "$email_order_count",
                        "operator": "equal_to",
                        "value": 1
                    }]
                },
                "then": [{
                        "key": "create_order",
                        "trigger_type": "webhook",
                        "webhook_details": {
                            "url": "https://www.google.co.in/",
                            "method": "POST"
                        },
                        "params": [
                            {
                                "name": "email_str",
                                "value": "email__as_str"
                            },
                            {
                                "name": "price",
                                "value": "total_price"
                            },
                            {
                                "name": "count",
                                "value": "note_attributes__count"
                            }
                    ]
                    },
                    {
                        "key": "award_points",
                        "trigger_type": "loyalty_event",
                        "webhook_details": {},
                        "params": [
                            {
                                "name": "points",
                                 "value": "1000__as_str"

                            }
                        ]
                    }
                ]
            }
        """
        key = request.GET.get(RequestKeys.KEY, None)
        description = request.data.get(RequestKeys.DESCRIPTION, None)
        collection = request.data.get(RequestKeys.COLLECTION, None)
        pop_keys(request.data)
        rule = json.dumps(request.data)
        rule_obj = update_rule(key, rule, description, collection)
        if rule_obj is not None:
            return Response(
                ResponseHandler.get_result(SuccessMessages.UPDATE_RULES_SUCCESS),
                status=status.HTTP_200_OK)
        else:
            return Response(
                ResponseHandler.get_result(FailMessages.INVALID_KEY),
                status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        delete the rule by key
        """
        key = request.GET.get(RequestKeys.KEY, None)
        rule = self.get_object(key)
        rule.delete()
        return Response(ResponseHandler.get_result(SuccessMessages.DELETE_RULES_SUCCESS),
                        status=status.HTTP_200_OK)


class GetAllRulesAPI(APIView):
    serializer_class = RuleSerializer
    authentication_classes = (CompanyTokenAuthenticationAllMethods,)

    def get(self, request):
        """
        An API to get all rules

        """
        try:
            rules = Rule.objects.all()
            serializer = self.serializer_class(rules, many=True)
            return Response(generic_response({'rules': serializer.data}))
        except Exception, e:
            return Response(ResponseHandler.get_result(e.message),
                            status=status.HTTP_400_BAD_REQUEST)


class GetCollectionNamesAPI(APIView):
    # COLLECTIONS = ['orders', 'products', 'customers']
    authentication_classes = (CompanyTokenAuthenticationAllMethods,)

    def get(self, request):
        """
        An API to get all collection names

        """
        # TODO - Uncomment this later
        data_mapper = DataLayer()
        collection_names = data_mapper.get_all_collections()
        return Response(generic_response({'collections': collection_names}))


class GetCollectionFieldsAPI(APIView):
    query_params = [{'name': 'collection', 'required': True}]
    authentication_classes = (CompanyTokenAuthenticationAllMethods,)

    def get(self, request):
        """
        AN API to get a collection's fields

        """
        collection = request.GET.get('collection', None)
        if collection:
            data_mapper = DataLayer()
            fields = data_mapper.get_collection_fields(collection)
            return Response(generic_response({'fields': fields}))
        else:
            return Response(ResponseHandler.get_result(FailMessages.INVALID_COLLECTION),
                            status=status.HTTP_400_BAD_REQUEST)


class GetAllCollectionInfo(APIView):
    authentication_classes = (CompanyTokenAuthenticationAllMethods,)

    def get(self, request):
        """
        AN API to get all collection's fields

        """
        data_mapper = DataLayer()
        collections = data_mapper.get_all_collections()
        data = []
        if collections:
            for collection in collections:
                fields = data_mapper.get_collection_fields(collection)
                data.append({
                            'collection': collection,
                            'fields': fields})
            return Response(generic_response(data))
        else:
            return Response(ResponseHandler.get_result(FailMessages.INVALID_COLLECTION),
                            status=status.HTTP_400_BAD_REQUEST)


class CeleryStatus(APIView):
    authentication_classes = (CompanyTokenAuthenticationAllMethods,)
    query_params = [{'name': 'key', 'required': True}]

    def get(self, request):
        # TODO -- Improve this later
        try:
            rule_key = request.GET.get(RequestKeys.RULE_KEY)
            if rule_key:
                redis_store = RedisStore()
                token = redis_store.get_id(rule_key, request.user.email)
                if token:
                    data = {}
                    is_completed = False
                    result = AsyncResult(token)
                    if result.status == 'SUCCESS':
                        is_completed = True
                        triggered_rule = TriggeredRules.objects.filter(rule_key=rule_key, email=request.user.email)
                        if triggered_rule:
                            data[ResponseKeys.ITEMS_PASSED] = len(ast.literal_eval(triggered_rule[0].data))
                        redis_store.delete_cache(rule_key, request.user.email)
                    data[ResponseKeys.IS_COMPLETED] = is_completed
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        ResponseHandler.get_result(FailMessages.INVALID_INPUT),
                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    ResponseHandler.get_result(FailMessages.INVALID_INPUT),
                    status=status.HTTP_400_BAD_REQUEST)
        except Exception, e:
            return Response(
                ResponseHandler.get_result(e.message),
                status=status.HTTP_400_BAD_REQUEST)


class TriggerRuleAPI(APIView):
    authentication_classes = (CompanyTokenAuthenticationAllMethods, )

    def get_object(self, key):
        try:
            rule = Rule.objects.get(key=key)
            return rule
        except Rule.DoesNotExist:
            raise Http404

    def post(self, request):
        """
        An API to trigger a rule

        Data:

            {
                "key": "sample_rule",
                "webhookData": {
                    "_id": "Webhook_data",
                    "email": "testar7@mailinator.com",
                    "total_price": "57.00",
                    "taxes": "12.50",
                    "note_attributes": [1, 2, 3]
                }
            }
        """
        rule_key = request.data.get(RequestKeys.KEY, None)
        webhook_data = request.data.get(RequestKeys.WEBHOOK_DATA, None)
        if rule_key:
            rule = self.get_object(rule_key)

            res = trigger_rule.delay(rule.get_rule(), request.user.email, rule_key, webhook_data)
            redis_store = RedisStore()
            redis_store.store_dict(request.user.email, res.id, rule_key)
            return Response(
                ResponseHandler.get_result(SuccessMessages.PROCESS_STARTED_SUCCESSFULLY),
                status=status.HTTP_200_OK)
        else:
            return Response(
                ResponseHandler.get_result(FailMessages.INVALID_KEY),
                status=status.HTTP_400_BAD_REQUEST)
