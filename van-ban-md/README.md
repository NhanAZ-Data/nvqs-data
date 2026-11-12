# Toàn văn văn bản pháp luật dạng Markdown

Thư mục này chứa bản Markdown đầy đủ, dành cho người đọc, tương ứng với từng
PDF trong [`../van-ban-nguon/`](../van-ban-nguon/).

- Mỗi file dùng đúng tên PDF tương ứng, chỉ đổi phần mở rộng `.pdf` thành
  `.md`, ví dụ `8428-2026-QY-DTr-Huong-dan-so-tuyen-kham-suc-khoe-NVQS-2027.md`.
- Phần đầu file có metadata, số hiệu, nguồn text, SHA-256 và liên kết tương đối
  tới PDF gốc.
- Phần nội dung giữ toàn văn đã trích xuất và được chuẩn hóa để dễ đọc, tìm kiếm
  và cung cấp cho agent.
- Khi cần kiểm tra chữ ký, dấu, bảng hoặc bố cục, phải đối chiếu PDF gốc.

## Cập nhật

Các file trong thư mục này được tạo đồng thời với `../agent-corpus/text/` bằng
`../tools/build_agent_corpus.py`. Không sửa riêng một bản Markdown; sau khi thay
đổi PDF hoặc nguồn text, hãy dựng lại corpus để bản dành cho người đọc và bản
dành cho agent cùng nội dung.
