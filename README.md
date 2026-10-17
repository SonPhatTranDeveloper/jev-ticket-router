# Jev Ticket Router

Code mẫu cho video **"Quên LLM đi khi bạn chỉ cần một QUYẾT ĐỊNH | Tất cả về JEV trong 11 PHÚT"**
trên kênh [Học Lập Trình cùng Phát](https://www.youtube.com/@TranSonPhat).

Một ticket hỗ trợ khách hàng, ba câu hỏi có kiểu (typed questions), và chỉ một
lần gọi duy nhất tới Jev — mô hình quyết định (decision model) của TypeSafe AI.
Không có prompt nào được viết ra, cũng không có JSON nào phải parse.

## Ý tưởng

Với một tác vụ phân loại đơn giản, hầu hết chúng ta hiện nay đều gửi cả ticket
cho một mô hình ngôn ngữ lớn, rồi lại phải viết thêm code để parse chuỗi trả về
và xử lý những category mà mô hình tự bịa ra. Jev đi theo hướng khác: chúng ta
khai báo trước những câu trả lời nào được cho phép, và Jev trả về lựa chọn kèm
xác suất, chứ không trả về văn bản.

Ba loại câu hỏi được dùng trong file này:

| Câu hỏi | Loại | Trả về |
| --- | --- | --- |
| `team` | `choice` | một trong ba bộ phận: billing, technical, account |
| `refund` | `noul` | xác suất từ 0 đến 1 cho câu hỏi có/không |
| `urgency` | `score` | một con số trên thang ba mức, có thể nằm giữa hai mức |

Cả ba câu hỏi được trả lời cùng một lúc, trong một lần gọi duy nhất.

## Cách chạy

Chỉ cần Python 3 — file này dùng standard library, không cần cài thêm thư viện
nào cả.

```bash
export TYPESAFE_API_KEY=apikey_...
python3 jev_router.py
```

API key được đọc từ biến môi trường `TYPESAFE_API_KEY`. Key không bao giờ được
viết vào trong file, vì file này xuất hiện trên màn hình trong video.

## Kết quả mẫu

```
team     : billing  (confidence 1.00)
           billing    1.000
           technical  0.000
           account    0.000
refund   : 0.99
urgency  : 1.45 — Bình thường, xử lý trong vòng hai ngày

→ tự động chuyển đến bộ phận billing
```

Một lần gọi mất khoảng 600 milli giây và tốn khoảng 22 phần triệu đô la.

## Hai điều đáng lưu ý

**`confidence` bằng `1.00` không có nghĩa là câu trả lời đúng.** Giá trị này chỉ
đo xem xác suất tập trung vào một lựa chọn đến mức nào, chứ không đo xem lựa
chọn đó có chính xác hay không. Jev không thể trả về một giá trị nằm ngoài tập
đã khai báo, nhưng vẫn có thể chọn sai một giá trị hợp lệ — và chọn sai với độ
tự tin tuyệt đối.

**Ngưỡng `AUTO_ROUTE_MIN_CONFIDENCE = 0.75` là do mình tự đặt**, dựa trên dữ
liệu của mình. Jev không đặt ngưỡng đó hộ chúng ta. Quyết định cuối cùng nằm
trong code, không nằm trong model.

## Về những con số được quảng cáo

Trong video mình có đối chiếu lại một vài số liệu, vì chúng đáng để đọc cẩn
thận hơn một chút:

- Trang chủ TypeSafe nói Jev nhanh hơn **193 lần** so với một LLM. Khi mình tự
  đo thì một lần gọi mất khoảng **600 milli giây**.
- Trên bộ dữ liệu **Banking77**, một bài test độc lập cho thấy Jev đạt
  **78,3%**, còn Claude Opus đạt **85,7%**.

Jev không phải để thay thế các mô hình ngôn ngữ lớn, mà để dùng cho những quyết
định nhỏ và lặp lại rất nhiều lần — dành LLM cho những việc cần suy luận thật sự.

## Kênh

Các video khác về AI, Machine Learning và lập trình:
[Học Lập Trình cùng Phát](https://www.youtube.com/@TranSonPhat)
