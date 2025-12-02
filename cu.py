import sys
import subprocess

print("Đang bắt đầu sửa lỗi... Đợi xíu nhé!")
print(f"Vị trí Python đang chạy: {sys.executable}")

try:
    # Dòng này ép máy tính cài requests vào đúng chỗ nó đang chạy
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    print("\n------------------------------------------------")
    print("✅ THÀNH CÔNG RỒI! Đã cài xong thư viện requests.")
    print("------------------------------------------------")
except Exception as e:
    print(f"\n❌ Vẫn lỗi: {e}")