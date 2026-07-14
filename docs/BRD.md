# Business Requirements Document (BRD)
## HR Tool — Hệ thống Hỗ trợ Tuyển dụng & Quản lý Hồ sơ Ứng viên

---

| Thông tin | Chi tiết |
|---|---|
| Tài liệu | Business Requirements Document (BRD) |
| Phiên bản | v1.0 |
| Ngày tạo | 2026-07-14 |
| Trạng thái | Draft |
| Người sở hữu | HR / Tuyển dụng |

---

## 1. Tóm tắt Điều hành (Executive Summary)

Doanh nghiệp đang đối mặt với việc xử lý hồ sơ ứng viên thủ công, tốn nhiều thời gian và dễ xảy ra sai sót. Mỗi vị trí tuyển dụng đòi hỏi nhân sự phải đọc, phân loại, và định dạng lại hàng chục hoặc hàng trăm hồ sơ ứng viên (CV) ở các định dạng khác nhau. Bên cạnh đó, khi cần trình bày ứng viên cho khách hàng (trong mô hình dịch vụ tuyển dụng), việc chuẩn hóa định dạng CV theo thương hiệu doanh nghiệp tiêu tốn thêm nhiều nguồn lực.

**HR Tool MVP** được xây dựng để tự động hóa quy trình này, giảm thiểu công sức thủ công, tăng tốc độ xử lý ứng viên, và đảm bảo sự nhất quán trong định dạng hồ sơ.

---

## 2. Bối cảnh Kinh doanh (Business Context)

### 2.1. Vấn đề hiện tại

Quy trình xử lý hồ sơ ứng viên hiện tại gặp các vấn đề sau:

1. **Đa dạng định dạng hồ sơ:** Ứng viên nộp CV ở nhiều định dạng khác nhau (PDF, Word, từng mẫu riêng biệt). Bộ phận HR phải đọc thủ công để lấy thông tin.
2. **Mất thời gian chuẩn hóa:** Khi cần trình bày hồ sơ với khách hàng, HR phải copy-paste thông tin vào mẫu cố định của công ty — mất 30–60 phút/hồ sơ.
3. **Dễ bỏ sót thông tin:** Quá trình chép tay thủ công dẫn đến nguy cơ thiếu hoặc sai thông tin quan trọng (ngày tháng, kỹ năng, liên lạc).
4. **Không có kho lưu trữ tập trung:** Hồ sơ ứng viên lưu rải rác ở email, thư mục máy tính cá nhân, không có cách tìm kiếm hay tái sử dụng hiệu quả.
5. **Thiếu nhất quán thương hiệu:** CV gửi khách hàng không đồng đều về định dạng và hình thức, ảnh hưởng hình ảnh chuyên nghiệp của doanh nghiệp.

### 2.2. Cơ hội

- Công nghệ hiện đại cho phép đọc và phân tích văn bản từ tài liệu số một cách tự động với độ chính xác cao.
- Các mẫu CV chuẩn của doanh nghiệp có thể được số hóa và tái sử dụng, giúp đảm bảo tính nhất quán.
- Xây dựng kho ứng viên tập trung giúp tìm kiếm và tái tiếp cận ứng viên cũ nhanh chóng trong các kỳ tuyển dụng tiếp theo.

---

## 3. Mục tiêu Kinh doanh (Business Objectives)

| # | Mục tiêu | Chỉ số đo lường (KPI) |
|---|---|---|
| BO-01 | Giảm thời gian xử lý mỗi hồ sơ ứng viên | Từ ~45 phút → dưới 5 phút/hồ sơ |
| BO-02 | Chuẩn hóa định dạng CV theo thương hiệu doanh nghiệp | 100% hồ sơ gửi khách hàng sử dụng đúng mẫu |
| BO-03 | Xây dựng cơ sở dữ liệu ứng viên tập trung | Toàn bộ hồ sơ ứng viên được lưu trữ tại một nơi |
| BO-04 | Giảm tỷ lệ sai sót do nhập liệu thủ công | Giảm sai sót thông tin từ quá trình copy-paste xuống dưới 5% |
| BO-05 | Nâng cao hình ảnh chuyên nghiệp với khách hàng | Tất cả CV trình bày cho khách hàng đồng nhất về mẫu và chất lượng |

---

## 4. Phạm vi (Scope)

### 4.1. Trong phạm vi (In Scope)

- Tiếp nhận và lưu trữ hồ sơ ứng viên từ file tải lên.
- Tự động trích xuất thông tin ứng viên từ hồ sơ (họ tên, liên lạc, kinh nghiệm, học vấn, kỹ năng).
- Cho phép chỉnh sửa thông tin ứng viên **trực tiếp trên giao diện web** với lưu trữ lịch sử phiên bản.
- Quản lý danh mục mẫu CV của doanh nghiệp.
- Tạo và xuất CV chuẩn hóa từ thông tin ứng viên và mẫu đã chọn.
- Xuất hồ sơ dưới dạng **PDF** (định dạng chính thức để gửi khách hàng).
- Xuất hồ sơ dưới dạng **Word (DOCX)** khi có nhu cầu chỉnh sửa thêm (tính năng bổ sung).

### 4.2. Ngoài phạm vi (Out of Scope — MVP)

- Đăng nhập / phân quyền người dùng.
- Tích hợp với hệ thống ATS (Applicant Tracking System) bên ngoài.
- Gửi email tự động cho ứng viên.
- Quản lý quy trình phỏng vấn và lịch hẹn.
- Phân tích ứng viên bằng AI (đánh giá phù hợp, xếp hạng tự động).
- Ứng dụng di động.

---

## 5. Người Dùng Mục tiêu (Target User)

> Hệ thống phục vụ **duy nhất một nhóm người dùng: bộ phận HR nội bộ** của doanh nghiệp. Không có phân quyền nhiều vai trò trong phạm vi MVP.

**Chuyên viên Tuyển dụng (HR):**
- Là người trực tiếp sử dụng toàn bộ tính năng của hệ thống.
- Kỳ vọng: Tiết kiệm thời gian xử lý hồ sơ, giao diện đơn giản, kết quả trích xuất chính xác.
- Không yêu cầu kỹ năng kỹ thuật; chỉ cần biết dùng trình duyệt web.

---

## 6. Yêu cầu Nghiệp vụ (Business Requirements)

### 6.1. Quản lý Mẫu CV (Template Management)

| Mã | Yêu cầu | Mức độ ưu tiên |
|---|---|---|
| BR-T01 | Hệ thống phải cho phép tải lên các mẫu CV của doanh nghiệp để số hóa và lưu trữ | Bắt buộc |
| BR-T02 | Hệ thống phải tự động nhận diện cấu trúc của mẫu CV (các phần, bố cục, màu sắc, phông chữ) | Bắt buộc |
| BR-T03 | Hệ thống phải lưu trữ và hiển thị danh sách tất cả các mẫu CV đã tải lên | Bắt buộc |
| BR-T04 | Người dùng phải có thể xóa các mẫu CV không còn sử dụng | Bắt buộc |
| BR-T05 | Khi mẫu không thể nhận diện tự động, hệ thống phải có phương án dự phòng để vẫn có thể trích xuất cấu trúc | Should-have |

### 6.2. Quản lý Hồ sơ Ứng viên (Candidate Management)

| Mã | Yêu cầu | Mức độ ưu tiên |
|---|---|---|
| BR-C01 | Hệ thống phải cho phép tải lên CV của ứng viên để xử lý | Bắt buộc |
| BR-C02 | Hệ thống phải tự động trích xuất: họ tên, email, số điện thoại, địa chỉ, liên kết mạng xã hội nghề nghiệp | Bắt buộc |
| BR-C03 | Hệ thống phải tự động trích xuất danh sách kinh nghiệm làm việc (tên công ty, vị trí, thời gian, mô tả công việc) | Bắt buộc |
| BR-C04 | Hệ thống phải tự động trích xuất thông tin học vấn (trường, bằng cấp, chuyên ngành, thời gian) | Bắt buộc |
| BR-C05 | Hệ thống phải tự động trích xuất kỹ năng và chứng chỉ | Bắt buộc |
| BR-C06 | Người dùng phải có thể chỉnh sửa toàn bộ thông tin đã trích xuất **trực tiếp trên giao diện web** mà không cần tải file về | Bắt buộc |
| BR-C07 | Hệ thống phải **lưu lịch sử các phiên bản** của hồ sơ ứng viên sau mỗi lần chỉnh sửa, cho phép xem lại hoặc khôi phục phiên bản trước | Bắt buộc |
| BR-C08 | Hệ thống phải lưu trữ và hiển thị danh sách tất cả ứng viên đã tải lên | Bắt buộc |
| BR-C09 | Người dùng phải có thể xóa hồ sơ ứng viên | Bắt buộc |
| BR-C10 | Khi trích xuất tự động không đủ thông tin, hệ thống phải cố gắng hoàn thiện bằng phương án hỗ trợ thông minh | Should-have |

### 6.3. Tạo & Xuất CV (CV Generation & Export)

| Mã | Yêu cầu | Mức độ ưu tiên |
|---|---|---|
| BR-G01 | Người dùng phải có thể chọn một ứng viên và một mẫu CV để tạo hồ sơ chuẩn hóa | Bắt buộc |
| BR-G02 | Hệ thống phải hiển thị bản xem trước của CV ngay trên giao diện web sau khi tạo | Bắt buộc |
| BR-G03 | Người dùng phải có thể tùy chỉnh nội dung trực tiếp trên giao diện web và xem kết quả ngay lập tức | Bắt buộc |
| BR-G04 | Hệ thống phải cho phép xuất CV dưới dạng **PDF** để gửi cho khách hàng — đây là định dạng xuất chính | **Bắt buộc** |
| BR-G05 | CV PDF xuất ra phải trung thành với định dạng của mẫu đã chọn (bố cục, màu sắc, phông chữ) | Bắt buộc |
| BR-G06 | Hệ thống phải lưu lại bản nháp CV để người dùng có thể tiếp tục chỉnh sửa sau | Bắt buộc |
| BR-G07 | Hệ thống nên cho phép xuất CV dưới dạng Word (DOCX) khi người dùng cần chỉnh sửa thêm ngoài hệ thống | Should-have |
| BR-G08 | Hệ thống nên hỗ trợ tải lên mẫu CV dạng DOCX (ngoài PDF) | Nice-to-have |

---

## 7. Yêu cầu Phi chức năng (Non-Functional Business Requirements)

| # | Yêu cầu | Mô tả |
|---|---|---|
| NFB-01 | **Tốc độ xử lý** | Một hồ sơ ứng viên phải được hệ thống xử lý và trả kết quả trong vòng 60 giây |
| NFB-02 | **Độ chính xác trích xuất** | Thông tin liên hệ cơ bản (email, số điện thoại) phải được trích xuất đúng ít nhất 90% trường hợp |
| NFB-03 | **Tính sẵn sàng** | Hệ thống phải hoạt động ổn định trong giờ hành chính (8:00–18:00) |
| NFB-04 | **Bảo mật dữ liệu** | Dữ liệu ứng viên và file tải lên phải được lưu trữ nội bộ qua MinIO trong hệ thống của doanh nghiệp, không gửi ra ngoài bên thứ ba |
| NFB-05 | **Dễ sử dụng** | Người dùng mới không cần đào tạo chuyên sâu vẫn có thể sử dụng thành thạo sau 30 phút làm quen |
| NFB-06 | **Định dạng đầu vào** | Hệ thống phải hỗ trợ đọc file **PDF có text layer** (copyable PDF). PDF dạng scan hình ảnh không được hỗ trợ trong MVP |
| NFB-07 | **Lịch sử phiên bản** | Mỗi lần lưu chỉnh sửa hồ sơ phải tạo ra một phiên bản mới — không được ghi đè phiên bản cũ |

---

## 8. Điều kiện Thành công (Success Criteria)

MVP được coi là thành công khi đáp ứng đầy đủ các tiêu chí sau:

- [ ] Chuyên viên HR có thể tải lên 1 mẫu CV (PDF có text layer) và hệ thống nhận diện đúng cấu trúc (ít nhất 2 phần).
- [ ] Upload file PDF dạng scan → hệ thống thông báo lỗi rõ ràng, hướng dẫn người dùng tải lại đúng định dạng.
- [ ] Chuyên viên HR có thể tải lên 1 CV ứng viên và hệ thống trích xuất đúng: họ tên, email, ít nhất 1 kinh nghiệm làm việc.
- [ ] Chuyên viên HR có thể chỉnh sửa thông tin ứng viên trực tiếp trên giao diện web và lưu thành công.
- [ ] Mỗi lần lưu tạo ra một phiên bản mới trong lịch sử — người dùng có thể xem lại hoặc khôi phục phiên bản cũ.
- [ ] Chuyên viên HR có thể tạo một CV chuẩn hóa bằng cách ghép thông tin ứng viên vào mẫu đã chọn.
- [ ] CV được xuất ra file PDF có thể mở được, hiển thị đúng nội dung và giữ đúng định dạng mẫu.
- [ ] Toàn bộ quy trình từ tải CV đến xuất hồ sơ chuẩn hóa hoàn thành trong dưới 5 phút.

---

## 9. Giả định & Ràng buộc (Assumptions & Constraints)

### Giả định
- Người dùng có kiến thức cơ bản về máy tính và sử dụng trình duyệt web.
- CV ứng viên là **file PDF có thể sao chép văn bản** (copyable PDF), không phải bản scan hình ảnh.
- Doanh nghiệp đã có ít nhất 1 mẫu CV theo định dạng PDF.
- Hệ thống chạy trên mạng nội bộ của doanh nghiệp.

### Ràng buộc
- Ngân sách MVP: Ưu tiên sử dụng công nghệ nguồn mở, không phát sinh chi phí bản quyền phần mềm.
- Phạm vi MVP: Không bao gồm tính năng đăng nhập/phân quyền — mọi người trong team đều truy cập được hệ thống.
- Bảo mật: Tuyệt đối không gửi dữ liệu ứng viên lên các dịch vụ AI đám mây bên ngoài. Mọi xử lý trí tuệ nhân tạo phải chạy hoàn toàn nội bộ (on-premise).

---

## 10. Rủi ro Kinh doanh (Business Risks)

| Rủi ro | Mức độ | Tác động | Phương án giảm thiểu |
|---|---|---|---|
| Trích xuất thông tin không chính xác với CV định dạng lạ | Trung bình | Người dùng mất tin tưởng vào hệ thống | Cho phép chỉnh sửa thủ công toàn bộ sau khi trích xuất |
| Người dùng không chịu thay đổi quy trình cũ | Trung bình | Tỷ lệ áp dụng thấp | Thiết kế UX đơn giản, đào tạo nhanh, demo trực tiếp |
| PDF có bảo vệ bản quyền hoặc là file scan | Cao | Không trích xuất được | Thông báo lỗi rõ ràng, hướng dẫn tải lại đúng định dạng |
| Mẫu CV của doanh nghiệp thay đổi thường xuyên | Thấp | Cần cập nhật mẫu liên tục | Thiết kế tính năng quản lý mẫu dễ cập nhật |
| Dữ liệu lịch sử phiên bản tích tụ theo thời gian | Thấp | Tăng dung lượng lưu trữ nếu số ứng viên lớn | Chấp nhận trong MVP; lên kế hoạch giới hạn số phiên bản lưu trữ (VD: tối đa 50 phiên bản/ứng viên) cho phiên bản sau |

---

*Tài liệu này sẽ được xem xét và cập nhật sau mỗi Sprint hoặc khi có thay đổi yêu cầu từ stakeholders.*

---

## 11. Lịch sử cập nhật (Audit Log)

- **14/07/2026**: Cập nhật hệ thống lưu trữ sang MinIO (On-Premise Object Storage) thay vì lưu trữ tại thư mục local theo yêu cầu. Thực hiện audit/check lại toàn bộ file 14/07/2026.
