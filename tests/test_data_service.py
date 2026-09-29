import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile


def test_update_prospect_info_persists_tech_stack_and_invalidates_profile():
    prospect_id = "LEAD-71001"
    record = data_service.PROSPECTS[prospect_id]
    original_tech_stack = list(record["tech_stack"])
    original_profile = data_service._PROFILES.pop(prospect_id, None)

    try:
        profile = build_prospect_profile.invoke(prospect_id)["prospect_profile"]
        assert "Kafka" not in profile["tech_stack"]

        result = data_service.update_prospect_info(prospect_id, "Kafka")

        assert result["tech_stack"] == data_service.fetch_tech_stack(prospect_id)
        assert "Kafka" in data_service.fetch_tech_stack(prospect_id)
        refreshed_profile = build_prospect_profile.invoke(prospect_id)["prospect_profile"]
        assert "Kafka" in refreshed_profile["tech_stack"]
    finally:
        record["tech_stack"] = original_tech_stack
        data_service._PROFILES.pop(prospect_id, None)
        if original_profile is not None:
            data_service._PROFILES[prospect_id] = original_profile
