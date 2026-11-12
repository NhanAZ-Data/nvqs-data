from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup
from pypdf import PdfReader


ANCHOR_PATTERNS = [
    ("chapter", re.compile(r"^\s*(CHƯƠNG\s+.+)$", re.IGNORECASE)),
    ("section", re.compile(r"^\s*(Mục\s+.+)$", re.IGNORECASE)),
    ("article", re.compile(r"^\s*(Điều\s+\d+[A-Za-zĐđ]*\s*[:.]?.*)$", re.IGNORECASE)),
    ("appendix", re.compile(r"^\s*(PHỤ LỤC\s+.+)$", re.IGNORECASE)),
    ("form", re.compile(r"^\s*(Mẫu\s+\d+[A-Za-zĐđ]*\s*[:.]?.*)$", re.IGNORECASE)),
]

DOC_EXTRACTOR = Path(__file__).with_name("extract_online_doc.ps1")

NORMALIZATION_PROFILE = "vi-legal-v2"
NAVIGATION_LINES = {
    "Lời mở đầu",
    "Tab mới ↗",
    "Sơ đồ",
    "Hỏi AI",
    "Hỏi Tú Vân về văn bản này",
    "Mục lục",
    "Tìm",
    "Đầu",
    "Theo dõi…",
    "Theo dõi...",
    "Tải về",
    "Bản gốc",
    "Lược đồ",
    "Lịch sử hiệu lực",
    "VB liên quan",
    "Chia sẻ",
    "In",
    "Góp ý",
    "Dạng thẻ",
    "Tờ văn bản",
    "Ghi chú & diễn giải",
    "Nguyên văn",
    "Toàn văn",
    "Từng phần",
    "Trích dẫn",
    "A−",
    "A+",
    "Đọc / Tạm dừng",
    "Cấu hình giọng",
    "Đọc tập trung",
    "Yêu cầu qua Zalo",
    "🎙️ Chọn giọng đọc:",
    "⚡ Tốc độ đọc:",
}
TRAILING_MARKERS = {
    "BÀI VIẾT CÙNG CHỦ ĐỀ:",
    "BÀI VIẾT LIÊN QUAN:",
    "Đang tải...",
    "ĐANG TẢI...",
}
OFFICIAL_HEADER_LINES = {
    "QUỐC HỘI",
    "CHÍNH PHỦ",
    "BỘ QUỐC PHÒNG",
    "BỘ CÔNG AN",
    "VĂN PHÒNG QUỐC HỘI",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFC", value)
    value = (
        value.replace("\u00a0", " ")
        .replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
        .replace("\ufeff", "")
        .replace("\x00", "")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )
    value = re.sub(
        r"\s*[-|]\s*(?=CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM)",
        "\n",
        value,
    )
    value = re.sub(
        r"(CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM)\s+(Độc lập - Tự do - Hạnh phúc)",
        r"\1\n\2",
        value,
    )
    value = re.sub(r"(Số:[^\n|]+)\s*\|\s*(Hà Nội,)", r"\1\n\2", value)
    value = re.sub(r"\bn\s*\n\s*gày\b", "ngày", value, flags=re.IGNORECASE)
    value = "".join(char if char in "\n\t" or ord(char) >= 32 else "" for char in value)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in value.split("\n")]
    lines = [
        re.sub(r"(?<=\d)\s+(?=\d)", "", line)
        if ("ngày" in line.lower() or "năm" in line.lower())
        else line
        for line in lines
    ]
    lines = [
        "| --- | --- | --- | --- | --- | --- |" if line == "|||||||" else line
        for line in lines
    ]
    deduplicated: list[str] = []
    for line in lines:
        if line and deduplicated and deduplicated[-1] == line:
            continue
        deduplicated.append(line)
    lines = deduplicated
    result: list[str] = []
    blank_count = 0
    for line in lines:
        if line.strip():
            blank_count = 0
            result.append(line)
        else:
            blank_count += 1
            if blank_count <= 1:
                result.append("")
    return "\n".join(result).strip()


def is_official_header_line(line: str) -> bool:
    upper = line.upper().strip()
    if upper in OFFICIAL_HEADER_LINES:
        return True
    return (
        "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" in upper
        and any(marker in upper for marker in ("QUỐC HỘI", "CHÍNH PHỦ", "BỘ QUỐC PHÒNG", "BỘ CÔNG AN"))
    )


def normalize_online_legal_text(value: str) -> str:
    """Remove common website chrome while retaining the legal document body."""
    text = normalize_text(value)
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line in NAVIGATION_LINES:
            continue
        if re.fullmatch(r"Điều\s+\d+[A-Za-zĐđ]*", line, re.IGNORECASE):
            continue
        if re.fullmatch(r"Chương\s+[IVXLCDM]+\s+—.*", line, re.IGNORECASE):
            continue
        if re.fullmatch(r"Mục\s+\d+", line, re.IGNORECASE):
            continue
        lines.append(line)

    # Secondary legal databases often put status/navigation before the actual
    # header. The agent corpus stores that metadata separately, so start at the
    # first recognizable official header when one exists.
    for index, line in enumerate(lines):
        context = " ".join(lines[index : index + 8]).upper()
        has_document_header_context = (
            "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" in context
            or "SỐ:" in context
            or "THÔNG TƯ" in context
            or "NGHỊ ĐỊNH" in context
            or "LUẬT" in context
        )
        if is_official_header_line(line) and has_document_header_context:
            lines = lines[index:]
            break

    for index, line in enumerate(lines):
        if line in TRAILING_MARKERS:
            lines = lines[:index]
            break

    return normalize_text("\n".join(lines))


def flatten_documents(manifest: dict) -> list[dict]:
    documents = list(manifest.get("documents") or [])
    additional = manifest.get("additional_documents") or {}
    documents.extend(additional.get("documents") or [])
    if not documents:
        raise ValueError("MANIFEST.yaml does not contain documents")
    return documents


def extract_pdf(pdf_path: Path) -> tuple[list[str], str]:
    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    errors: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            pages.append(normalize_text(page.extract_text() or ""))
        except Exception as exc:
            pages.append("")
            errors.append(f"page {page_number}: {type(exc).__name__}: {exc}")
    return pages, "; ".join(errors)


def extract_online_text(url: str, selector: str, min_chars: int) -> tuple[str | None, str]:
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; NVQS-Agent-Corpus/1.0)"},
            timeout=30,
        )
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup.select("script, style, noscript, header, footer, nav, form, aside"):
            tag.decompose()
        target = soup.select_one(selector) if selector else soup.body
        if target is None:
            return None, f"selector_not_found: {selector}"
        text = normalize_online_legal_text(target.get_text("\n"))
        if len(text) < min_chars:
            return None, f"text_too_short: {len(text)} < {min_chars}"
        return text, ""
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def extract_online_doc(url: str, min_chars: int) -> tuple[str | None, str]:
    """Read an official legacy .doc using the installed Microsoft Word COM reader."""
    if not DOC_EXTRACTOR.is_file():
        return None, f"missing_doc_extractor: {DOC_EXTRACTOR}"
    try:
        completed = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(DOC_EXTRACTOR),
                url,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            check=False,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip()
            return None, f"doc_reader_exit_{completed.returncode}: {detail[:500]}"
        text = normalize_online_legal_text(completed.stdout)
        if len(text) < min_chars:
            return None, f"text_too_short: {len(text)} < {min_chars}"
        return text, ""
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def extract_online_source(
    url: str, selector: str, min_chars: int, source_format: str | None
) -> tuple[str | None, str, str]:
    if source_format in {"doc", "docx", "msword", "word"}:
        text, error = extract_online_doc(url, min_chars)
        return text, error, "Microsoft Word COM .doc reader"
    text, error = extract_online_text(url, selector, min_chars)
    return text, error, f"BeautifulSoup.select({selector!r})"


def make_unit_id(document_id: str, source_kind: str, unit_index: int) -> str:
    return f"{document_id}:{source_kind}:{unit_index:04d}"


def find_anchors(
    document_id: str, document_index: int, pages: list[str], source_kind: str
) -> list[dict]:
    anchors: list[dict] = []
    for unit_index, page_text in enumerate(pages, start=1):
        unit_id = make_unit_id(document_id, source_kind, unit_index)
        for line_number, line in enumerate(page_text.splitlines(), start=1):
            candidate = " ".join(line.split())
            if not candidate:
                continue
            for anchor_type, pattern in ANCHOR_PATTERNS:
                match = pattern.match(candidate)
                if match:
                    anchors.append(
                        {
                            "schema_version": 2,
                            "record_type": "anchor",
                            "anchor_id": f"{unit_id}:line-{line_number:05d}",
                            "document_index": document_index,
                            "document_id": document_id,
                            "unit_id": unit_id,
                            "unit_index": unit_index,
                            "page_number": unit_index if source_kind == "pdf_extraction" else None,
                            "source_kind": source_kind,
                            "line_number": line_number,
                            "anchor_type": anchor_type,
                            "heading": match.group(1).strip(),
                        }
                    )
                    break
    return anchors


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
            stream.write("\n")


def quote_yaml(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def write_index_yaml(path: Path, metadata: list[dict], generated_at: str) -> None:
    lines = [
        "corpus_type: nvqs_agent_corpus",
        "schema_version: 2",
        f"generated_at: {quote_yaml(generated_at)}",
        "language: vi",
        "topic: nghĩa vụ quân sự Việt Nam",
        f"normalization_profile: {quote_yaml(NORMALIZATION_PROFILE)}",
        "source_manifest: ../van-ban-nguon/MANIFEST.yaml",
        "source_directory: ../van-ban-nguon",
        "artifacts:",
        "  documents_jsonl: documents.jsonl",
        "  pages_jsonl: pages.jsonl",
        "  anchors_jsonl: anchors.jsonl",
        "  schema_json: schema.json",
        "  text_directory: text/",
        "  reader_text_directory: ../van-ban-md/",
        "documents:",
    ]
    for item in metadata:
        lines.append(f"  - document_index: {quote_yaml(item['document_index'])}")
        lines.append(f"    id: {quote_yaml(item['id'])}")
        for key in (
            "identifier",
            "title",
            "source_pdf",
            "text_file",
            "reader_text_file",
            "pdf_declared_page_count",
            "pdf_page_count",
            "text_unit_count",
            "text_char_count",
            "nonempty_text_units",
            "text_source",
            "text_source_tier",
            "quality_status",
            "text_normalization_profile",
            "source_provenance",
        ):
            if key in item:
                lines.append(f"    {key}: {quote_yaml(item[key])}")
        lines.append(f"    source_page: {quote_yaml(item.get('source_pdf_page'))}")
        lines.append(f"    download_url: {quote_yaml(item.get('source_pdf_download_url'))}")
        lines.append(f"    text_source_url: {quote_yaml(item.get('text_source_url'))}")
        lines.append(f"    text_source_page: {quote_yaml(item.get('text_source_page'))}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a machine-readable corpus from NVQS PDFs")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--online-sources", type=Path, required=False)
    parser.add_argument(
        "--reader-output",
        type=Path,
        required=False,
        help="Directory for reader-facing Markdown copies (defaults to a sibling van-ban-md directory)",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    manifest_path = args.manifest.resolve()
    output = args.output.resolve()
    reader_output = (
        args.reader_output.resolve()
        if args.reader_output
        else output.parent / "van-ban-md"
    )
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    documents = flatten_documents(manifest)
    online_config = {}
    if args.online_sources:
        online_payload = yaml.safe_load(args.online_sources.resolve().read_text(encoding="utf-8")) or {}
        online_config = online_payload.get("sources") or {}

    text_dir = output / "text"
    text_dir.mkdir(parents=True, exist_ok=True)
    reader_output.mkdir(parents=True, exist_ok=True)
    metadata: list[dict] = []
    pages_jsonl: list[dict] = []
    anchors: list[dict] = []
    generated_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    for document_index, document in enumerate(documents, start=1):
        document_id = document["id"]
        filename = document["filename"]
        pdf_path = root / filename
        if not pdf_path.is_file():
            raise FileNotFoundError(f"Missing PDF for {document_id}: {pdf_path}")

        actual_bytes = pdf_path.stat().st_size
        actual_sha256 = sha256_file(pdf_path)
        pdf_reader = PdfReader(str(pdf_path))
        actual_pdf_pages = len(pdf_reader.pages)

        online_source = online_config.get(document_id) or {}
        online_text = None
        online_error = None
        online_method = None
        if online_source.get("url"):
            online_text, online_error, online_method = extract_online_source(
                online_source["url"],
                online_source.get("selector", "body"),
                int(online_source.get("min_chars", 1000)),
                online_source.get("format"),
            )

        if online_text:
            pages = [online_text]
            text_source = "online_doc" if online_source.get("format") else "online_html"
            extraction_method = online_method or f"BeautifulSoup.select({online_source.get('selector', 'body')!r})"
            extraction_error = None
            status = "ok"
            source_kind = text_source
            text_unit_label = "Online full text"
        else:
            pages, extraction_error = extract_pdf(pdf_path)
            text_source = "pdf_extraction"
            extraction_method = "pypdf.page.extract_text"
            source_kind = "pdf_extraction"
            text_unit_label = "PDF page"

        text_chars = sum(len(page) for page in pages)
        nonempty_pages = sum(bool(page.strip()) for page in pages)
        if text_source.startswith("online_"):
            status = "ok"
        elif nonempty_pages == 0:
            status = "empty_or_image_only"
            extraction_error = extraction_error or "all_pages_empty_or_image_only"
        elif nonempty_pages <= 1 and text_chars < 1000:
            status = "partial_or_image_only"
            extraction_error = extraction_error or "only_signature_or_sparse_text_extracted"
        elif extraction_error:
            status = "page_extraction_warning"
        else:
            status = "ok"
        text_file = f"text/{document_id}.md"
        reader_text_filename = f"{Path(filename).stem}.md"
        reader_text_file = f"../van-ban-md/{reader_text_filename}"
        corpus_pdf_relative = f"../van-ban-nguon/{filename}"
        reader_pdf_relative = f"../van-ban-nguon/{filename}"

        manifest_match = {
            "page_count": document.get("pages") == actual_pdf_pages,
            "byte_count": document.get("bytes") == actual_bytes,
            "sha256": str(document.get("sha256", "")).upper() == actual_sha256,
        }
        manifest_match["all"] = all(manifest_match.values())
        item = {
            "schema_version": 2,
            "record_type": "document",
            "document_index": document_index,
            "id": document_id,
            "identifier": document.get("identifier"),
            "title": document.get("title"),
            "source_pdf": corpus_pdf_relative,
            "source_pdf_filename": filename,
            "source_pdf_page": document.get("source_page"),
            "source_pdf_download_url": document.get("download_url"),
            "pdf_declared_page_count": document.get("pages"),
            "pdf_page_count": actual_pdf_pages,
            "pdf_declared_byte_count": document.get("bytes"),
            "pdf_byte_count": actual_bytes,
            "pdf_declared_sha256": str(document.get("sha256", "")).upper(),
            "pdf_sha256": actual_sha256,
            "pdf_manifest_match": manifest_match,
            "text_file": text_file,
            "reader_text_file": reader_text_file,
            "text_source": text_source,
            "text_source_url": online_source.get("url"),
            "text_source_page": online_source.get("source_page"),
            "text_source_tier": online_source.get("source_tier"),
            "text_extraction_method": extraction_method,
            "text_normalization_profile": NORMALIZATION_PROFILE,
            "text_unit_count": len(pages),
            "text_char_count": text_chars,
            "nonempty_text_units": nonempty_pages,
            "quality_status": status,
            "quality_warning": extraction_error or None,
            "online_fetch_error": online_error or None,
            "source_provenance": document.get("provenance", "official_or_manifest_source"),
            "source_note": document.get("source_note"),
        }
        metadata.append(item)

        header = {
            "schema_version": 2,
            "record_type": "text_document",
            "document_index": document_index,
            "document_id": document_id,
            "title": document.get("title"),
            "identifier": document.get("identifier"),
            "source_pdf": corpus_pdf_relative,
            "source_pdf_page": document.get("source_page"),
            "pdf_sha256": actual_sha256,
            "text_source": text_source,
            "text_source_url": online_source.get("url"),
            "text_source_page": online_source.get("source_page"),
            "text_extraction_method": extraction_method,
            "text_normalization_profile": NORMALIZATION_PROFILE,
            "quality_status": status,
        }
        md_parts = [
            "<!-- agent-metadata: " + json.dumps(header, ensure_ascii=False) + " -->",
            "",
            f"# {document.get('title') or document_id}",
            "",
            f"- Mã: `{document_id}`",
            f"- Số hiệu: `{document.get('identifier') or ''}`",
            f"- PDF gốc: `{corpus_pdf_relative}`",
            f"- SHA-256 PDF: `{actual_sha256}`",
            f"- Nguồn text: `{text_source}`",
            f"- Chuẩn hóa: `{NORMALIZATION_PROFILE}`",
        ]
        if document.get("source_note"):
            md_parts.append(f"- Ghi chú nguồn: {document['source_note']}")
        if status != "ok":
            md_parts.append(f"- Trạng thái trích xuất: `{status}`")
        if extraction_error:
            md_parts.append(f"- Cảnh báo trích xuất: {extraction_error}")
        md_parts.extend(
            [
                "",
                f"> Bản text này lấy từ {text_source}. Khi cần kiểm tra chữ ký, dấu, bảng hoặc bố cục hình ảnh, mở PDF gốc.",
                "",
            ]
        )

        for unit_number, page_text in enumerate(pages, start=1):
            unit_id = make_unit_id(document_id, source_kind, unit_number)
            heading = f"## {text_unit_label} {unit_number:04d}" if source_kind == "pdf_extraction" else f"## {text_unit_label}"
            md_parts.extend([heading, "", page_text or "[EMPTY_OR_IMAGE_ONLY_PAGE]", ""])
            pages_jsonl.append(
                {
                    "schema_version": 2,
                    "record_type": "text_unit",
                    "document_index": document_index,
                    "document_id": document_id,
                    "identifier": document.get("identifier"),
                    "unit_id": unit_id,
                    "unit_index": unit_number,
                    "page_number": unit_number if source_kind == "pdf_extraction" else None,
                    "source_kind": source_kind,
                    "text_source_url": online_source.get("url"),
                    "text_normalization_profile": NORMALIZATION_PROFILE,
                    "text": page_text,
                    "char_count": len(page_text),
                    "is_empty": not bool(page_text),
                }
            )
        (output / text_file).parent.mkdir(parents=True, exist_ok=True)
        (output / text_file).write_text("\n".join(md_parts), encoding="utf-8", newline="\n")
        reader_md = "\n".join(md_parts).replace(corpus_pdf_relative, reader_pdf_relative)
        (reader_output / reader_text_filename).write_text(
            reader_md,
            encoding="utf-8",
            newline="\n",
        )
        anchors.extend(find_anchors(document_id, document_index, pages, source_kind))

    output.mkdir(parents=True, exist_ok=True)
    write_jsonl(output / "documents.jsonl", metadata)
    write_jsonl(output / "pages.jsonl", pages_jsonl)
    write_jsonl(output / "anchors.jsonl", anchors)
    write_index_yaml(output / "index.yaml", metadata, generated_at)

    print(
        json.dumps(
            {
                "status": "ok",
                "output": str(output),
                "documents": len(metadata),
                "pages": len(pages_jsonl),
                "anchors": len(anchors),
                "text_chars": sum(item["text_char_count"] for item in metadata),
                "online_text_used": sum(item["text_source"].startswith("online_") for item in metadata),
                "pdf_fallback_used": sum(item["text_source"] == "pdf_extraction" for item in metadata),
                "online_fallbacks": [
                    {"id": item["id"], "error": item["online_fetch_error"]}
                    for item in metadata
                    if item["online_fetch_error"] and item["text_source"] == "pdf_extraction"
                ],
                "warnings": [
                    {
                        "id": item["id"],
                        "status": item["quality_status"],
                        "error": item["quality_warning"],
                    }
                    for item in metadata
                    if item["quality_status"] != "ok"
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
