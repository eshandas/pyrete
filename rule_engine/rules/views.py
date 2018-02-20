from django.views.generic import View
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import Http404


class Rules(View):
    template_name = 'rule_engine/rules/all_rules.html'

    def get(self, request):
        return render(request, self.template_name, {})


class Rule(View):
    template_name = 'rule_engine/rules/rule.html'

    def get(self, request):
        return render(request, self.template_name, {})
