# Leviathan Hunter – IPA cho iPhone (không cần Mac)

Có 2 bản IPA, cài song song được (khác bundle ID):
- **Levihunt-12Pro.ipa**: bản gốc, dùng cho iPhone 12 Pro.
- **Levihunt-iPhone6.ipa**: bản đã vá CSS cho iOS 12 (iPhone 6).

## 1. Build trên GitHub (miễn phí)
1. Tạo repo mới trên github.com, vào Add file → Upload files, kéo TOÀN BỘ nội dung thư mục này vào
   (nhớ cả thư mục ẩn `.github`; nếu Windows ẩn nó, bật "Hiện mục ẩn" hoặc dùng GitHub Desktop).
2. Commit lên nhánh `main` → tab **Actions** → "Build IPA (chưa ký)" tự chạy (hoặc bấm Run workflow).
3. Chờ ~10 phút → mở lần chạy đó → mục **Artifacts** tải `Levihunt-12Pro.ipa` và `Levihunt-iPhone6.ipa`
   (tải về là file .zip, giải nén ra lấy .ipa).

## 2. Cài lên iPhone từ Windows
- Cài **iTunes** và **iCloud** bản tải từ apple.com (không dùng bản Microsoft Store), rồi cài **Sideloadly**.
- Cắm iPhone, kéo file .ipa vào Sideloadly, nhập Apple ID, bấm Start.
- Trên iPhone: Cài đặt → Cài đặt chung → Quản lý VPN & thiết bị → tin cậy Apple ID của bạn.
- Apple ID miễn phí: app hết hạn sau 7 ngày (ký lại bằng Sideloadly) và tối đa 3 app đang active.

## Đổi tên / icon
- Tên: sửa `display_name` trong `.github/workflows/build-ipa.yml`.
- Icon: thay các file trong `App/Resources/Assets.xcassets/AppIcon.appiconset/` (hoặc nhờ Claude tạo lại).

## Bản vá iPhone 6
`tools/make_ios12.py` tạo `www-ios12/index.html` từ `www-modern/index.html`
(inset, gap của flexbox, dvh, clamp(), :focus-visible, tiền tố -webkit-...).
Giữ nguyên: thuộc tính `translate`/`scale` của CSS mới chỉ ảnh hưởng hiệu ứng trang trí và giao diện desktop.

## Bản PWA (không cần IPA)
Thư mục `pwa/`: đưa lên Netlify/GitHub Pages rồi Safari → Chia sẻ → Thêm vào Màn hình chính.
