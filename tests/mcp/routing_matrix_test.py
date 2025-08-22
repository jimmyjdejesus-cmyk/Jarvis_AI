import logging
from contextlib import contextmanager

ROUTING_TABLE = {
    "code": "gpt-4",
    "security": "claude",
    "arch": "local",
}


@contextmanager
def capture_logs():
    logger = logging.getLogger("mcp")
    handler = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    records = []
    handler.emit = lambda record: records.append(handler.format(record))
    try:
        yield records
    finally:
        logger.removeHandler(handler)


def route(task_type, text, fail=False):
    model = ROUTING_TABLE[task_type]
    logger = logging.getLogger("mcp")
    logger.debug(f"route {task_type} -> {model}")
    if fail and model != "local":
        logger.debug("remote failure, falling back to local")
        return "local"
    return model


def test_routing_matrix_with_fallback():
    with capture_logs() as logs:
        for task, model in ROUTING_TABLE.items():
            chosen = route(task, "test")
            assert chosen == model
        # force a failure and ensure fallback
        chosen = route("code", "fail", fail=True)
        assert chosen == "local"
    # explainability in logs
    assert any("route code -> gpt-4" in line for line in logs)
    assert any("remote failure" in line for line in logs)
