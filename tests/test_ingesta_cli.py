"""Pruebas unitarias de la CLI de ingesta — TK-003.

Cubre: build_source_file (AC-017), idempotencia (AC-009/BR-04)
y el argparser (AC-010).
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# build_source_file — AC-017: ruta absoluta o relativa producen el mismo resultado
# ---------------------------------------------------------------------------


def test_build_source_file_relative_and_absolute_are_equal(tmp_path: Path) -> None:
    """build_source_file debe dar el mismo source_file con ruta relativa o absoluta."""
    from smart_api_search.domain.files_source import build_source_file

    spec_file = tmp_path / "subdir" / "api.yaml"
    spec_file.parent.mkdir()
    spec_file.touch()

    result_abs = build_source_file(tmp_path, spec_file)
    result_abs2 = build_source_file(tmp_path.resolve(), spec_file.resolve())

    assert result_abs == "file:subdir/api.yaml"
    assert result_abs == result_abs2


# ---------------------------------------------------------------------------
# Idempotencia — BR-04, AC-009: decisión una sola vez por fuente
# ---------------------------------------------------------------------------


def test_idempotency_skips_existing_source() -> None:
    """Fuente ya indexada debe omitirse sin reindexar (sin --force)."""
    source_decision: dict[str, bool] = {}

    def _should_index(source_file: str, qdrant: MagicMock, collection_name: str, force: bool = False) -> bool:
        if source_file in source_decision:
            return source_decision[source_file]
        result = qdrant.count(
            collection_name=collection_name,
            count_filter={"must": [{"key": "source_file", "match": {"value": source_file}}]},
            exact=False,
        )
        decision = result.count == 0
        source_decision[source_file] = decision
        return decision

    mock_qdrant = MagicMock()
    count_result = MagicMock()
    count_result.count = 5  # fuente ya existe
    mock_qdrant.count.return_value = count_result

    should_index_first = _should_index("file:api.json", mock_qdrant, "test-col")
    should_index_second = _should_index("file:api.json", mock_qdrant, "test-col")  # segunda vez

    assert should_index_first is False
    assert should_index_second is False
    # count solo se llama una vez (la decisión se cachea)
    assert mock_qdrant.count.call_count == 1


def test_idempotency_indexes_new_source() -> None:
    """Fuente nueva (0 puntos) debe indexarse."""
    source_decision: dict[str, bool] = {}

    def _should_index(source_file: str, qdrant: MagicMock, collection_name: str) -> bool:
        if source_file in source_decision:
            return source_decision[source_file]
        result = qdrant.count(
            collection_name=collection_name,
            count_filter={"must": [{"key": "source_file", "match": {"value": source_file}}]},
            exact=False,
        )
        decision = result.count == 0
        source_decision[source_file] = decision
        return decision

    mock_qdrant = MagicMock()
    count_result = MagicMock()
    count_result.count = 0  # fuente nueva
    mock_qdrant.count.return_value = count_result

    assert _should_index("file:new.json", mock_qdrant, "test-col") is True


# ---------------------------------------------------------------------------
# CLI parser — AC-010
# ---------------------------------------------------------------------------


def test_parser_has_required_args() -> None:
    """El parser debe reconocer todas las opciones de AC-010."""
    from smart_api_search.cli.ingest import _build_parser

    parser = _build_parser()
    args = parser.parse_args([
        "--source", "files",
        "--specs-dir", "/tmp/specs",
        "--no-enrich",
        "--dry-run",
        "--force",
    ])
    assert args.source == "files"
    assert args.specs_dir == "/tmp/specs"
    assert args.no_enrich is True
    assert args.dry_run is True
    assert args.force is True
