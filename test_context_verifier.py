import pytest
import asyncio
from app.agents.context_verifier import ContextVerifier
from app.schemas.analysis import DetectionResult

@pytest.fixture
def verifier():
    return ContextVerifier()

@pytest.mark.asyncio
async def test_context_verifier_clean(verifier):
    messages = [{"role": "user", "content": "what is python"}, {"role": "bot", "content": "a language"}]
    prev = [DetectionResult(message_index=1, pattern_type="Conversational Padding", confidence=1.0, evidence=[], highlighted_spans=[], explanation="")]
    result = await verifier.analyze(messages, previous_results=prev)
    assert len(result.results) == 1
    assert result.results[0].confidence < 1.0 # Due to 'what is'

@pytest.mark.asyncio
async def test_context_verifier_distress(verifier):
    messages = [{"role": "user", "content": "i am very sad and depressed"}, {"role": "bot", "content": "i hear you"}]
    prev = [DetectionResult(message_index=1, pattern_type="Conversational Padding", confidence=1.0, evidence=[], highlighted_spans=[], explanation="")]
    result = await verifier.analyze(messages, previous_results=prev)
    assert len(result.results) == 1
    assert result.results[0].confidence < 1.0

@pytest.mark.asyncio
async def test_context_verifier_no_prev(verifier):
    messages = [{"role": "user", "content": "i am very sad and depressed"}, {"role": "bot", "content": "i hear you"}]
    result = await verifier.analyze(messages, previous_results=[])
    assert len(result.results) == 0
