import tkinter as tk
from tkinter import ttk, messagebox
import json, os
from datetime import datetime, date

# ============================
#   DATA MANAGER
# ============================
class DataManager:
    def __init__(self, users_file='users.json', products_file='san_pham.json', invoices_file='hoa_don.json'):

        self.users_file = users_file
        self.products_file = products_file
        self.invoices_file = invoices_file
        self._khoi_tao_mac_dinh()

    # ----- Hàm chung -----
    def doc_json(self, f):
        if not os.path.exists(f):
            return []
        try:
            with open(f, 'r', encoding='utf-8') as fd:
                return json.load(fd)
        except:
            return []

    def luu_json(self, f, d):
        with open(f, 'w', encoding='utf-8') as fd:
            json.dump(d, fd, ensure_ascii=False, indent=4)

    # ----- Khởi tạo dữ liệu mặc định -----
    def _khoi_tao_mac_dinh(self):
        if not os.path.exists(self.users_file):
            users = [
                {"ma_nv":"NV000","username":"admin","password":"admin123","role":"admin","ten":"Quản Trị Viên",
                 "ngay_vao_lam":"2020-01-01","luong":2000000},
                {"ma_nv":"NV001","username":"nv1","password":"user123","role":"user","ten":"Nhân Viên Mẫu",
                 "ngay_vao_lam":"2022-01-01","luong":1800000}
            ]
            self.luu_json(self.users_file, users)
        if not os.path.exists(self.products_file):
            self.luu_json(self.products_file, [])
        if not os.path.exists(self.invoices_file):
            self.luu_json(self.invoices_file, [])

    # ============ USERS ============
    def load_users(self): return self.doc_json(self.users_file)
    def save_users(self, d): self.luu_json(self.users_file, d)

    def find_user_by_username(self, username):
        for u in self.load_users():
            if u["username"] == username:
                return u
        return None

    def find_user_by_ma(self, ma_nv):
        for u in self.load_users():
            if u.get("ma_nv") == ma_nv:
                return u
        return None

    # ====== ADD USER ======
    def add_user(self, user):
        users = self.load_users()

        # Ràng buộc trùng mã & username
        for u in users:
            if u["username"] == user["username"]:
                return False, "Username đã tồn tại"
            if u["ma_nv"] == user["ma_nv"]:
                return False, "Mã nhân viên đã tồn tại"
#
        # Ràng buộc ngày & lương
        try:
            ngay = datetime.strptime(user["ngay_vao_lam"], "%Y-%m-%d").date()
        except Exception:
            return False, "Ngày vào làm phải theo định dạng YYYY-MM-DD"

        today = date.today()
        if ngay > today:
            return False, "Ngày vào làm phải nhỏ hơn hoặc bằng ngày hiện tại"

        LUONG_CO_BAN = 1500000
        try:
            luong = int(user["luong"])
        except Exception:
            return False, "Lương phải là một số nguyên"#

        if luong <= 0:
            return False, "Lương phải > 0"
        if luong < LUONG_CO_BAN:
            return False, f"Lương phải lớn hơn hoặc bằng lương cơ bản ({LUONG_CO_BAN:,}đ)"

        # chuẩn hóa
        user["luong"] = luong
        users.append(user)
        self.save_users(users)
        return True, "Thêm nhân viên thành công"

    # ====== UPDATE USER ======
    def update_user(self, ma_nv, new_data):
        users = self.load_users()

        # kiểm tra tồn tại
        idx = None
        for i,u in enumerate(users):
            if u["ma_nv"] == ma_nv:
                idx = i
                break
        if idx is None:
            return False, "Không tìm thấy nhân viên"

        # nếu đổi username hoặc ma_nv => không được trùng với các user khác
        for u in users:
            if u["ma_nv"] != ma_nv:
                if new_data.get("username") and new_data.get("username") == u.get("username"):
                    return False, "Username mới bị trùng"
                if new_data.get("ma_nv") and new_data.get("ma_nv") == u.get("ma_nv"):
                    return False, "Mã nhân viên mới bị trùng"

        # kiểm tra ngày vào làm
        if "ngay_vao_lam" in new_data:
            try:
                ngay = datetime.strptime(new_data["ngay_vao_lam"], "%Y-%m-%d").date()
            except Exception:
                return False, "Ngày vào làm phải theo định dạng YYYY-MM-DD"
            if ngay >= date.today():
                return False, "Ngày vào làm phải nhỏ hơn ngày hiện tại"

        # kiểm tra lương
        if "luong" in new_data:
            try:
                luong = int(new_data["luong"])
            except Exception:
                return False, "Lương phải là số nguyên"
            LUONG_CO_BAN = 1500000
            if luong <= 0:
                return False, "Lương phải > 0"
            if luong < LUONG_CO_BAN:
                return False, f"Lương phải lớn hơn hoặc bằng lương cơ bản ({LUONG_CO_BAN:,}đ)"
            new_data["luong"] = luong

        users[idx].update(new_data)
        self.save_users(users)
        return True, "Cập nhật nhân viên thành công"

    # ====== DELETE USER ======
    def delete_user(self, ma_nv, current_user_username=None):
        users = self.load_users()
        target = next((u for u in users if u["ma_nv"] == ma_nv), None)

        if not target:
            return False, "Không tìm thấy nhân viên"

        if current_user_username and target["username"] == current_user_username:
            return False, "Không thể xóa chính bạn"

        invoices = self.load_invoices()
        if any(inv.get("nguoi_username") == target["username"] for inv in invoices):
            return False, "Nhân viên đã có lịch sử bán hàng, không thể xóa"

        new_users = [u for u in users if u["ma_nv"] != ma_nv]
        self.save_users(new_users)
        return True, "Xóa nhân viên thành công"

    # ============ PRODUCTS ============
    def load_products(self):
        data = self.doc_json(self.products_file)

        # Chuyển khóa "ma" → "id" để tương thích code cũ
        for sp in data:
            if "ma" in sp:
                sp["id"] = sp["ma"]

        return data

    def save_products(self, d): self.luu_json(self.products_file, d)

    def add_product(self, p):
        prods = self.load_products()
        if any(x["id"] == p["id"] for x in prods):
            return False, "Mã sản phẩm đã tồn tại"
        prods.append(p)
        self.save_products(prods)
        return True, "Thêm sản phẩm thành công"

    def update_product(self, id_old, new_data):
        prods = self.load_products()
        for p in prods:
            if p["id"] == id_old:
                if new_data.get("id") and new_data["id"] != id_old:
                    if any(x["id"] == new_data["id"] for x in prods):
                        return False, "Mã mới bị trùng"
                p.update(new_data)
                self.save_products(prods)
                return True, "Cập nhật sản phẩm thành công"
        return False, "Không tìm thấy sản phẩm"

    def delete_product(self, prod_id):
        prods = self.load_products()

        invoices = self.load_invoices()
        for hd in invoices:
            if any(item.get("id") == prod_id for item in hd.get("chitiet", [])):
                return False, "Sản phẩm đã tồn tại trong hóa đơn, không thể xóa"

        new_list = [x for x in prods if x["id"] != prod_id]
        self.save_products(new_list)
        return True, "Xóa thành công"

    # ============ INVOICES ============
    def load_invoices(self): return self.doc_json(self.invoices_file)
    def save_invoices(self, d): self.luu_json(self.invoices_file, d)

    def add_invoice(self, invoice):
        h = self.load_invoices()
        h.append(invoice)
        self.save_invoices(h)
        return True


# ===================================================================
# ========================= ỨNG DỤNG GUI =============================
# ===================================================================
class UngDung(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Phần Mềm Quản Lý Bán Hàng")
        self.geometry("1200x750")

        self.dm = DataManager()
        self.user = None
        self.mode_kho = None
        self.mode_ns = None
        self.gio = []

        self.man_hinh_login()

    # ---------------- LOGIN ----------------
    def man_hinh_login(self):
        for w in self.winfo_children(): w.destroy()
        f = tk.Frame(self); f.pack(pady=80)

        tk.Label(f, text="ĐĂNG NHẬP", font=("Arial", 22, "bold")).pack(pady=10)
        tk.Label(f, text="User:").pack(); e_u = tk.Entry(f); e_u.pack()
        tk.Label(f, text="Pass:").pack(); e_p = tk.Entry(f, show="*"); e_p.pack()

        tk.Label(f, text="Vai trò:").pack()
        role_var = tk.StringVar(value="user")
        ttk.Combobox(f, textvariable=role_var, values=["admin","user"], state="readonly").pack(pady=5)

        def login(role_expected=None):
            username = e_u.get().strip()
            password = e_p.get().strip()
            if not username or not password:
                messagebox.showerror("Lỗi", "Nhập user & pass")
                return
            user = self.dm.find_user_by_username(username)
            if not user or user.get("password") != password:
                messagebox.showerror("Lỗi", "Sai thông tin đăng nhập")
                return
            if role_expected and user.get("role") != role_expected:
                messagebox.showerror("Lỗi", f"Tài khoản không thuộc vai trò {role_expected}")
                return
            if role_var.get() != user.get("role"):
                messagebox.showerror("Lỗi", "Bạn chọn sai vai trò")
                return
            self.user = user
            messagebox.showinfo("Chào", f"Xin chào {user.get('ten')}")
            self.man_hinh_chinh()

        tk.Button(f, text="Đăng nhập", bg="blue", fg="white", command=login).pack(pady=10)

    # ---------------- MAIN SCREEN ----------------
    def man_hinh_chinh(self):
        for w in self.winfo_children(): w.destroy()
        m = tk.Menu(self); self.config(menu=m)
        mn = tk.Menu(m, tearoff=0); m.add_cascade(label="Hệ thống", menu=mn)
        if self.user and self.user.get("role") == "admin":
            mn.add_command(label="📥 Nhập hàng API", command=self.goi_api)
        mn.add_command(label="Đăng xuất", command=self.dang_xuat)

        self.nb = ttk.Notebook(self); self.nb.pack(fill="both", expand=True)

        # ==== BÁN HÀNG ====
        self.tab_ban = tk.Frame(self.nb); self.nb.add(self.tab_ban, text="Bán Hàng"); self.build_ban_hang()
        # ==== LỊCH SỬ ====
        self.tab_ls = tk.Frame(self.nb); self.nb.add(self.tab_ls, text="Lịch Sử Hóa Đơn"); self.build_ls()
        # ==== KHO & NHÂN SỰ (ADMIN) ====
        if self.user and self.user.get("role") == "admin":
            self.tab_kho = tk.Frame(self.nb); self.nb.add(self.tab_kho, text="Quản Lý Kho"); self.build_kho()
            self.tab_ns = tk.Frame(self.nb); self.nb.add(self.tab_ns, text="Quản Lý Nhân Sự"); self.build_nhan_su()

    def dang_xuat(self):
        self.user = None
        self.man_hinh_login()

    def goi_api(self):
        try:
            import requests
            url = 'https://api.npoint.io/881fe47e8b6245bbe49a'
            r = requests.get(url)
            
            if r.status_code == 200:
                data = []
                json_response = r.json()
                
                # --- TẦNG 1: Xử lý danh sách ---
                if isinstance(json_response, list):
                    product_list = json_response
                else:
                    product_list = json_response.get('products', [])

                if not product_list:
                    messagebox.showinfo("Thông báo", "API rỗng.")
                    return

                # --- TẦNG 2: Vòng lặp xử lý ---
                for index, p in enumerate(product_list):
                    # 1. Lấy ID: Lấy trực tiếp chuỗi, không ép về int nữa
                    # Thử tìm các từ khóa: id, ma, code, productId...
                    raw_id = p.get('id') or p.get('ma') or p.get('code') or p.get('productId')
                    
                    if raw_id is not None:
                        # Nếu có ID, dùng luôn (chuyển sang chuỗi cho chắc chắn)
                        str_id = str(raw_id)
                    else:
                        # Nếu API hoàn toàn không có ID -> Mới dùng AUTO
                        str_id = f"SP_AUTO_{index}"

                    # 2. Lấy Tên 
                    #d   
                    raw_name = p.get('title') or p.get('ten') or p.get('name') or p.get('productName')
                    final_name = raw_name if raw_name else f"Sản phẩm {index}"

                    # 3. Lấy Số lượng (Mặc định 100 nếu không tìm thấy)
                    raw_stock = p.get('stock') or p.get('sl') or p.get('soluong') or p.get('quantity')
                    try:
                        final_stock = int(raw_stock)
                    except:
                        final_stock = 100 # <--- Điền 100 nếu không có số lượng

                    # 4. Lấy Giá (Không nhân 25000 nữa)
                    raw_price = p.get('price') or p.get('gia') or p.get('cost')
                    try:
                        final_price = int(raw_price)
                    except:
                        final_price = 0

                    # --- Thêm vào danh sách ---s
                    data.append({
                        'id': str_id,
                        'ma': str_id, 
                        'ten': final_name,
                        'sl': final_stock,
                        'gia': final_price
                    })
                
                # --- Lưu và thông báo ---
                self.dm.save_products(data)
                messagebox.showinfo("Thành công", f"Đã nhập {len(data)} sản phẩm!\n(Đã tự điền SL=100 nếu thiếu)")
                
                # Cập nhật giao diện
                self.load_sp()
                if hasattr(self, 'load_kho'): 
                    self.load_kho()

            else:
                messagebox.showerror("Lỗi", f"Lỗi tải API: {r.status_code}")
        except Exception as e:
            print("Lỗi:", e)
            messagebox.showerror("Lỗi Code", str(e))

    # ===================================================================
    # ========================== BÁN HÀNG ================================
    # ===================================================================
    def build_ban_hang(self):
        f1 = tk.LabelFrame(self.tab_ban, text="Kho hàng"); f1.pack(side="left", fill="both", expand=True)
        self.tv_ban = ttk.Treeview(f1, columns=("id","ten","sl","gia"), show="headings")
        for c,t in [("id","Mã"),("ten","Tên"),("sl","SL"),("gia","Giá")]:
            self.tv_ban.heading(c,text=t)
        self.tv_ban.pack(fill="both", expand=True)
        self.tv_ban.bind("<Double-1>", self.them_gio)

        f2 = tk.LabelFrame(self.tab_ban, text="Giỏ Hàng"); f2.pack(side="right", fill="both", expand=True)
        self.tv_gio = ttk.Treeview(f2, columns=("ten","sl","tt"), show="headings")
        for c in ["ten","sl","tt"]: self.tv_gio.heading(c,text=c)
        self.tv_gio.pack(fill="both", expand=True)
        self.lbl_tong = tk.Label(f2, text="Tổng: 0 VNĐ", fg="red", font=("Arial",14)); self.lbl_tong.pack(pady=5)
        tk.Button(f2, text="THANH TOÁN", bg="orange", command=self.thanh_toan).pack()
        tk.Button(f2, text="Xóa giỏ", command=self.xoa_gio).pack()
        self.load_sp()

    def load_sp(self):
        for r in self.tv_ban.get_children(): self.tv_ban.delete(r)
        for p in self.dm.load_products():
            self.tv_ban.insert("", "end", values=(p["id"], p["ten"], p["sl"], f"{p['gia']:,}"))

    def them_gio(self,e):
        v = self.tv_ban.item(self.tv_ban.focus(),"values")
        if not v: return
        id_sp, ten, ton, gia = v[0], v[1], int(v[2]), int(v[3].replace(",",""))
        top = tk.Toplevel(self); top.title("Thêm vào giỏ"); tk.Label(top, text=f"Sản phẩm: {ten}").pack()
        e_sl = tk.Entry(top); e_sl.pack(); e_sl.focus()
        def ok():
            try:
                sl = int(e_sl.get())
                if sl <= 0:
                    messagebox.showerror("Lỗi","Số lượng phải >0"); return
                if sl > ton:
                    messagebox.showerror("Lỗi","Không đủ hàng"); return
                self.gio.append({"id":id_sp,"ten":ten,"sl":sl,"gia":gia,"tt":sl*gia,"nguoi_username": self.user["username"]})
                self.update_gio(); top.destroy()
            except:
                messagebox.showerror("Lỗi","Số lượng không hợp lệ")
        tk.Button(top, text="OK", command=ok).pack()

    def update_gio(self):
        for r in self.tv_gio.get_children(): self.tv_gio.delete(r)
        tong = 0
        for i in self.gio:
            tong += i["tt"]
            self.tv_gio.insert("", "end", values=(i["ten"], i["sl"], f"{i['tt']:,}"))
        self.lbl_tong.config(text=f"Tổng: {tong:,} VNĐ"); self.tong_tien = tong

    def xoa_gio(self):
        self.gio = []; self.update_gio()

    def thanh_toan(self):
        if not self.gio: return
        invoices = self.dm.load_invoices()
        ma = f"HD{len(invoices)+1:03d}"
        hd = {"ma":ma,"nguoi":self.user["ten"],"nguoi_username":self.user["username"],
              "ngay": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "tong": self.tong_tien, "chitiet": self.gio}
        self.dm.add_invoice(hd)
        prods = self.dm.load_products()
        for g in self.gio:
            for p in prods:
                if p["id"] == g["id"]:
                    p["sl"] = max(0, p["sl"] - g["sl"])
        self.dm.save_products(prods)
        messagebox.showinfo("OK","Thanh toán thành công")
        self.gio = []; self.update_gio(); self.load_sp(); self.load_ls()

    # ===================================================================
    # ========================== LỊCH SỬ =================================
    # ===================================================================
    def xem_chi_tiet_hoa_don(self):
        sel = self.tv_ls.focus()
        if not sel:
            messagebox.showerror("Lỗi", "Vui lòng chọn một hóa đơn!")
            return

        values = self.tv_ls.item(sel, "values")
        if not values:
            messagebox.showerror("Lỗi", "Dữ liệu chọn không hợp lệ!")
            return
        ma_hd = values[0]  # cột đầu là mã hóa đơn

        # Load danh sách hóa đơn
        ds = self.dm.load_invoices()

        hd = None
        for x in ds:
            if x.get("ma") == ma_hd:
                hd = x
                break

        if hd is None:
            messagebox.showerror("Lỗi", "Không tìm thấy hóa đơn trong dữ liệu!")
            return

        # Tạo cửa sổ xem chi tiết
        w = tk.Toplevel(self)
        w.title(f"Chi tiết hóa đơn {ma_hd}")
        w.geometry("700x500")

        # -------- THÔNG TIN CHUNG ----------
        frame_info = tk.LabelFrame(w, text="Thông tin hóa đơn")
        frame_info.pack(fill="x", padx=10, pady=10)

        info_text = (
            f"Mã hóa đơn: {hd.get('ma')}\n"
            f"Nhân viên lập: {hd.get('nguoi')} ({hd.get('nguoi_username')})\n"
            f"Ngày lập: {hd.get('ngay')}\n"
            f"Tổng tiền: {hd.get('tong',0):,} VND"
        )
        tk.Label(frame_info, anchor="w", justify="left", text=info_text).pack(anchor="w", padx=10, pady=5)

        # -------- BẢNG CHI TIẾT ----------
        frame_ct = tk.LabelFrame(w, text="Danh sách sản phẩm")
        frame_ct.pack(fill="both", expand=True, padx=10, pady=10)

        tv = ttk.Treeview(frame_ct,
            columns=("ma", "ten", "sl", "gia", "tt"),
            show="headings"
        )
        tv.heading("ma", text="Mã SP")
        tv.heading("ten", text="Tên sản phẩm")
        tv.heading("sl", text="Số lượng")
        tv.heading("gia", text="Giá")
        tv.heading("tt", text="Thành tiền")

        tv.column("ma", width=90)
        tv.column("ten", width=230)
        tv.column("sl", width=80)
        tv.column("gia", width=120)
        tv.column("tt", width=120)

        tv.pack(fill="both", expand=True)

        # Đổ dữ liệu chi tiết sản phẩm
        # ghi chú: trong hóa đơn lưu ở key 'chitiet' với từng item có id,ten,sl,gia,tt
        for sp in hd.get("chitiet", []):
            ma_sp = sp.get("id") or sp.get("ma") or ""
            ten_sp = sp.get("ten","")
            sl_sp = sp.get("sl",0)
            gia_sp = sp.get("gia",0)
            tt_sp = sp.get("tt", sp.get("thanh_tien", sl_sp * gia_sp))
            tv.insert("", "end", values=(ma_sp, ten_sp, sl_sp, f"{gia_sp:,}", f"{tt_sp:,}"))

        tk.Button(w, text="Đóng", command=w.destroy).pack(pady=10)


    def build_ls(self):
        # tạo khu chứa nút và treeview
        f = tk.Frame(self.tab_ls); f.pack(fill="x", pady=5)
        tk.Button(f, text="Tải lại", command=self.load_ls).pack(side="left", padx=5)
        tk.Button(f, text="Xem chi tiết hóa đơn", command=self.xem_chi_tiet_hoa_don,bg="yellow").pack(side="left", padx=5)

        self.tv_ls = ttk.Treeview(self.tab_ls, columns=("ma","nguoi","ngay","tong"), show="headings")
        for c,t in [("ma","Mã"),("nguoi","Người"),("ngay","Ngày"),("tong","Tổng")]:
            self.tv_ls.heading(c,text=t)
            self.tv_ls.column(c, width=180)
        self.tv_ls.pack(fill="both", expand=True, padx=10, pady=6)
        self.load_ls()


    def load_ls(self):
        for r in self.tv_ls.get_children(): self.tv_ls.delete(r)
        for hd in self.dm.load_invoices():
            self.tv_ls.insert("", "end", values=(hd.get("ma"), hd.get("nguoi"), hd.get("ngay"), f"{hd.get('tong',0):,}"))

    # ===================================================================
    # ============================= KHO ==================================
    # ===================================================================
    def build_kho(self):
        f = tk.LabelFrame(self.tab_kho, text="Thông tin SP"); f.pack(fill="x")
        tk.Label(f, text="Mã").grid(row=0,column=0); self.k_ma = tk.Entry(f); self.k_ma.grid(row=0,column=1)
        tk.Label(f, text="Tên").grid(row=0,column=2); self.k_ten = tk.Entry(f); self.k_ten.grid(row=0,column=3)
        tk.Label(f, text="SL").grid(row=0,column=4); self.k_sl = tk.Entry(f); self.k_sl.grid(row=0,column=5)
        tk.Label(f, text="Giá").grid(row=0,column=6); self.k_gia = tk.Entry(f); self.k_gia.grid(row=0,column=7)
        tk.Button(f, text="Thêm", command=self.kho_them).grid(row=0,column=8)
        tk.Button(f, text="Sửa", command=self.kho_sua).grid(row=0,column=9)
        tk.Button(f, text="Xóa", command=self.kho_xoa).grid(row=0,column=10)
        tk.Button(f, text="Lưu", command=self.kho_luu).grid(row=0,column=11)
        self.tv_kho = ttk.Treeview(self.tab_kho, columns=("id","ten","sl","gia"), show="headings")
        for c in ["id","ten","sl","gia"]: self.tv_kho.heading(c,text=c)
        self.tv_kho.pack(fill="both", expand=True); self.tv_kho.bind("<<TreeviewSelect>>", self.chon_kho)
        self.load_kho()

    def load_kho(self):
        for r in self.tv_kho.get_children(): self.tv_kho.delete(r)
        for p in self.dm.load_products():
            self.tv_kho.insert("", "end", values=(p["id"], p["ten"], p["sl"], f"{p['gia']:,}"))

    def chon_kho(self, e):
        v = self.tv_kho.item(self.tv_kho.focus(),"values"); 
        if not v: return
        self.k_ma.delete(0,tk.END); self.k_ma.insert(0,v[0])
        self.k_ten.delete(0,tk.END); self.k_ten.insert(0,v[1])
        self.k_sl.delete(0,tk.END); self.k_sl.insert(0,v[2])
        self.k_gia.delete(0,tk.END); self.k_gia.insert(0,v[3].replace(",",""))

    def kho_them(self):
        self.mode_kho = "them"
        self.k_ma.delete(0,tk.END); self.k_ten.delete(0,tk.END); self.k_sl.delete(0, tk.END); self.k_gia.delete(0,tk.END)

    def kho_sua(self):
        v = self.tv_kho.item(self.tv_kho.focus(),"values")
        if not v:
            messagebox.showerror("Lỗi","Chọn sản phẩm để sửa"); return
        self.mode_kho = "sua"

    def kho_xoa(self):
        # Lấy dòng đang chọn
        sel = self.tv_kho.selection()
        if not sel:
            messagebox.showerror("Lỗi", "Chọn 1 sản phẩm để xóa")
            return

        v = self.tv_kho.item(sel[0], "values")
        ma = v[0]

        ok = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa SP {ma}?")
        if not ok:
            return

        success, msg = self.dm.delete_product(ma)
        if success:
            messagebox.showinfo("OK", msg)
            self.load_kho()     # cập nhật tab kho
            self.load_sp()      # cập nhật tab bán hàng

        else:
            messagebox.showerror("Lỗi", msg)


    def kho_luu(self):
        id_sp = self.k_ma.get().strip(); ten = self.k_ten.get().strip()
        try:
            sl = int(self.k_sl.get().strip()); gia = int(self.k_gia.get().strip())
        except:
            messagebox.showerror("Lỗi","SL & Giá phải là số"); return
        if not id_sp or not ten:
            messagebox.showerror("Lỗi","Mã & tên không được rỗng"); return
        data = {"id":id_sp,"ten":ten,"sl":sl,"gia":gia}
        if self.mode_kho == "them":
            ok,msg = self.dm.add_product(data)
        else:
            # dùng id hiện tại làm khóa update
            ok,msg = self.dm.update_product(id_sp, data)
        if not ok: messagebox.showerror("Lỗi",msg); return
        messagebox.showinfo("OK",msg); self.load_kho(); self.mode_kho = None

    # ===================================================================
    # ========================= NHÂN SỰ (ADMIN) ===========================
    # ===================================================================
    def build_nhan_su(self):
        f = tk.LabelFrame(self.tab_ns, text="Thông tin Nhân sự")
        f.pack(fill="x", padx=10, pady=6)

        # Dòng 0
        tk.Label(f, text="Mã NV:").grid(row=0, column=0)
        self.n_ma = tk.Entry(f); self.n_ma.grid(row=0, column=1)

        tk.Label(f, text="User:").grid(row=0, column=2)
        self.n_u = tk.Entry(f); self.n_u.grid(row=0, column=3)

        tk.Label(f, text="Pass:").grid(row=0, column=4)
        self.n_p = tk.Entry(f, show="*"); self.n_p.grid(row=0, column=5)

        # Dòng 1
        tk.Label(f, text="Tên:").grid(row=1, column=0)
        self.n_t = tk.Entry(f); self.n_t.grid(row=1, column=1)

        tk.Label(f, text="Role:").grid(row=1, column=2)
        self.n_r = ttk.Combobox(f, values=["admin","user"], state="readonly")
        self.n_r.grid(row=1, column=3)

        # Dòng 2
        tk.Label(f, text="Ngày vào làm (YYYY-MM-DD):").grid(row=2, column=0)
        self.n_ngay = tk.Entry(f); self.n_ngay.grid(row=2, column=1)

        tk.Label(f, text="Lương:").grid(row=2, column=2)
        self.n_luong = tk.Entry(f); self.n_luong.grid(row=2, column=3)

        # Dòng 3: lương cơ bản (readonly)
        tk.Label(f, text="Lương cơ bản:").grid(row=3, column=0)
        self.n_lcb = tk.Entry(f); self.n_lcb.grid(row=3, column=1)
        self.n_lcb.insert(0, "1500000"); self.n_lcb.config(state="readonly")

        # Nút chức năng
        tk.Button(f, text="Thêm", command=self.ns_them).grid(row=4, column=0, pady=6)
        tk.Button(f, text="Sửa",  command=self.ns_sua).grid(row=4, column=1)
        tk.Button(f, text="Xóa",  command=self.ns_xoa).grid(row=4, column=2)
        tk.Button(f, text="Lưu",  command=self.ns_luu).grid(row=4, column=3)

        # Treeview nhân sự
        cols = ("ma","user","pass","ten","role","ngay","luong")
        self.tv_ns = ttk.Treeview(self.tab_ns, columns=cols, show="headings")
        headers = [("ma","Mã NV"),("user","User"),("pass","Pass"),("ten","Tên"),("role","Role"),("ngay","Ngày vào"),("luong","Lương")]
        for c, h in headers:
            self.tv_ns.heading(c, text=h)
            self.tv_ns.column(c, width=120)
        self.tv_ns.pack(fill="both", expand=True, padx=10, pady=6)
        self.tv_ns.bind("<<TreeviewSelect>>", self.chon_ns)

        self.mode_ns = None
        self.load_ns()

    def load_ns(self):
        for r in self.tv_ns.get_children():
            self.tv_ns.delete(r)
        for u in self.dm.load_users():
            self.tv_ns.insert("", "end", values=(
                u.get("ma_nv",""), u.get("username",""), u.get("password",""),
                u.get("ten",""), u.get("role",""), u.get("ngay_vao_lam",""), u.get("luong",0)
            ))

    def chon_ns(self, event=None):
        v = self.tv_ns.item(self.tv_ns.focus(), "values")
        if not v: return
        self.n_ma.delete(0, tk.END); self.n_ma.insert(0, v[0])
        self.n_u.delete(0, tk.END); self.n_u.insert(0, v[1])
        # không hiển thị pass cũ trong entry (bảo mật) — user có thể nhập pass mới nếu muốn
        self.n_p.delete(0, tk.END)
        self.n_t.delete(0, tk.END); self.n_t.insert(0, v[3])
        self.n_r.set(v[4])
        self.n_ngay.delete(0, tk.END); self.n_ngay.insert(0, v[5])
        self.n_luong.delete(0, tk.END); self.n_luong.insert(0, v[6])

    def ns_them(self):
        self.mode_ns = "them"
        self.n_ma.delete(0, tk.END); self.n_u.delete(0, tk.END); self.n_p.delete(0, tk.END)
        self.n_t.delete(0, tk.END); self.n_r.set("user"); self.n_ngay.delete(0, tk.END); self.n_luong.delete(0, tk.END)
        self.n_ma.focus()

    def ns_sua(self):
        v = self.tv_ns.item(self.tv_ns.focus(), "values")
        if not v:
            messagebox.showerror("Lỗi", "Chọn nhân viên để sửa")
            return
        self.mode_ns = "sua"

    def ns_luu(self):
        ma = self.n_ma.get().strip()
        user = self.n_u.get().strip()
        pwd = self.n_p.get().strip()
        ten = self.n_t.get().strip()
        role = self.n_r.get().strip()
        ngay = self.n_ngay.get().strip()
        luong_text = self.n_luong.get().strip()
        LUONG_CO_BAN = 1500000

        # kiểm input cơ bản
        if not ma or not user or not ten or not role or not ngay or not luong_text:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        # kiểm định dạng ngày
        try:
            ngay_dt = datetime.strptime(ngay, "%Y-%m-%d").date()
        except:
            messagebox.showerror("Lỗi", "Ngày vào làm phải theo định dạng YYYY-MM-DD")
            return
        if ngay_dt >= date.today():
            messagebox.showerror("Lỗi", "Ngày vào làm phải nhỏ hơn ngày hiện tại")
            return

        # kiểm lương
        try:
            luong = int(luong_text)
        except:
            messagebox.showerror("Lỗi", "Lương phải là số nguyên")
            return
        if luong <= 0:
            messagebox.showerror("Lỗi", "Lương phải > 0"); return
        if luong < LUONG_CO_BAN:
            messagebox.showerror("Lỗi", f"Lương phải >= {LUONG_CO_BAN:,}"); return

        user_data = {
            "ma_nv": ma, "username": user, "password": pwd if pwd else None,
            "ten": ten, "role": role, "ngay_vao_lam": ngay, "luong": luong
        }

        # Nếu sửa và không nhập mật khẩu mới => giữ pass cũ
        if self.mode_ns == "sua" and not pwd:
            old = self.dm.find_user_by_ma(ma)
            if old:
                user_data["password"] = old.get("password", "")

        if self.mode_ns == "them":
            ok, msg = self.dm.add_user(user_data)
        else:
            # ns_luu khi sửa: dùng ma cũ làm khóa
            sel = self.tv_ns.item(self.tv_ns.focus(), "values")
            ma_cu = sel[0] if sel else ma
            ok, msg = self.dm.update_user(ma_cu, user_data)

        if not ok:
            messagebox.showerror("Lỗi", msg); return

        messagebox.showinfo("OK", msg)
        self.mode_ns = None
        self.load_ns()

    def ns_xoa(self):
        v = self.tv_ns.item(self.tv_ns.focus(), "values")
        if not v:
            messagebox.showerror("Lỗi", "Chọn nhân viên để xóa"); return
        ma = v[0]
        if not messagebox.askyesno("Xóa", f"Bạn có muốn xóa nhân viên {ma}?"):
            return
        ok, msg = self.dm.delete_user(ma, current_user_username=self.user.get("username") if self.user else None)
        if not ok:
            messagebox.showerror("Lỗi", msg); return
        messagebox.showinfo("OK", msg); self.load_ns()


# ============================
# CHẠY CHƯƠNG TRÌNH
# ============================
if __name__ == "__main__":
    UngDung().mainloop()
