import hashlib
import json
import os

class Authenticator:
    def __init__(self, user_file='users.json'):
        self.user_file = user_file
        if not os.path.exists(self.user_file):
            self.create_admin_user()

    def hash_password(self, password):
        """Mã hóa mật khẩu sang chuỗi ký tự an toàn (SHA256)."""
        return hashlib.sha256(password.encode()).hexdigest()

    def load_users(self):
        """Hàm phụ trợ: Đọc danh sách user từ file."""
        try:
            with open(self.user_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_users(self, users):
        """Hàm phụ trợ: Lưu danh sách user vào file."""
        with open(self.user_file, 'w') as f:
            json.dump(users, f, indent=4)

    def create_admin_user(self):
        """Tạo tài khoản admin mặc định khi chạy lần đầu."""
        users = [{
            "username": "admin",
            "password": self.hash_password("admin123"), 
            "role": "admin"
        }]
        self.save_users(users)
        print("Đã khởi tạo tài khoản Admin mặc định (admin/admin123).")

    def register(self, username, password, role="user"):
        """
        Chức năng: Tạo tài khoản mới.
        Mặc định role là 'user' (người dùng thông thường).
        """
        users = self.load_users()

        for user in users:
            if user['username'] == username:
                return False, "Tài khoản đã tồn tại!"

        new_user = {
            "username": username,
            "password": self.hash_password(password), 
            "role": role
        }
        users.append(new_user)
        self.save_users(users)
        return True, "Tạo tài khoản thành công!"

    def login(self, username, password):
        """Kiểm tra đăng nhập. Trả về role nếu đúng, None nếu sai."""
        users = self.load_users()
        hashed_input = self.hash_password(password)
        
        for user in users:
            if user['username'] == username and user['password'] == hashed_input:
                return user['role'] 
        
        return None