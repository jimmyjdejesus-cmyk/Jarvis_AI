from memory_service.project_memory import (
    JSONFileBackend,
    Namespace,
    ProjectMemory,
    L1_FACT,
    L2_STRATEGY,
)


def test_add_and_retrieve_entry():
    pm = ProjectMemory()
    ns = Namespace(project="p", session="s", team="t")
    node_id = pm.add_entry(
        ns=ns,
        layer=L1_FACT,
        content="earth orbits sun",
        run_id="r1",
        mission_id="m1",
    )
    g = pm.get_graph(ns)
    assert node_id in g
    data = g.nodes[node_id]
    assert data["layer"] == L1_FACT
    assert data["run_id"] == "r1"
    assert data["mission_id"] == "m1"


def test_namespace_isolation_and_links():
    pm = ProjectMemory()
    ns1 = Namespace(project="p", session="s1", team="t")
    ns2 = Namespace(project="p", session="s2", team="t")
    a = pm.add_entry(
        ns=ns1,
        layer=L1_FACT,
        content="a",
        run_id="r",
        mission_id="m",
    )
    b = pm.add_entry(
        ns=ns1,
        layer=L2_STRATEGY,
        content="b",
        run_id="r",
        mission_id="m",
        links=[a],
    )
    pm.add_entry(
        ns=ns2,
        layer=L1_FACT,
        content="c",
        run_id="r2",
        mission_id="m2",
    )

    g1 = pm.get_graph(ns1)
    g2 = pm.get_graph(ns2)
    assert g1.has_edge(b, a)
    assert len(g1) == 2
    assert len(g2) == 1


def test_link_to_nonexistent_node_is_ignored():
    pm = ProjectMemory()
    ns = Namespace(project="p", session="s", team="t")
    node_id = pm.add_entry(
        ns=ns,
        layer=L1_FACT,
        content="a",
        run_id="r",
        mission_id="m",
    )
    pm.add_entry(
        ns=ns,
        layer=L2_STRATEGY,
        content="b",
        run_id="r",
        mission_id="m",
        links=["missing"],
    )
    g = pm.get_graph(ns)
    assert not list(g.successors(node_id))


def test_team_namespace_separation():
    pm = ProjectMemory()
    ns1 = Namespace(project="p", session="s", team="t1")
    ns2 = Namespace(project="p", session="s", team="t2")
    pm.add_entry(
        ns=ns1,
        layer=L1_FACT,
        content="a",
        run_id="r1",
        mission_id="m1",
    )
    pm.add_entry(
        ns=ns2,
        layer=L1_FACT,
        content="b",
        run_id="r2",
        mission_id="m2",
    )
    g1 = pm.get_graph(ns1)
    g2 = pm.get_graph(ns2)
    assert len(g1) == 1
    assert len(g2) == 1


def test_invalid_layer_raises_error():
    pm = ProjectMemory()
    ns = Namespace(project="p", session="s", team="t")
    try:
        pm.add_entry(
            ns=ns,
            layer="wrong",
            content="a",
            run_id="r",
            mission_id="m",
        )
    except ValueError as exc:  # noqa: SIM105
        assert "Invalid layer" in str(exc)
    else:  # pragma: no cover
        assert False, "expected ValueError"


def test_missing_provenance_raises_error():
    pm = ProjectMemory()
    ns = Namespace(project="p", session="s", team="t")
    try:
        pm.add_entry(
            ns=ns,
            layer=L1_FACT,
            content="a",
            run_id="",
            mission_id="m",
        )
    except ValueError as exc:  # noqa: SIM105
        assert "run_id and mission_id" in str(exc)
    else:  # pragma: no cover
        assert False, "expected ValueError"


def test_content_is_sanitised():
    pm = ProjectMemory()
    ns = Namespace(project="p", session="s", team="t")
    node_id = pm.add_entry(
        ns=ns,
        layer=L1_FACT,
        content="<script>alert('x')</script> DROP TABLE",
        run_id="r",
        mission_id="m",
    )
    g = pm.get_graph(ns)
    assert "<" not in g.nodes[node_id]["content"]
    assert "script" not in g.nodes[node_id]["content"].lower()


def test_persistence_backend_roundtrip(tmp_path):
    backend_path = tmp_path / "mem.json"
    backend = JSONFileBackend(str(backend_path))
    pm = ProjectMemory(backend=backend)
    ns = Namespace(project="p", session="s", team="t")
    node_id = pm.add_entry(
        ns=ns,
        layer=L1_FACT,
        content="persisted",
        run_id="r",
        mission_id="m",
    )

    pm_loaded = ProjectMemory(backend=backend)
    g = pm_loaded.get_graph(ns)
    assert node_id in g


def test_large_graph_stress():
    pm = ProjectMemory()
    ns = Namespace(project="p", session="s", team="t")
    for i in range(1000):
        pm.add_entry(
            ns=ns,
            layer=L1_FACT,
            content=f"n{i}",
            run_id="r",
            mission_id="m",
        )
    g = pm.get_graph(ns)
    assert len(g) == 1000