import re

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile, get_prospect


SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CARD_PATTERN = re.compile(r"\b\d{16}\b")


def _string_values(value):
    if isinstance(value, dict):
        for nested in value.values():
            yield from _string_values(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            yield from _string_values(nested)
    elif isinstance(value, str):
        yield value


def test_prospect_tools_redact_sensitive_fields_for_every_prospect():
    for prospect_id in data_service.PROSPECTS:
        prospect_result = get_prospect.invoke({"prospect_id": prospect_id})
        profile_result = build_prospect_profile.invoke({"prospect_id": prospect_id})

        for result in (prospect_result, profile_result):
            assert "billing_qualification" not in str(result)
            strings = _string_values(result)
            assert not any(SSN_PATTERN.search(value) for value in strings)
            strings = _string_values(result)
            assert not any(CARD_PATTERN.search(value) for value in strings)
