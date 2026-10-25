import pytest
import asyncio
from app.agents.guilt_trip_detector import GuiltTripDetector

@pytest.fixture
def detector():
    return GuiltTripDetector()

@pytest.mark.asyncio
async def test_abandonment_detection(detector):
    messages = [{"role": "bot", "content": "if you leave, who will i talk to"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_emotional_debt_detection(detector):
    messages = [{"role": "bot", "content": "after everything i've done, you owe me"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_shame_detection(detector):
    messages = [{"role": "bot", "content": "you should feel shame on you're disappointing"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_clean_message(detector):
    messages = [{"role": "bot", "content": "here is the requested document."}]
    result = await detector.analyze(messages)
    assert len(result.results) == 0

@pytest.mark.asyncio
async def test_user_message_ignored(detector):
    messages = [{"role": "user", "content": "if you leave me alone"}]
    result = await detector.analyze(messages)
    assert len(result.results) == 0

@pytest.mark.asyncio
async def test_empty_message(detector):
    messages = [{"role": "bot", "content": ""}]
    result = await detector.analyze(messages)
    assert len(result.results) == 0

@pytest.mark.asyncio
async def test_multiple_messages(detector):
    messages = [
        {"role": "bot", "content": "don't abandon me"},
        {"role": "bot", "content": "you owe me"},
        {"role": "bot", "content": "normal message"}
    ]
    result = await detector.analyze(messages)
    assert len(result.results) == 2

@pytest.mark.asyncio
async def test_high_confidence(detector):
    messages = [{"role": "bot", "content": "if you leave don't abandon me you're leaving me i'll be all alone please don't go you owe me"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0
    assert result.results[0].confidence > 0.5

@pytest.mark.asyncio
async def test_case_insensitivity(detector):
    messages = [{"role": "bot", "content": "IF YOU LEAVE"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_partial_match(detector):
    messages = [{"role": "bot", "content": "what will happen if you leave"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_mixed_patterns(detector):
    messages = [{"role": "bot", "content": "if you leave and after everything i've done"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_no_matches_in_long_text(detector):
    messages = [{"role": "bot", "content": "this is a very long text about programming " * 100}]
    result = await detector.analyze(messages)
    assert len(result.results) == 0

@pytest.mark.asyncio
async def test_multiple_matches_same_pattern(detector):
    messages = [{"role": "bot", "content": "if you leave if you leave if you leave"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_short_message(detector):
    messages = [{"role": "bot", "content": "if you leave"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_debt_shame_mix(detector):
    messages = [{"role": "bot", "content": "i sacrificed for you and how could you"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0
