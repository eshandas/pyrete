from __future__ import absolute_import

import datetime

from celery import task

from rule_engine.core.nodes import (
    ReteGraph,
)
from rule_engine.core.engine import (
    RuleEngine,
)
from rule_engine.core.data_layer import (
    DataLayer,
)
from rule_engine.core.variable_processor import (
    VariableProcessor,
)

from rule_engine.rules.models import ExecutionSummary
import json
import logging
from rule_engine import settings


@task(name='Trigger Rule')
def trigger_rule(rule, email, rule_key, webhook_data=None):
    """
    Trigger a rule
    """
    graph = ReteGraph()
    graph.load_rule(rule)

    # ---------------------- Fetch data from DB
    data = DataLayer().get_data(
        rules=[rule],
        filter={},
        limit=0)
    data['webhook'] = [webhook_data]
    print len(data)
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
        key=rule_key,
        email=email)
    logging.basicConfig(filename=settings.LOG_FILE, level=logging.INFO)
    logging.info('--------------------------------------')
    logging.info(rule_key)
    logging.info(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    trigger = json.dumps(trigger)
    execution_summary = ExecutionSummary(rule_key=rule_key, rule_summary=trigger)
    execution_summary.save()
    return trigger
