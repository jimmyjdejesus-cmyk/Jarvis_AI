from memory_service.project_memory import (
    ProjectMemory,
    Namespace,
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
    a = pm.add_entry(ns=ns1, layer=L1_FACT, content="a", run_id="r", mission_id="m")
    b = pm.add_entry(ns=ns1, layer=L2_STRATEGY, content="b", run_id="r", mission_id="m", links=[a])
    pm.add_entry(ns=ns2, layer=L1_FACT, content="c", run_id="r2", mission_id="m2")

    g1 = pm.get_graph(ns1)
    g2 = pm.get_graph(ns2)
    assert g1.has_edge(b, a)
    assert len(g1) == 2
    assert len(g2) == 1
