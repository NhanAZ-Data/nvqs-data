# NVQS agent corpus schema v2

Bộ dữ liệu này được tạo từ các PDF trong `../van-ban-nguon/` để agent có thể
tra cứu, thống kê và đối chiếu văn bản về nghĩa vụ quân sự Việt Nam.

## Quy trình nguồn

Quy trình là **online-first**:

1. Lấy toàn văn HTML hoặc DOC/DOCX đã có trên mạng theo
   `../tools/online_text_sources.yaml`.
2. Làm sạch giao diện website, chuẩn hóa Unicode/NBSP/khoảng trắng và loại các
   thành phần điều hướng như `Mục lục`, `Hỏi AI`, `Tab mới`, `Sơ đồ`.
3. Chỉ khi nguồn online không truy cập được, selector không tồn tại hoặc text
   quá ngắn mới fallback sang `pypdf.page.extract_text` trên PDF cục bộ.
4. PDF cục bộ vẫn là nguồn đối chiếu hash, số trang, chữ ký, dấu, bảng và bố
   cục. Text online không thay thế việc kiểm tra PDF gốc khi trích dẫn pháp lý.

## Schema chung

Mọi record JSONL đều có các trường sau.

- `schema_version: 2`
- `record_type`: `document`, `text_unit` hoặc `anchor`
- `document_index`: thứ tự ổn định theo manifest
- `text_normalization_profile: vi-legal-v2` cho record có text

Các đường dẫn trong corpus là tương đối từ thư mục `agent-corpus`.

## Các tệp

- `documents.jsonl` chứa một record cho mỗi văn bản. Đọc file này trước để lọc
  theo số hiệu, nguồn, hash, chất lượng và trạng thái hiệu lực nguồn.
- `pages.jsonl` chứa đơn vị text chuẩn hóa cho agent. PDF fallback có một record
  cho mỗi trang cùng với `page_number`. HTML/DOC online thường có một record toàn văn
  với `page_number: null` vì không giữ được ánh xạ sang trang PDF.
- `anchors.jsonl` lập chỉ mục Chương, Mục, Điều, Phụ lục và Mẫu. Mỗi anchor có
  `unit_id`, `unit_index`, `line_number` và `heading` để nhảy ngược về
  `pages.jsonl`.
- `schema.json` định nghĩa hợp đồng dữ liệu v2, liệt kê record type, trường bắt buộc và
  các giá trị enum cho agent hoặc validator.
- `index.yaml` cung cấp chỉ mục gọn cho người đọc và công cụ không muốn parse JSONL.
- Mỗi file trong `text/*.md` chứa một văn bản đã chuẩn hóa, có JSON metadata ở
  đầu file và phần nội dung để đọc trực tiếp.

## Schema `documents.jsonl`

Record có các trường sau để mô tả nguồn PDF.

- `source_pdf`, `source_pdf_filename`
- `pdf_declared_page_count`, `pdf_page_count`
- `pdf_declared_byte_count`, `pdf_byte_count`
- `pdf_declared_sha256`, `pdf_sha256`
- `pdf_manifest_match.page_count`, `.byte_count`, `.sha256`, `.all`

Record có các trường sau để mô tả text.

- `text_source`: `online_html`, `online_doc` hoặc `pdf_extraction`
- `text_source_url`, `text_source_page`, `text_source_tier`
- `text_extraction_method`
- `text_unit_count`, `text_char_count`, `nonempty_text_units`
- `quality_status`, `quality_warning`, `online_fetch_error`

`source_provenance` và `source_note` giữ lại các cảnh báo provenance, ví dụ
PDF là bản sao trên cổng cơ quan nhà nước hoặc tệp đính kèm từ trang mirror.

## Trạng thái chất lượng

- Trạng thái `ok` nghĩa là đã tạo được text dùng cho đọc và tìm kiếm. Vẫn nên đối chiếu PDF gốc khi
  cần trích dẫn từng chữ.
- Trạng thái `page_extraction_warning` nghĩa là một hoặc nhiều trang PDF có lỗi nhưng vẫn còn
  text.
- Trạng thái `partial_or_image_only` nghĩa là chỉ lấy được rất ít text, thường là chữ ký hoặc
  phần không đáng kể của PDF scan. Không dùng làm toàn văn.
- Trạng thái `empty_or_image_only` nghĩa là PDF không có lớp text đọc được. Cần HTML/DOC khác hoặc
  OCR có kiểm tra thủ công.

`text_char_count: 0` không có nghĩa là văn bản không có nội dung. Nó chỉ là
giới hạn của lớp text trong PDF.

## Ví dụ truy vấn

```powershell
# Liệt kê nguồn và chất lượng của từng văn bản
Get-Content .\documents.jsonl |
  ForEach-Object { $_ | ConvertFrom-Json } |
  Select-Object document_index, identifier, text_source, quality_status,
    text_char_count, text_source_tier

# Tìm nội dung liên quan
rg -n "BMI|chiều cao|cân nặng|khiếu nại|tố cáo|Điều 332" .\text .\pages.jsonl .\anchors.jsonl

# Lấy toàn văn một văn bản theo id
Get-Content .\pages.jsonl |
  ForEach-Object { $_ | ConvertFrom-Json } |
  Where-Object document_id -eq 'SRC-HEALTH-BASE-2023' |
  Select-Object -ExpandProperty text
```

## Provenance

`text_source_tier` phân biệt `official_html`, `official_congbao_doc`,
`secondary_fulltext`, `official_summary_only` và
`official_attachment_mirror_summary_only`. Không nên đánh đồng toàn văn trên
website thứ cấp và bản ban hành chính thức. Trường `source_pdf` cùng các hash
là điểm neo để kiểm tra lại.

Hướng dẫn `8428/QY-ĐTr` hiện có PDF từ tệp đính kèm công khai qua trang mirror.
Chưa xác nhận được URL tệp trực tiếp công khai trên cổng Bộ Quốc phòng. Ghi
chú này được giữ trong cả manifest và `documents.jsonl`.
