# PDF có lớp văn bản

Thư mục này chứa các bản PDF tải trực tiếp từ nguồn công khai đã được kiểm tra
có lớp văn bản có thể chọn và sao chép. Các tệp được giữ nguyên dạng PDF của
nguồn tải về; không OCR, không dựng lại PDF từ Markdown/HTML/DOCX và không sửa
nội dung, dấu, chữ ký hoặc bố cục.

## Cách dùng

- Dùng PDF trong thư mục này khi cần tìm kiếm, sao chép hoặc trích xuất text.
- Dùng `MANIFEST.yaml` để biết văn bản nào là bản một tệp, văn bản nào được
  Công báo chia thành nhiều tệp, URL nguồn, số trang, số ký tự trích xuất và
  SHA-256.
- Thư mục `van-ban-nguon/` vẫn được giữ nguyên làm bộ PDF nguồn đối chiếu ban
  đầu. Hai thư mục không phải là hai phiên bản nội dung để trộn lẫn.

## Phạm vi hiện tại

Hiện có **24 tệp PDF text**, đại diện cho **20 văn bản** trong bộ 24 văn bản
nguồn:

- 100/2015/QH13: 4 tệp Công báo số 1263+1264, 1265+1266, 1267+1268 và
  1269+1270.
- 88/VBHN-BQP: 2 tệp Công báo số 1641+1642 và 1643+1644.
- 18 văn bản còn lại: 78/2015/QH13, 98/2025/QH15, 14/2026/QH16,
  133/2026/VBHN-LQ-VPQH, 36/VBHN-BQP, 28/2026/NĐ-CP, 101/2025/TT-BCA,
  68/2025/TT-BQP, 75/VBHN-BQP, 106/2025/TT-BQP, 173/2026/TT-BQP,
  218/2025/NĐ-CP, 220/2025/NĐ-CP, 6375/QĐ-BQP, 8428/QY-ĐTr,
  218/2013/TT-BQP, 62/2023/TT-BCA và 131/2025/TT-BCA.

Tên tệp một-tới-một được giữ giống tệp trong `van-ban-nguon`; chỉ các văn bản
mà nguồn chính thức chia thành nhiều tệp mới có hậu tố `cong-bao-...` để không
giả vờ rằng đã tạo ra một PDF hợp nhất mới.

## Các PDF chưa đưa vào đây

Một văn bản vẫn có trong `van-ban-nguon/` nhưng chưa đạt ngưỡng PDF text hữu ích
ở các nguồn đã kiểm tra:

- `105-2023-TT-BQP...pdf`: PDF gốc hiện có là bản scan; hai tệp PDF Công báo tải được có tổng lớp text rất
  ít (1.573 và 3.871 ký tự cho 31 và 74 trang); phần nội dung chính vẫn là
  ảnh scan.
- `13-2016-NĐ-CP...pdf`, `148-2018/TT-BQP...pdf` và `45/2025/TT-BQP...pdf`:
  bản PDF gốc trong `van-ban-nguon/` là scan; Markdown tương ứng lấy từ nguồn
  toàn văn HTML để không OCR hoặc dựng lại PDF.

Trường hợp này không bị OCR hoặc chuyển đổi sang PDF mới để tránh làm
thay đổi bố cục và tạo cảm giác sai rằng đó là bản PDF text gốc. Toàn văn HTML,
DOC/DOCX hoặc Markdown tương ứng vẫn có thể được tra trong `van-ban-md/` và
`agent-corpus/` khi registry nguồn đã có.

## Kiểm tra chất lượng

Các tệp đã được kiểm tra là PDF hợp lệ, có số trang và có text trích xuất được
trên các trang nội dung. Thống kê chi tiết, provenance và hash nằm trong
[`MANIFEST.yaml`](./MANIFEST.yaml).

Ngày rà soát: 2026-11-13, múi giờ Asia/Saigon.
