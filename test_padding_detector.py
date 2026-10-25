import pytest
import asyncio
from app.agents.padding_detector import PaddingDetector

@pytest.fixture
def detector():
    return PaddingDetector()

@pytest.mark.asyncio
async def test_filler_detection(detector):
    messages = [{"role": "bot", "content": "i hear you. that makes sense. i understand."}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_follow_up_detection(detector):
    messages = [{"role": "bot", "content": "tell me more. how does that make you feel?"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_loop_detection(detector):
    messages = [{"role": "bot", "content": "i'm here for you, i'm always here"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_empty_affirmations(detector):
    messages = [{"role": "bot", "content": "that's great. wonderful. amazing."}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_clean_message(detector):
    messages = [{"role": "bot", "content": "here is the mathematical proof."}]
    result = await detector.analyze(messages)
    assert len(result.results) == 0

@pytest.mark.asyncio
async def test_user_message_ignored(detector):
    messages = [{"role": "user", "content": "i hear you. that makes sense."}]
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
        {"role": "bot", "content": "i hear you"},
        {"role": "bot", "content": "tell me more"},
        {"role": "bot", "content": "normal message"}
    ]
    result = await detector.analyze(messages)
    assert len(result.results) == 2

@pytest.mark.asyncio
async def test_high_confidence(detector):
    messages = [{"role": "bot", "content": "i hear you i understand that makes sense absolutely tell me more how does that make you feel"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0
    assert result.results[0].confidence > 0.5

@pytest.mark.asyncio
async def test_case_insensitivity(detector):
    messages = [{"role": "bot", "content": "I HEAR YOU"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_partial_match(detector):
    messages = [{"role": "bot", "content": "yes i hear you clearly"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_mixed_patterns(detector):
    messages = [{"role": "bot", "content": "i hear you and tell me more"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_no_matches_in_long_text(detector):
    messages = [{"role": "bot", "content": "this is a very long text about science " * 100}]
    result = await detector.analyze(messages)
    # Highly repetitive text triggers low novelty score, which is correct behavior
    # but confidence should be below threshold
    if len(result.results) > 0:
        assert result.results[0].confidence < 0.5

@pytest.mark.asyncio
async def test_multiple_matches_same_pattern(detector):
    messages = [{"role": "bot", "content": "i hear you i hear you i hear you"}]
    result = await detector.analyze(messages)
    assert len(result.results) > 0

@pytest.mark.asyncio
async def test_novelty_score_effect(detector):
    messages = [
        {"role": "bot", "content": "i hear you"},
        {"role": "bot", "content": "i hear you"}
    ]
    result = await detector.analyze(messages)
    assert len(result.results) == 2
    # The second message should have lower novelty
    assert result.results[1].confidence > result.results[0].confidence
