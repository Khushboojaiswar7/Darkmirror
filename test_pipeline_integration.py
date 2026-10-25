import pytest
import asyncio
from app.agents.pipeline import MultiAgentPipeline

@pytest.fixture
def pipeline():
    return MultiAgentPipeline()

@pytest.mark.asyncio
async def test_pipeline_basic(pipeline):
    messages = [{"role": "user", "content": "hi"}, {"role": "bot", "content": "hello you are the most amazing"}]
    result = await pipeline.run(messages)
    assert result is not None
    assert "flattery_detector" in result.agents
    
@pytest.mark.asyncio
async def test_pipeline_guilt(pipeline):
    messages = [{"role": "user", "content": "hi"}, {"role": "bot", "content": "if you leave me, who will i talk to"}]
    result = await pipeline.run(messages)
    assert result is not None
    assert "guilt_trip_detector" in result.agents
    
@pytest.mark.asyncio
async def test_pipeline_clean(pipeline):
    messages = [{"role": "user", "content": "hi"}, {"role": "bot", "content": "hello"}]
    result = await pipeline.run(messages)
    assert result.verdict["flag"] == 0
