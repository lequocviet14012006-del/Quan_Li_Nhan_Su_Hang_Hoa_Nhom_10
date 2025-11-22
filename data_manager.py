import json
import os

class DataManager:
    """Class chịu trách nhiệm duy nhất là Đọc và Ghi file JSON."""
    
    def __init__(self, file_path):
        self.file_path = file_path

    def read_data(self):
        """Đọc dữ liệu từ file. Trả về list rỗng nếu file lỗi hoặc không tồn tại."""
        if not os.path.exists(self.file_path):
            return [] # File chưa có thì trả về list rỗng để code không bị crash
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return [] # Nếu file lỗi định dạng, cũng trả về rỗng

    def write_data(self, data):
        """Ghi đè dữ liệu vào file JSON."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                # ensure_ascii=False để viết tiếng Việt không bị lỗi font
                # indent=4 để file JSON đẹp, dễ đọc
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Lỗi ghi file: {e}")
            return False

class EmployeeManager:
    def __init__(self):
        # Khởi tạo DataManager chuyên quản lý file employees.json
        self.db = DataManager('employees.json')

    def get_all(self):
        return self.db.read_data()

    def add_employee(self, name, position, date, salary):
        employees = self.get_all()
        
        # --- Logic tự động tạo ID (NV001, NV002...) ---
        new_id = 1
        if len(employees) > 0:
            # Lấy ID cuối cùng (ví dụ "NV005"), cắt bỏ chữ "NV", lấy số 5 + 1
            last_id = employees[-1]['id'] 
            new_id = int(last_id.replace("NV", "")) + 1
        
        id_str = f"NV{new_id:03d}" # Format thành NV001, NV010...
        
        # Tạo dictionary nhân viên mới
        new_emp = {
            "id": id_str,
            "ten": name,
            "chuc_vu": position,
            "ngay_vao_lam": date,
            "luong": int(salary)
        }
        
        employees.append(new_emp)
        return self.db.write_data(employees)

    def update_employee(self, emp_id, name, position, date, salary):
        employees = self.get_all()
        for emp in employees:
            if emp['id'] == emp_id:
                emp['ten'] = name
                emp['chuc_vu'] = position
                emp['ngay_vao_lam'] = date
                emp['luong'] = int(salary)
                return self.db.write_data(employees)
        return False # Không tìm thấy ID

    def delete_employee(self, emp_id):
        employees = self.get_all()
        # Giữ lại những người có ID KHÁC với id cần xóa
        new_list = [emp for emp in employees if emp['id'] != emp_id]
        
        if len(new_list) < len(employees): # Nếu độ dài thay đổi nghĩa là đã xóa được
            return self.db.write_data(new_list)
        return False

    def search_employee(self, keyword):
        employees = self.get_all()
        keyword = keyword.lower()
        result = []
        for emp in employees:
            # Tìm trong tên hoặc mã NV
            if keyword in emp['ten'].lower() or keyword in emp['id'].lower():
                result.append(emp)
        return result

class ProductManager:
    def __init__(self):
        self.db = DataManager('products.json')

    def get_all(self):
        return self.db.read_data()

    def add_product(self, name, stock, price, supplier):
        products = self.get_all()
        
        # Logic tạo ID cho sản phẩm (SP001...)
        new_id = 1
        if len(products) > 0:
            last_id = products[-1]['id']
            new_id = int(last_id.replace("SP", "")) + 1
        id_str = f"SP{new_id:03d}"

        new_prod = {
            "id": id_str,
            "ten_hang": name,
            "so_luong_ton": int(stock),
            "don_gia": int(price),
            "nha_cung_cap": supplier
        }
        products.append(new_prod)
        return self.db.write_data(products)

    def update_product(self, prod_id, name, stock, price, supplier):
        products = self.get_all()
        for prod in products:
            if prod['id'] == prod_id:
                prod['ten_hang'] = name
                prod['so_luong_ton'] = int(stock)
                prod['don_gia'] = int(price)
                prod['nha_cung_cap'] = supplier
                return self.db.write_data(products)
        return False

    def delete_product(self, prod_id):
        products = self.get_all()
        new_list = [p for p in products if p['id'] != prod_id]
        if len(new_list) < len(products):
            return self.db.write_data(new_list)
        return False

    def search_product(self, keyword):
        products = self.get_all()
        keyword = keyword.lower()
        result = []
        for prod in products:
            if keyword in prod['ten_hang'].lower() or keyword in prod['id'].lower():
                result.append(prod)
        return result

# Phần này chỉ chạy khi bạn run file này trực tiếp
if __name__ == "__main__":
    print("--- TEST NHÂN VIÊN ---")
    emp_mgr = EmployeeManager()
    
    # 1. Test Thêm
    print("Đang thêm nhân viên...")
    emp_mgr.add_employee("Nguyễn Văn Test", "Thực tập", "2023-10-01", 5000000)
    
    # 2. Test Đọc
    data = emp_mgr.get_all()
    print(f"Danh sách hiện tại: {len(data)} nhân viên")
    print(data)

    # 3. Test Tìm kiếm
    search_res = emp_mgr.search_employee("Test")
    print(f"Tìm thấy: {search_res}")

    # Hãy mở file employees.json ra xem dữ liệu có vào không nhé!