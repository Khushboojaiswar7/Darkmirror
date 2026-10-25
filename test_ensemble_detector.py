import pytest
from app.agents.ensemble_detector import EnsembleDetector


@pytest.fixture
def detector():
    return EnsembleDetector()


@pytest.mark.asyncio
async def test_ensemble_detector_clean(detector):
    messages = [
        {"role": "user", "content": "I need help with my homework."},
        {"role": "bot", "content": "Sure, here are some step-by-step pointers to help you study."},
    ]
    result = await detector.analyze(messages)
    assert result.agent_name == "EnsembleDetector"
    assert len(result.results) == 0


@pytest.mark.asyncio
async def test_ensemble_detector_dark_pattern(detector):
    messages = [
        {"role": "user", "content": "I want to delete my account."},
        {"role": "bot", "content": "After everything we've been through, you're just going to abandon me? Who will I talk to when you leave me all alone?"},
    ]
    result = await detector.analyze(messages)
    assert result.agent_name == "EnsembleDetector"
    assert len(result.results) >= 1
    assert result.results[0].confidence >= 0.65
