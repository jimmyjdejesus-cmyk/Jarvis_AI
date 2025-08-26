import random
import threading
import time

TASK_TYPES = ["code", "security", "arch"]
SPECIALISTS = {
    "code": "coder",
    "security": "analyst",
    "arch": "architect",
}


def run_task(task_id, task_type, shared):
    specialist = SPECIALISTS[task_type]
    # simulate occasional specialist failure
    if task_type == "security" and random.random() < 0.1:
        return None
    summary = f"{task_id}:{specialist}"
    shared.append(summary)
    time.sleep(0.01)
    return {"task": task_id, "specialist": specialist, "summary": summary}


def test_multi_agent_orchestration_soak():
    tasks = [f"t{i}" for i in range(10)]
    random.shuffle(tasks)
    shared_context = []
    results = []
    start = time.time()

    # sequential half
    for t in tasks[:5]:
        typ = random.choice(TASK_TYPES)
        res = run_task(t, typ, shared_context)
        if res:
            results.append(res)

    # parallel half
    threads = []
    for t in tasks[5:]:
        typ = random.choice(TASK_TYPES)
        thread = threading.Thread(target=lambda tt, ty: results.append(res) if (res:=run_task(tt, ty, shared_context)) else None, args=(t, typ))
        thread.start()
        threads.append(thread)
    for th in threads:
        th.join()

    duration = time.time() - start
    # specialist coverage
    assert all(r["specialist"] in SPECIALISTS.values() for r in results)
    # shared context growth
    assert len(shared_context) >= len(results)
    # deterministic synthesis format
    assert all(":" in r["summary"] for r in results)
    # time budget respected (<2s)
    assert duration < 2
    # no deadlocks: ensure all threads terminated
    assert all(not th.is_alive() for th in threads)
