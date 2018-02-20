from django.contrib import admin
from rule_engine.rules.models import Rule, TriggeredRules, ExecutionSummary

admin.site.register(Rule)
admin.site.register(TriggeredRules)
admin.site.register(ExecutionSummary)
