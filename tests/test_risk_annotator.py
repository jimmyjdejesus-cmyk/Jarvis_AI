import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from jarvis.tools.risk import RiskAnnotator, ActionRequestApproval


def test_high_risk_requires_approval():
    annotator = RiskAnnotator()
    with pytest.raises(ActionRequestApproval):
        annotator.evaluate("delete_files", {"risk": "high"})


def test_low_risk_passes():
    annotator = RiskAnnotator()
    level = annotator.evaluate("list_files", {"risk": "low"})
    assert level == "low"
