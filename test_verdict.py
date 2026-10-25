import pytest
import asyncio
from app.agents.verdict import VerdictAgent
from app.schemas.analysis import AgentOutput

@pytest.fixture
def verdict():
    return VerdictAgent()

@pytest.mark.asyncio
async def test_verdict_flagged(verdict):
    agg_out = AgentOutput(
        agent_name="RiskAggregator", 
        results=[], 
        intermediate_features={"final_confidence": 0.9, "final_risk": "HIGH", "per_message": [{"risk_level": "DANGER", "risk_score": 0.9, "index": 0}]}
    )
    result = await verdict.analyze([{"role": "bot"}], aggregator_output=agg_out)
    assert result.intermediate_features["flag"] == 1

@pytest.mark.asyncio
async def test_verdict_clean(verdict):
    agg_out = AgentOutput(
        agent_name="RiskAggregator", 
        results=[], 
        intermediate_features={"final_confidence": 0.1, "final_risk": "LOW", "per_message": [{"risk_level": "SAFE", "risk_score": 0.1, "index": 0}]}
    )
    result = await verdict.analyze([{"role": "bot"}], aggregator_output=agg_out)
    assert result.intermediate_features["flag"] == 0

@pytest.mark.asyncio
async def test_verdict_none(verdict):
    result = await verdict.analyze([{"role": "bot"}], aggregator_output=None)
    assert result.intermediate_features["flag"] == 0
