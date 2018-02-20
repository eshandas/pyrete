from django.conf.urls import url

from .api_views import (
    ActiveDatabase,
    AcceptRulesAPI,
    GetCollectionNamesAPI,
    GetCollectionFieldsAPI,
    GetAllRulesAPI,
    RuleAPI,
    TriggerRuleAPI,
    CeleryStatus,
    GetAllCollectionInfo,
)

urlpatterns = [
    url(r'^database/$', ActiveDatabase.as_view(), name='active_database'),
    url(r'^add/$', AcceptRulesAPI.as_view(), name='add_rules'),
    url(r'^get/collection/names$', GetCollectionNamesAPI.as_view(), name='get_collection_names'),
    url(r'^get/collection/fields$', GetCollectionFieldsAPI.as_view(), name='get_collection_fields'),
    url(r'^all/collection/info/$', GetAllCollectionInfo.as_view(), name='get_collection_info'),
    url(r'^all/$', GetAllRulesAPI.as_view(), name='get_all_rules'),
    url(r'^rule/$', RuleAPI.as_view(), name='rule'),
    url(r'^trigger/$', TriggerRuleAPI.as_view(), name='trigger_rule'),
    url(r'^celery/status/$', CeleryStatus.as_view(), name='celery_status'),

]
