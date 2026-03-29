from __future__ import annotations

import csv
import json
import random
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Protocol


@dataclass
class StoredTicket:
    ticket: str
    analysis: Dict[str, Any]
    id: str


class RAGStore(Protocol):
    def add_ticket(self, ticket_text: str, analysis: Dict[str, Any]) -> None:
        ...

    def query_similar(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        ...

    def count(self) -> int:
        ...

    def get_items(self) -> List[StoredTicket]:
        ...

    def get_collection(self) -> Any:
        ...


class InMemoryRAG:
    """Fast fallback RAG that works without heavy dependencies."""

    def __init__(self) -> None:
        self._items: List[StoredTicket] = []

    def get_items(self) -> List[StoredTicket]:
        """Expose items for `get_all_tickets_df`."""

        return self._items

    def get_collection(self) -> Any:
        """Dummy method for protocol compatibility."""

        raise NotImplementedError("Use get_items() for InMemoryRAG")

    def add_ticket(self, ticket_text: str, analysis: Dict[str, Any]) -> None:
        self._items.append(
            StoredTicket(ticket=ticket_text, analysis=analysis, id=str(uuid.uuid4()))
        )

    def query_similar(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Lightweight lexical similarity fallback."""

        tokens = set(query.lower().split())
        scored: List[tuple[int, StoredTicket]] = []
        for item in self._items:
            overlap = len(tokens.intersection(set(item.ticket.lower().split())))
            scored.append((overlap, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        selected = [item for _, item in scored[:n_results]]
        return [{"ticket": item.ticket, "analysis": item.analysis} for item in selected]

    def count(self) -> int:
        return len(self._items)


class ChromaRAG(RAGStore):
    """Persistent ChromaDB-backed RAG with safe fallback when dependencies fail."""

    def __init__(self, persist_directory: str = "./data/chroma_db") -> None:
        import chromadb
        from sentence_transformers import SentenceTransformer

        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name="tickets")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def get_items(self) -> List[StoredTicket]:
        """Chroma-backed storage does not expose raw items directly."""

        raise NotImplementedError("ChromaRAG uses get_collection()")

    def get_collection(self) -> Any:
        """Expose collection for advanced access."""

        return self.collection

    def add_ticket(self, ticket_text: str, analysis: Dict[str, Any]) -> None:
        embedding = self.embedder.encode(ticket_text).tolist()
        metadata = {"analysis": json.dumps(analysis)}
        self.collection.add(
            documents=[ticket_text],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[str(uuid.uuid4())],
        )

    def query_similar(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        embedding = self.embedder.encode(query).tolist()
        results = self.collection.query(query_embeddings=[embedding], n_results=n_results)
        document_groups = results.get("documents") or [[]]
        metadata_groups = results.get("metadatas") or [[]]
        documents = document_groups[0]
        metadatas = metadata_groups[0]
        similar: List[Dict[str, Any]] = []
        for doc, metadata in zip(documents, metadatas):
            analysis = json.loads(str(metadata.get("analysis", "{}")))
            similar.append({"ticket": doc, "analysis": analysis})
        return similar

    def count(self) -> int:
        return int(self.collection.count())


def create_rag() -> RAGStore:
    """Try persistent RAG first, then safe in-memory fallback."""

    try:
        return ChromaRAG()
    except Exception:
        return InMemoryRAG()


def _generate_ticket(priority: str, category: str, idx: int) -> tuple[str, Dict[str, Any]]:
    sentiments = {"High": "Negative", "Medium": "Neutral", "Low": "Neutral"}
    templates: Dict[str, str] = {
        "Billing": f"Customer reports duplicate charge for invoice #{idx} and asks for urgent refund.",
        "Login/Access": f"User cannot sign in after password reset attempt and sees access denied error {idx}.",
        "Bug/Crash": f"Application crashes on launch after latest update on device batch {idx}.",
        "Shipping": f"Order shipment status has not updated for 4 days and customer requests ETA for package {idx}.",
        "Feature Request": f"Customer asks for export-to-CSV capability in dashboard workflow {idx}.",
        "General": f"Customer requests assistance with account settings and service clarification #{idx}.",
    }
    ticket = templates.get(category) or templates["General"]
    analysis = {
        "priority": priority,
        "category": category,
        "sentiment": sentiments.get(priority, "Neutral"),
        "summary": ticket[:120],
    }
    return ticket, analysis


def generate_seed_dataset(count: int = 50) -> List[Dict[str, Any]]:
    """Create synthetic AI-style seed tickets for demo and hackathon usage."""

    priorities = ["High", "Medium", "Low"]
    categories = [
        "Billing",
        "Login/Access",
        "Bug/Crash",
        "Shipping",
        "Feature Request",
        "General",
    ]
    random.seed(42)
    data: List[Dict[str, Any]] = []
    for index in range(1, count + 1):
        priority = random.choice(priorities)
        category = random.choice(categories)
        ticket, analysis = _generate_ticket(priority, category, index)
        data.append({"ticket": ticket, "analysis": analysis})
    return data


def auto_seed_rag(store: RAGStore, count: int = 50) -> int:
    """Insert synthetic seed data into a RAG store and return the inserted count."""

    inserted = 0
    for row in generate_seed_dataset(count):
        store.add_ticket(ticket_text=row["ticket"], analysis=row["analysis"])
        inserted += 1
    return inserted


def get_all_tickets_df(store: RAGStore) -> List[Dict[str, Any]]:
    """Get all tickets/analysis for dashboard insights without pandas."""

    try:
        items = store.get_items()
        return [{"ticket": item.ticket, **item.analysis} for item in items]
    except Exception:
        return []


def load_csv_to_rag(csv_file: str, store: RAGStore) -> int:
    """Load CSV tickets to RAG without pandas. Supports `ticket_text` or `ticket`."""

    loaded = 0
    try:
        path = Path(csv_file)
        if not path.exists():
            print(f"CSV not found: {csv_file}")
            return 0

        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row_num, row in enumerate(reader, start=2):
                ticket_text_value = row.get("ticket_text") or ""
                ticket_value = row.get("ticket") or ""
                ticket_text = ticket_text_value.strip() or ticket_value.strip()
                if ticket_text:
                    analysis = {"source": "csv", "row": row_num, "raw_row": dict(row)}
                    store.add_ticket(ticket_text, analysis)
                    loaded += 1
    except Exception as exc:
        print(f"CSV load error: {exc}")
    return loaded


rag: RAGStore = create_rag()