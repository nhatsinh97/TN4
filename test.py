import cv2
import pytesseract

# Đọc ảnh gốc
image = cv2.imread("output.jpg")
if image is None:
    print("❌ Không thể đọc ảnh. Kiểm tra đường dẫn hoặc định dạng ảnh.")
    exit(1)

# ⚠️ Cắt vùng chứa số: điều chỉnh lại theo ảnh thực tế nếu cần
# Dạng: image[y1:y2, x1:x2]
cropped = image[130:240, 150:400]  # Tham số ví dụ, có thể bạn cần thay đổi

# Tiền xử lý ảnh
gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# Debug ảnh đã xử lý
cv2.imwrite("debug_crop.jpg", gray)

# OCR
custom_config = r'--oem 3 --psm 6 outputbase digits'
result = pytesseract.image_to_string(gray, config=custom_config)

print("🔢 Số nước nhận diện được:", result.strip())
