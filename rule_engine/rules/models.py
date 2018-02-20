from __future__ import unicode_literals

from django.db import models

import json


class Rule(models.Model):
    """
    Rule Engine

    """
    key = models.CharField(
        max_length=255
    )
    description = models.CharField(
        max_length=255,
        null=True
    )
    rule = models.TextField()
    added_on = models.DateTimeField(
        auto_now_add=True)
    updated_on = models.DateTimeField(
        auto_now=True)

    def get_rule(self):
        rule = json.loads(self.rule)
        rule['key'] = self.key
        return rule

    def __str__(self):
        return self.key

    class Meta:
        verbose_name_plural = 'rules'


class TriggeredRules(models.Model):
    """
    Contains all the data that was triggered by a single rule

    """

    rule_key = models.CharField(
        max_length=255
    )
    email = models.EmailField(
        max_length=255
    )
    data = models.TextField()


class ExecutionSummary(models.Model):
    rule_key = models.CharField(
        max_length=255
    )
    rule_summary = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Execution Summary'

    def __str__(self):
        return self.rule_key
