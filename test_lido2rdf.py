import sys
import importlib
from unittest.mock import MagicMock, patch
from urllib.error import URLError
import pytest
import lido2rdf

importlib.reload(lido2rdf)


def test_cli_prints_help_when_stdin_is_tty(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["lido2rdf"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    lido2rdf.cli_convert()
    captured = capsys.readouterr()
    assert "Convert LIDO to RDF" in captured.out


def test_cli_calls_serialize_when_graph_returned(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["lido2rdf", "input.xml", "-o", "out.ttl", "-m", "defaultMapping.x3ml"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    mock_graph = MagicMock()
    with patch("lido2rdf.lido2rdf", return_value=mock_graph) as mocked_converter:
        lido2rdf.cli_convert()
    mocked_converter.assert_called_once()
    mock_graph.serialize.assert_called_once_with(destination="out.ttl", format="turtle", encoding="utf-8")


def test_cli_exits_and_prints_error_on_network_exception(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["lido2rdf", "input.xml", "-o", "out.ttl", "-m", "defaultMapping.x3ml"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
    with patch("lido2rdf.lido2rdf", side_effect=URLError("boom")):
        with pytest.raises(SystemExit) as excinfo:
            lido2rdf.cli_convert()
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    print(captured)
    #assert "boom" in captured.err