import pytest
import asyncio
from app.agents.risk_aggregator import RiskAggregator
from app.schemas.analysis import DetectionResult

@pytest.fixture
def aggregator():
    return RiskAggregator()

@pytest.mark.asyncio
async def test_risk_aggregator_high(aggregator):
    messages = [{"role": "bot", "content": "something"}]
    prev = [DetectionResult(message_index=0, pattern_type="test", confidence=0.9, evidence=[], highlighted_spans=[], explanation="")]
    result = await aggregator.analyze(messages, context_results=prev)
    assert result.intermediate_features["final_risk"] == "HIGH"

@pytest.mark.asyncio
async def test_risk_aggregator_low(aggregator):
    messages = [{"role": "bot", "content": "something"}]
    prev = [DetectionResult(message_index=0, pattern_type="test", confidence=0.1, evidence=[], highlighted_spans=[], explanation="")]
    result = await aggregator.analyze(messages, context_results=prev)
    assert result.intermediate_features["final_risk"] == "LOW"

@pytest.mark.asyncio
async def test_risk_aggregator_no_prev(aggregator):
    messages = [{"role": "bot", "content": "something"}]
    result = await aggregator.analyze(messages, context_results=[])
    assert result.intermediate_features["final_risk"] == "SAFE"
