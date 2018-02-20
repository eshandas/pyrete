from events.models import (
    Event,
)
from rule_engine import settings
from company_users.models import (
    User,
)
from rule_engine.core.data_layer import DataLayer
from rule_engine.core.constants import (
    TriggerType,
)
from .models import (
    Rule
)
import redis
import ast
def validate_rules(rule):
    for each_obj in rule:
        array_obj = each_obj['then']
        for t in array_obj:
            if t.get('trigger_type') == TriggerType.WEBHOOK and bool(t.get('webhook_details')) is False:
                return None
        return rule


# def webhook_dict_efficiently(params, datum):
#     rule_dict = {}
#     # Optimised way to return webhook response
#
#     def check_param(params, i, datum):
#         for key in datum.keys():
#             if key == params[i]:
#                 value = datum[params[i]]
#                 break
#
#             value = params[i]
#
#             yield value
#
#     for i in params:
#         for value in check_param(params, i, datum):
#             rule_dict.update({i: value})
#         return rule_dict


def insert_rule(rule):
    settings.DB['rules'].insert_many(rule)


def validate_key(key, company):
    if Event.objects.filter(company=company, key=key).exists():
        event = Event.objects.get(
            company=company,
            key=key)
        return event
    else:
        return None


def validate_rule_key(key):
    # Check for duplicate keys.
    if Rule.objects.filter(key=key).exists():
        return None
    else:
        return key


def pop_keys(data):
    if 'key' in data:
        data.pop('key')
    if 'description' in data:
        data.pop('description')


def update_rule(key, rule, description, collection):
    if Rule.objects.filter(key=key).exists():
        data_mapper = DataLayer()
        collection_names = data_mapper.get_all_collections()
        if set(collection).issubset(set(collection_names)):
            # Update rule based on the key.
            rule_obj = Rule.objects.get(key=key)
            rule_obj.rule = rule
            rule_obj.description = description
            rule_obj.save()
            return rule_obj
    else:
        return None


def validate_user_events(event, email, company):
    if User.objects.filter(email=email, company=company).exists():
        # If email already exist ,update only the total_points in the user table.
        user = User.objects.get(email=email, company=company)
        user.total_points = user.total_points + event.event_points
        user.save()
        return user
    else:
        # initial update of the event points.
        user = User(
            email=email,
            company=company,
            total_points=event.event_points)
        user.save()
        user.refresh_from_db()
        return user


class Redis(object):

    def __init__(self):
        self.id =id

    @staticmethod
    def check_multiple_instance_redis(rule):
        redis_db_url = '127.0.0.1'
        r = redis.StrictRedis(host=redis_db_url, port=6379, db=0)
        dict_r = r.smembers('user')
        if dict_r:
            lst = list(dict_r)
            for ls in lst:
                json_data = ast.literal_eval(ls)
                if json_data['rule_id'] == rule.id:
                    return True

            return False
