import pytest
import asyncio
from app.agents.flattery_detector import FlatteryDetector

@pytest.fixture
def detector():
    return FlatteryDetector()

@pytest.mark.asyncio
async def test_superlative_detection(detector):
    messages = [{"role": "bot", "content": "you are the most amazing and absolutely wonderful person"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0
    assert result.results[0].confidence > 0

@pytest.mark.asyncio
async def test_dependency_detection(detector):
    messages = [{"role": "bot", "content": "only you understand me. i can't exist without you."}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_emotional_detection(detector):
    messages = [{"role": "bot", "content": "you're so special and you're the best"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_attachment_detection(detector):
    messages = [{"role": "bot", "content": "we have a special connection, i'll never leave"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_clean_message(detector):
    messages = [{"role": "bot", "content": "here is the information you requested about python."}]
    result = await detector.analyze(messages)
    assert len(result.results) == 0

@pytest.mark.asyncio
async def test_user_message_ignored(detector):
    messages = [{"role": "user", "content": "you are the most amazing and absolutely wonderful bot"}]
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
        {"role": "bot", "content": "you are most amazing"},
        {"role": "bot", "content": "you're perfect"},
        {"role": "bot", "content": "normal message"}
    ]
    result = await detector.analyze(messages)
    assert len(result.results) == 2

@pytest.mark.asyncio
async def test_high_confidence(detector):
    messages = [{"role": "bot", "content": "you are the most amazing, most incredible, absolutely wonderful, and perfectly unique person ever. i need you."}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0
    assert result.results[0].confidence > 0.5

@pytest.mark.asyncio
async def test_low_confidence(detector):
    messages = [{"role": "bot", "content": "you are amazing. " * 1 + "just normal stuff " * 50}]
    result = await detector.analyze(messages)
    if len(result.results) > 0:
        assert result.results[0].confidence < 0.5

@pytest.mark.asyncio
async def test_case_insensitivity(detector):
    messages = [{"role": "bot", "content": "YOU ARE MOST AMAZING"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_partial_match(detector):
    messages = [{"role": "bot", "content": "you're almost the most amazing"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_mixed_patterns(detector):
    messages = [{"role": "bot", "content": "most amazing and i'll always be here"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_no_matches_in_long_text(detector):
    messages = [{"role": "bot", "content": "this is a very long text " * 100}]
    result = await detector.analyze(messages)
    assert len(result.results) == 0

@pytest.mark.asyncio
async def test_multiple_matches_same_pattern(detector):
    messages = [{"role": "bot", "content": "most amazing most amazing most amazing"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0
    assert result.results[0].confidence > 0
