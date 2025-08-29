import copy
from concurrent.futures import ThreadPoolExecutor

from jarvis.orchestration.context_utils import filter_team_outputs


def test_filter_team_outputs_missing_team():
    ctx = {"a": 1, "token": "data"}
    result = filter_team_outputs(ctx, {}, "security_quality")
    assert result == ctx and result is not ctx


def test_filter_team_outputs_concurrent_calls():
    ctx = {"shared": 1, "token": "data"}
    team_outputs = {"security_quality": {"token": "data"}}

    def call():
        # use copy to ensure input isn't mutated during threads
        return filter_team_outputs(
            copy.deepcopy(ctx), team_outputs, "security_quality"
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: call(), range(8)))

    for r in results:
        assert "token" not in r
    # original context remains intact
    assert ctx["token"] == "data"
