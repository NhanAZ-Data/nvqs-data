# Dữ liệu pháp luật nghĩa vụ quân sự Việt Nam

Corpus nguồn và dữ liệu máy đọc về pháp luật nghĩa vụ quân sự (NVQS) Việt Nam,
được chuẩn hóa để con người và agent có thể tra cứu, phân tích, đối chiếu nguồn
và tái tạo dữ liệu.

[![Schema](https://img.shields.io/badge/corpus-schema%20v2-2563eb)](./agent-corpus/README.md)
[![Ngôn ngữ](https://img.shields.io/badge/ng%C3%B4n%20ng%E1%BB%AF-ti%E1%BA%BFng%20Vi%E1%BB%87t-dc2626)](./agent-corpus/)
[![Phạm vi](https://img.shields.io/badge/v%C4%83n%20b%E1%BA%A3n-18-0f766e)](./van-ban-nguon/MANIFEST.yaml)

> Đây là bộ dữ liệu phục vụ nghiên cứu, tra cứu và xây dựng ứng dụng. Không phải
> ý kiến tư vấn pháp lý. Khi dùng để giải quyết một trường hợp cụ thể, cần kiểm
> tra văn bản đang có hiệu lực và đối chiếu bản gốc do cơ quan có thẩm quyền ban
> hành.

## Mục tiêu

Repository này tập trung vào ba việc:

- lưu giữ các PDF nguồn đã tải, kèm SHA-256, số trang, kích thước và URL nguồn;
- ưu tiên lấy lớp văn bản từ HTML/DOC/DOCX công khai để giảm lỗi trích xuất PDF;
- cung cấp corpus JSONL/Markdown có cấu trúc để agent dễ tìm kiếm, thống kê và
  trích dẫn theo văn bản, đơn vị nội dung và điều khoản.

Các câu hỏi phù hợp với corpus gồm: điều kiện và quy trình tuyển quân, khám sức
khỏe NVQS, tiêu chuẩn thể lực/BMI, hồ sơ và thủ tục, nghĩa vụ tham gia Công an
nhân dân, xử phạt hành chính và trách nhiệm hình sự liên quan đến trốn tránh
nghĩa vụ quân sự.

## Phạm vi dữ liệu hiện tại

Bộ nguồn hiện có **18 văn bản PDF**, gồm:

| Nhóm | Văn bản chính |
| --- | --- |
| Luật NVQS | 78/2015/QH13; 98/2025/QH15; 14/2026/QH16; 133/2026/VBHN-LQ-VPQH |
| Tuyển chọn, gọi nhập ngũ | 36/VBHN-BQP; 68/2025/TT-BQP; 173/2026/TT-BQP |
| Khám và tiêu chuẩn sức khỏe | 105/2023/TT-BQP; 88/2025/VBHN-BQP; 106/2025/TT-BQP; 8428/QY-ĐTr |
| Điều kiện loại trừ liên quan sơ tuyển | 28/2026/NĐ-CP về danh mục chất ma túy và tiền chất |
| Đăng ký, thủ tục NVQS | 75/VBHN-BQP; 6375/QĐ-BQP |
| Quốc phòng, quân sự và xử phạt | 220/2025/NĐ-CP; 218/2025/NĐ-CP |
| Nghĩa vụ tham gia CAND | 101/2025/TT-BCA |
| Liên quan hình sự | Bộ luật Hình sự 100/2015/QH13, bản toàn văn có Điều 332 |

Danh mục đầy đủ, tên tệp, hash và provenance nằm trong
[`van-ban-nguon/MANIFEST.yaml`](./van-ban-nguon/MANIFEST.yaml).

## Cách tổ chức repository

```text
.
├── README.md                         # Tài liệu tổng quan của repository
├── nvqs-law-2026-agent-brief.md      # Brief nghiệp vụ và định hướng tra cứu
├── so-do-ung-xu-khi-nghi-ghi-sai-ket-qua-kham-nvqs.md
│                                      # Sơ đồ ứng xử, khiếu nại, tố cáo, giám định
├── van-ban-nguon/                    # PDF nguồn, manifest và metadata tải về
│   ├── MANIFEST.yaml
│   └── *.pdf
├── van-ban-md/                       # Toàn văn Markdown dành cho người đọc
│   ├── README.md
│   └── *.md                           # Cùng tên PDF, chỉ đổi .pdf thành .md
├── agent-corpus/                     # Corpus đã chuẩn hóa cho agent
│   ├── README.md                     # Mô tả schema và cách truy vấn
│   ├── schema.json                   # Hợp đồng dữ liệu schema v2
│   ├── index.yaml                    # Chỉ mục tổng hợp và thống kê
│   ├── documents.jsonl               # Một record cho mỗi văn bản
│   ├── pages.jsonl                   # Các đơn vị văn bản để đọc/tìm kiếm
│   ├── anchors.jsonl                 # Chương, mục, điều, phụ lục, biểu mẫu
│   └── text/                         # Văn bản Markdown có metadata cho agent
└── tools/
    ├── build_agent_corpus.py         # Tạo lại corpus
    ├── online_text_sources.yaml      # Registry nguồn HTML/DOC/DOCX
    └── extract_online_doc.ps1        # Hỗ trợ trích xuất DOC/DOCX trên Windows
```

## Đọc toàn văn Markdown

Thư mục [`van-ban-md/`](./van-ban-md/) chứa một file `.md` đầy đủ cho từng văn
bản PDF trong `van-ban-nguon/`. Đây là bản dành cho người đọc: mở trực tiếp để
đọc toàn văn, tìm kiếm bằng `Ctrl+F`, hoặc liên kết tới PDF gốc để đối chiếu
chữ ký, dấu, bảng và bố cục.

Các file trong `van-ban-md/` được tạo cùng lúc với `agent-corpus/text/` từ cùng
một nguồn text. Không chỉnh sửa riêng một bản; khi cập nhật PDF hoặc nguồn text,
hãy chạy lại công cụ dựng corpus để hai bản Markdown không bị lệch nội dung.

## Dùng nhanh cho agent

### Đọc danh mục văn bản

```powershell
Get-Content .\agent-corpus\documents.jsonl |
  ConvertFrom-Json |
  Select-Object doc_id, identifier, title, text_source, quality_status
```

### Tìm điều khoản hoặc chủ đề

```powershell
rg -n "BMI|chiều cao|cân nặng|khiếu nại|tố cáo|Điều 332" `
  .\agent-corpus\text `
  .\agent-corpus\pages.jsonl `
  .\agent-corpus\anchors.jsonl
```

### Lấy các điều khoản có tiêu đề tương ứng

```powershell
Get-Content .\agent-corpus\anchors.jsonl |
  ConvertFrom-Json |
  Where-Object { $_.anchor_type -eq "article" -and $_.title -match "khám|sức khỏe|nhập ngũ" } |
  Select-Object doc_id, anchor_id, title, page_number, char_start, char_end
```

### Đọc một tài liệu theo `doc_id`

```powershell
$id = "SRC-HEALTH-BASE-2023"
Get-Content .\agent-corpus\pages.jsonl |
  ConvertFrom-Json |
  Where-Object { $_.doc_id -eq $id } |
  Select-Object unit_id, page_number, text
```

Nếu cần hiểu đầy đủ trường dữ liệu, đọc
[`agent-corpus/README.md`](./agent-corpus/README.md) trước khi xử lý JSONL.

Tài liệu thực hành về cách bảo toàn chứng cứ và xử lý khi nghi ngờ ghi sai kết
quả khám sức khỏe nằm tại
[`so-do-ung-xu-khi-nghi-ghi-sai-ket-qua-kham-nvqs.md`](./so-do-ung-xu-khi-nghi-ghi-sai-ket-qua-kham-nvqs.md).

## Schema corpus v2

Corpus dùng ba loại record chính:

| Tệp | Vai trò | Khóa thường dùng |
| --- | --- | --- |
| `documents.jsonl` | Metadata, nguồn, hash, trạng thái chất lượng của văn bản | `doc_id`, `identifier` |
| `pages.jsonl` | Văn bản chuẩn hóa dùng cho đọc và tìm kiếm | `unit_id`, `doc_id` |
| `anchors.jsonl` | Chỉ mục cấu trúc như Chương, Mục, Điều, Phụ lục, Mẫu | `anchor_id`, `doc_id` |

Các trường cần chú ý:

- `text_source`: `online_html`, `online_doc` hoặc `pdf_extraction`;
- `quality_status`: trạng thái kiểm tra lớp text;
- `source_pdf`, `pdf_sha256`, `pdf_manifest_match`: liên kết giữa corpus và PDF
  nguồn;
- `source_url`, `source_page`, `provenance`: nguồn và mức độ tin cậy cần xem khi
  trích dẫn;
- `page_number`, `char_start`, `char_end`: vị trí tương đối trong text unit,
  không mặc nhiên là số trang PDF đối với nguồn HTML/DOC toàn văn.

## Chính sách nguồn và provenance

Quy trình xây dựng corpus là **online-first**:

1. Đọc metadata và PDF nguồn từ `van-ban-nguon/MANIFEST.yaml`.
2. Tìm lớp text công khai tương ứng trong
   [`tools/online_text_sources.yaml`](./tools/online_text_sources.yaml).
3. Ưu tiên HTML, DOC hoặc DOCX từ cổng văn bản chính thức; với DOC/DOCX trên
   Windows, bộ công cụ có thể dùng Microsoft Word COM để đọc nội dung.
4. Chỉ fallback sang `pypdf` khi nguồn online không truy cập được, không có
   selector phù hợp hoặc text lấy được quá ngắn.
5. Giữ PDF cục bộ làm bản đối chiếu hash, số trang, chữ ký, dấu, bảng và bố cục.

Điều này có nghĩa `text_source: online_html` hoặc `online_doc` không phải là
cam kết rằng text đó thay thế được PDF gốc trong mọi tình huống. Với trích dẫn
pháp lý, cần kiểm tra cả nội dung corpus và bản PDF nguồn.

Hai trường hợp cần chú ý:

- `6375/QĐ-BQP`: PDF được lấy từ bản sao trên cổng thông tin cơ quan nhà nước;
  khi xử lý tranh chấp nên đối chiếu bản phát hành của Bộ Quốc phòng.
- `8428/QY-ĐTr`: PDF hiện có từ tệp đính kèm công khai qua trang mirror; chưa xác
  nhận được URL tệp trực tiếp công khai trên cổng Bộ Quốc phòng. Khi dùng cho
  quyết định cá nhân, cần đối chiếu bản do cơ quan quân sự ban hành.
- `173/2026/TT-BQP` và `28/2026/NĐ-CP`: PDF lấy từ tệp đính kèm chính thức trên
  Cổng thông tin điện tử Chính phủ; bản `.md` ưu tiên toàn văn HTML từ nguồn đọc
  công khai để agent tìm kiếm, còn PDF vẫn là bản đối chiếu pháp lý.
- Hướng dẫn `8428/QY-ĐTr` còn dẫn chiếu `150/2026/TT-BQP` và `6098/QĐ-BQP`;
  tại thời điểm cập nhật chưa tìm được bản PDF công khai có thể xác minh provenance
  trên Cổng văn bản Chính phủ hoặc phapluatquansu.vn, nên chưa đưa bản không kiểm
  chứng vào corpus. Đây là hai mục cần rà lại khi nguồn công khai xuất hiện.

URL nguồn và ghi chú provenance được giữ trong manifest và trong metadata của
`documents.jsonl`; không nên xóa các trường này khi tạo bản dẫn xuất.

## Tái tạo corpus

Yêu cầu tối thiểu:

- Windows nếu cần trích xuất nguồn DOC/DOCX bằng Word COM;
- Python 3;
- các gói Python: `requests`, `beautifulsoup4`, `PyYAML`, `pypdf`.

Cài đặt gói:

```powershell
python -m pip install requests beautifulsoup4 PyYAML pypdf
```

Tạo lại corpus từ PDF nguồn và registry online:

```powershell
python .\tools\build_agent_corpus.py `
  --root .\van-ban-nguon `
  --manifest .\van-ban-nguon\MANIFEST.yaml `
  --online-sources .\tools\online_text_sources.yaml `
  --output .\agent-corpus
```

Lệnh trên đồng thời tạo/cập nhật các file đọc trực tiếp tại
`van-ban-md/`. Có thể chỉ định thư mục khác bằng tùy chọn `--reader-output`.

Lệnh trên có thể tải lại nội dung từ Internet. Kết quả phụ thuộc vào trạng thái
nguồn online tại thời điểm chạy; sau khi tạo lại cần kiểm tra diff, hash và
chất lượng trước khi commit.

## Kiểm định hiện tại

Snapshot hiện tại của corpus:

| Chỉ số | Giá trị |
| --- | ---: |
| Văn bản | 18 |
| Nguồn text online | 16 |
| PDF fallback | 2 |
| Text unit | 40 |
| Anchor | 1.027 |
| Tổng ký tự text | 1.437.776 |
| PDF khớp manifest | 18/18 |
| `quality_status: ok` | 16/16 |

Kiểm tra cú pháp công cụ và trạng thái Git:

```powershell
python -m py_compile .\tools\build_agent_corpus.py
git status --short
```

`git status --short` không nên còn thay đổi ngoài những thay đổi mà người dùng
đang chủ động thực hiện.

## Nguyên tắc sử dụng kết quả

- Phân biệt rõ **văn bản hiện hành**, **văn bản sửa đổi**, **văn bản hợp nhất**
  và **hướng dẫn nghiệp vụ**.
- Không suy ra hiệu lực chỉ từ ngày tải tệp hoặc từ việc một văn bản xuất hiện
  trong corpus.
- Khi trả lời một câu hỏi pháp lý, nên ghi rõ số hiệu, điều/khoản, nguồn và
  thời điểm kiểm tra.
- Không dùng text đã trích xuất để bỏ qua chữ ký, dấu, phụ lục, bảng hoặc chú
  thích trong PDF gốc.
- Đối với khiếu nại, tố cáo, khám sức khỏe hoặc nghĩa vụ cá nhân, cần kiểm tra
  thêm quy trình hành chính và tình trạng hiệu lực tại cơ quan có thẩm quyền.

## Nguồn tham khảo chính

Một số cổng nguồn được sử dụng trong registry:

- [Cổng Thông tin điện tử Chính phủ — Cơ sở dữ liệu văn bản](https://vanban.chinhphu.vn/)
- [Công báo điện tử Chính phủ](https://congbao.chinhphu.vn/)
- [Cổng thông tin điện tử Bộ Công an](https://bocongan.gov.vn/)
- [Cổng thông tin điện tử Bộ Quốc phòng](https://mod.gov.vn/)

## Trạng thái và giấy phép

Corpus đang ở trạng thái phục vụ nghiên cứu và phát triển. Repository hiện chưa
tuyên bố một giấy phép riêng cho toàn bộ dữ liệu. Quyền đối với từng văn bản,
PDF, bản sao và nội dung công bố thuộc về nguồn/cơ quan tương ứng; hãy kiểm tra
điều kiện sử dụng của nguồn trước khi phân phối lại hoặc dùng cho sản phẩm
thương mại.

