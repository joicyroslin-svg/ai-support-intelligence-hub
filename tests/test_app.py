from unittest.mock import MagicMock
import pytest
from assistant.rag import load_csv_to_rag, rag
from assistant.service import bulk_analyze_tickets

def test_load_csv(tmp_path):
    csv_file = tmp_path / 'test.csv'
    csv_file.write_text('ticket_text\\nTest ticket')
    count = load_csv_to_rag(str(csv_file), rag)
    assert count > 0

def test_bulk_analyze_rag_output():
    tickets = [{'ticket': 'test'}]
    results = bulk_analyze_tickets(tickets)
    assert len(results) == 1
    assert 'priority' in results[0]
