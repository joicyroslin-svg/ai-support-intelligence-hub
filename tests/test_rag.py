from __future__ import annotations

from assistant.rag import InMemoryRAG, auto_seed_rag, generate_seed_dataset


def test_in_memory_rag_roundtrip() -> None:
    store = InMemoryRAG()
    store.add_ticket("payment failed during checkout", {"priority": "High"})
    store.add_ticket("order delayed and tracking not updated", {"priority": "Medium"})

    results = store.query_similar("payment issue", n_results=1)

    assert len(results) == 1
    assert "payment" in results[0]["ticket"].lower()
    assert store.count() == 2


def test_generate_seed_dataset_shape() -> None:
    rows = generate_seed_dataset(count=7)
    assert len(rows) == 7
    assert "ticket" in rows[0]
    assert "analysis" in rows[0]


def test_auto_seed_rag_count() -> None:
    store = InMemoryRAG()
    inserted = auto_seed_rag(store, count=12)
    assert inserted == 12
    assert store.count() == 12
