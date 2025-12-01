import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import hashlib
import requests
from datetime import datetime

# =========================================================================
# PHẦN 1: BACKEND (XỬ LÝ FILE & API)
# =========================================================================

class HeThongBaoMat:
    def __init__(self, file_user='users.json'):
        self.file_user = file_user
        self.khoi_tao()

    def ma_hoa(self, mk):
        # SỬA: Không mã hóa nữa, trả về nguyên mật khẩu gốc
        return mk 

    def doc_user(self):
        if not os.path.exists(self.file_user): return []
        try:
            with open(self.file_user, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []

    def luu_user(self, users):
        with open(self.file_user, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4, ensure_ascii=False)

    def khoi_tao(self):
        if not os.path.exists(self.file_user):
            # Lưu pass dạng thường
            self.luu_user([
                {"username": "admin", "password": "admin123", "role": "admin", "ten": "Quản Trị Viên"},
                {"username": "nv1", "password": "user123", "role": "user", "ten": "Nhân Viên Mẫu"}
            ])

    def dang_nhap(self, u, p):
        # So sánh trực tiếp pass nhập vào với pass trong file
        for user in self.doc_user():
            if user['username'] == u and user['password'] == p: return user
        return None

    def dang_ky(self, u, p, r, t):
        users = self.doc_user()
        for x in users:
            if x['username'] == u: return False, "Tài khoản đã tồn tại!"
        # Lưu trực tiếp p (pass thường)
        users.append({"username": u, "password": p, "role": r, "ten": t})
        self.luu_user(users)
        return True, "Thêm thành công!"

    def xoa_user(self, u):
        users = self.doc_user()
        moi = [x for x in users if x['username'] != u]
        if len(moi) < len(users):
            self.luu_user(moi); return True
        return False

# --- HÀM JSON CHUNG ---
def doc_json(f):
    if not os.path.exists(f): return []
    try:
        with open(f, 'r', encoding='utf-8') as file: return json.load(file)
    except: return []

def luu_json(f, d):
    with open(f, 'w', encoding='utf-8') as file: json.dump(d, file, ensure_ascii=False, indent=4)

def api_nhap_hang():
    try:
        r = requests.get("https://dummyjson.com/products")
        if r.status_code == 200:
            data = []
            for p in r.json()['products']:
                data.append({"id": f"SP{p['id']:03d}", "ten": p['title'], "sl": p['stock'], "gia": int(p['price']*25000)})
            luu_json('products.json', data)
            return True, f"Đã nhập {len(data)} SP!"
        return False, "Lỗi API"
    except Exception as e: return False, str(e)

# =========================================================================
# PHẦN 2: GIAO DIỆN (GUI)
# =========================================================================

class UngDung(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Phần Mềm Quản Lý Bán Hàng")
        self.geometry("1200x750")
        self.auth = HeThongBaoMat()
        self.user = None
        if not os.path.exists('products.json'): luu_json('products.json', [])
        self.man_hinh_login()

    def man_hinh_login(self):
        for w in self.winfo_children(): w.destroy()
        f = tk.Frame(self); f.pack(pady=100)
        tk.Label(f, text="ĐĂNG NHẬP", font=("Arial", 20, "bold")).pack(pady=10)
        
        tk.Label(f, text="User:").pack(); e_u = tk.Entry(f); e_u.pack(pady=5)
        tk.Label(f, text="Pass:").pack(); e_p = tk.Entry(f, show="*"); e_p.pack(pady=5)
        
        def login():
            u = self.auth.dang_nhap(e_u.get(), e_p.get())
            if u: 
                self.user = u
                messagebox.showinfo("Chào", f"Xin chào {u['ten']}")
                self.man_hinh_chinh()
            else: messagebox.showerror("Lỗi", "Sai thông tin")
            
        tk.Button(f, text="Đăng nhập", bg="blue", fg="white", command=login).pack(pady=20)
        tk.Label(f, text="Admin: admin/admin123 | NV: nv1/user123").pack()

    def man_hinh_chinh(self):
        for w in self.winfo_children(): w.destroy()
        
        # Menu
        m = tk.Menu(self); self.config(menu=m)
        sys = tk.Menu(m, tearoff=0); m.add_cascade(label="Hệ thống", menu=sys)
        if self.user['role'] == 'admin':
            sys.add_command(label="📥 Nhập hàng API", command=self.goi_api)
        sys.add_command(label="Đăng xuất", command=self.dang_xuat)

        # Notebook
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Bán Hàng
        self.tab_ban = tk.Frame(self.nb); self.nb.add(self.tab_ban, text="Bán Hàng")
        self.build_ban_hang()

        # Tab 2: Lịch sử
        self.tab_ls = tk.Frame(self.nb); self.nb.add(self.tab_ls, text="Lịch Sử Hóa Đơn")
        self.build_lich_su()

        # Tab 3 & 4: Admin Only
        if self.user['role'] == 'admin':
            # Tab Kho
            self.tab_kho = tk.Frame(self.nb)
            self.nb.add(self.tab_kho, text="Quản Lý Kho")
            self.build_kho()

            # Tab Nhân sự
            self.tab_ns = tk.Frame(self.nb)
            self.nb.add(self.tab_ns, text="Quản Lý Nhân Sự")
            self.build_nhan_su()

    def dang_xuat(self):
        self.user = None; self.config(menu=""); self.man_hinh_login()

    def goi_api(self):
        ok, msg = api_nhap_hang()
        messagebox.showinfo("TB", msg)
        if ok: self.load_sp(); self.load_kho()

    # --- LOGIC BÁN HÀNG ---
    def build_ban_hang(self):
        f1 = tk.LabelFrame(self.tab_ban, text="Kho Hàng"); f1.pack(side="left", fill="both", expand=True)
        self.tv_ban = ttk.Treeview(f1, columns=("id", "ten", "sl", "gia"), show="headings")
        for c, t in [("id","Mã"), ("ten","Tên"), ("sl","Tồn"), ("gia","Giá")]:
            self.tv_ban.heading(c, text=t)
            self.tv_ban.column(c, width=60)
        self.tv_ban.pack(fill="both", expand=True)
        self.tv_ban.bind("<Double-1>", self.them_gio)

        f2 = tk.LabelFrame(self.tab_ban, text="Giỏ Hàng"); f2.pack(side="right", fill="both", expand=True)
        self.tv_gio = ttk.Treeview(f2, columns=("ten", "sl", "tt"), show="headings")
        self.tv_gio.heading("ten", text="Tên"); self.tv_gio.heading("sl", text="SL"); self.tv_gio.heading("tt", text="Thành tiền")
        self.tv_gio.pack(fill="both", expand=True)
        
        self.lbl_tong = tk.Label(f2, text="Tổng: 0 VNĐ", font=("bold", 14), fg="red"); self.lbl_tong.pack(pady=10)
        tk.Button(f2, text="THANH TOÁN", bg="orange", command=self.thanh_toan).pack(pady=5)
        tk.Button(f2, text="Xóa Giỏ", command=self.xoa_gio).pack(pady=5)
        self.gio = []; self.load_sp()

    def load_sp(self):
        for r in self.tv_ban.get_children(): self.tv_ban.delete(r)
        for p in doc_json('products.json'):
            self.tv_ban.insert("", "end", values=(p['id'], p['ten'], p['sl'], f"{p['gia']:,}"))

    def them_gio(self, e):
        v = self.tv_ban.item(self.tv_ban.focus(), 'values')
        if not v: return
        id_sp, ten, ton, gia = v[0], v[1], int(v[2]), int(v[3].replace(",",""))
        
        top = tk.Toplevel(self); top.geometry("200x100")
        tk.Label(top, text="Số lượng:").pack()
        e_sl = tk.Entry(top); e_sl.pack(); e_sl.focus()
        def ok():
            try:
                sl = int(e_sl.get())
                if sl > ton: messagebox.showerror("Lỗi", "Không đủ hàng"); return
                self.gio.append({"id": id_sp, "ten": ten, "sl": sl, "gia": gia, "tt": sl*gia})
                self.update_gio(); top.destroy()
            except: pass
        tk.Button(top, text="OK", command=ok).pack()

    def update_gio(self):
        for r in self.tv_gio.get_children(): self.tv_gio.delete(r)
        tong = 0
        for i in self.gio:
            self.tv_gio.insert("", "end", values=(i['ten'], i['sl'], f"{i['tt']:,}"))
            tong += i['tt']
        self.lbl_tong.config(text=f"Tổng: {tong:,} VNĐ"); self.tong_tien = tong

    def xoa_gio(self): self.gio = []; self.update_gio()

    def thanh_toan(self):
        if not self.gio: return
        hds = doc_json('hoa_don.json')
        ma = f"HD{len(hds)+1:03d}"
        hds.append({"ma": ma, "nguoi": self.user['ten'], "ngay": datetime.now().strftime("%Y-%m-%d"), "tong": self.tong_tien, "chitiet": self.gio})
        luu_json('hoa_don.json', hds)
        
        prods = doc_json('products.json')
        for g in self.gio:
            for p in prods:
                if p['id'] == g['id']: p['sl'] -= g['sl']
        luu_json('products.json', prods)
        
        messagebox.showinfo("OK", "Thanh toán xong!"); self.xoa_gio(); self.load_sp(); self.load_ls()

    # --- LOGIC LỊCH SỬ ---
    def build_lich_su(self):
        f = tk.Frame(self.tab_ls); f.pack(fill="x", padx=10, pady=5)
        tk.Button(f, text="Tải lại", command=self.load_ls).pack(side="left")
        tk.Button(f, text="Xem Chi Tiết", bg="yellow", command=self.xem_ct).pack(side="left", padx=10)
        if self.user['role'] == 'admin':
            tk.Button(f, text="Xóa", bg="red", fg="white", command=self.xoa_ls).pack(side="right")
            
        self.tv_ls = ttk.Treeview(self.tab_ls, columns=("ma", "nguoi", "ngay", "tong"), show="headings")
        for c, t in [("ma","Mã"), ("nguoi","Người lập"), ("ngay","Ngày"), ("tong","Tổng tiền")]:
            self.tv_ls.heading(c, text=t)
        self.tv_ls.pack(fill="both", expand=True, padx=10)
        self.load_ls()

    def load_ls(self):
        for r in self.tv_ls.get_children(): self.tv_ls.delete(r)
        for h in doc_json('hoa_don.json'):
            self.tv_ls.insert("", "end", values=(h['ma'], h['nguoi'], h['ngay'], f"{h['tong']:,}"))

    def xem_ct(self):
        v = self.tv_ls.item(self.tv_ls.focus(), 'values')
        if not v: return
        hd = next((x for x in doc_json('hoa_don.json') if x['ma'] == v[0]), None)
        top = tk.Toplevel(self); top.title("Chi tiết"); top.geometry("500x300")
        tv = ttk.Treeview(top, columns=("ten", "sl", "gia", "tt"), show="headings")
        for c in ["ten", "sl", "gia", "tt"]: tv.heading(c, text=c)
        tv.pack(fill="both", expand=True)
        for i in hd['chitiet']: tv.insert("", "end", values=(i['ten'], i['sl'], f"{i['gia']:,}", f"{i['tt']:,}"))

    def xoa_ls(self):
        v = self.tv_ls.item(self.tv_ls.focus(), 'values')
        if v and messagebox.askyesno("Xóa", "Xóa hóa đơn?"):
            luu_json('hoa_don.json', [h for h in doc_json('hoa_don.json') if h['ma'] != v[0]])
            self.load_ls()

    # --- LOGIC KHO (ADMIN) - ĐÃ SỬA LỖI GRID ---
    def build_kho(self):
        f = tk.LabelFrame(self.tab_kho, text="Thông tin"); f.pack(fill="x", padx=10)
        # Sử dụng row=, column= rõ ràng
        tk.Label(f, text="Mã:").grid(row=0, column=0); self.k_ma=tk.Entry(f); self.k_ma.grid(row=0, column=1)
        tk.Label(f, text="Tên:").grid(row=0, column=2); self.k_ten=tk.Entry(f); self.k_ten.grid(row=0, column=3)
        tk.Label(f, text="SL:").grid(row=0, column=4); self.k_sl=tk.Entry(f); self.k_sl.grid(row=0, column=5)
        tk.Label(f, text="Giá:").grid(row=0, column=6); self.k_gia=tk.Entry(f); self.k_gia.grid(row=0, column=7)
        tk.Button(f, text="Lưu", command=self.luu_kho).grid(row=0, column=8, padx=5)
        tk.Button(f, text="Xóa", command=self.xoa_kho).grid(row=0, column=9)
        
        self.tv_kho = ttk.Treeview(self.tab_kho, columns=("id", "ten", "sl", "gia"), show="headings")
        for c in ["id", "ten", "sl", "gia"]: self.tv_kho.heading(c, text=c)
        self.tv_kho.pack(fill="both", expand=True, padx=10)
        self.tv_kho.bind("<<TreeviewSelect>>", self.chon_kho)
        self.load_kho()

    def load_kho(self):
        for r in self.tv_kho.get_children(): self.tv_kho.delete(r)
        for p in doc_json('products.json'):
            self.tv_kho.insert("", "end", values=(p['id'], p['ten'], p['sl'], f"{p['gia']:,}"))

    def chon_kho(self, e):
        v = self.tv_kho.item(self.tv_kho.focus(), 'values')
        if v:
            self.k_ma.delete(0,tk.END); self.k_ma.insert(0,v[0])
            self.k_ten.delete(0,tk.END); self.k_ten.insert(0,v[1])
            self.k_sl.delete(0,tk.END); self.k_sl.insert(0,v[2])
            self.k_gia.delete(0,tk.END); self.k_gia.insert(0,v[3].replace(",",""))

    def luu_kho(self):
        ma, ten = self.k_ma.get(), self.k_ten.get()
        try: sl, gia = int(self.k_sl.get()), int(self.k_gia.get())
        except: return
        ds = doc_json('products.json'); found=False
        for p in ds:
            if p['id'] == ma: p['ten']=ten; p['sl']=sl; p['gia']=gia; found=True
        if not found: ds.append({"id":ma, "ten":ten, "sl":sl, "gia":gia})
        luu_json('products.json', ds); self.load_kho(); self.load_sp()

    def xoa_kho(self):
        luu_json('products.json', [p for p in doc_json('products.json') if p['id'] != self.k_ma.get()])
        self.load_kho(); self.load_sp()

    # --- LOGIC NHÂN SỰ (ADMIN) - ĐÃ SỬA LỖI GRID ---
    def build_nhan_su(self):
        f = tk.LabelFrame(self.tab_ns, text="Thông tin"); f.pack(fill="x", padx=10)
        # Sử dụng row=, column= rõ ràng
        tk.Label(f, text="User:").grid(row=0, column=0); self.n_u=tk.Entry(f); self.n_u.grid(row=0, column=1)
        tk.Label(f, text="Pass:").grid(row=0, column=2); self.n_p=tk.Entry(f); self.n_p.grid(row=0, column=3)
        tk.Label(f, text="Tên:").grid(row=1, column=0); self.n_t=tk.Entry(f); self.n_t.grid(row=1, column=1)
        tk.Label(f, text="Role:").grid(row=1, column=2); self.n_r=tk.Entry(f); self.n_r.grid(row=1, column=3)
        tk.Button(f, text="Thêm", command=self.them_ns).grid(row=2, column=0, pady=5)
        tk.Button(f, text="Xóa", command=self.xoa_ns).grid(row=2, column=1)
        
        self.tv_ns = ttk.Treeview(self.tab_ns, columns=("u", "p", "t", "r"), show="headings")
        for c in ["u", "p", "t", "r"]: self.tv_ns.heading(c, text=c)
        self.tv_ns.pack(fill="both", expand=True, padx=10)
        self.tv_ns.bind("<<TreeviewSelect>>", self.chon_ns)
        self.load_ns()

    def load_ns(self):
        for r in self.tv_ns.get_children(): self.tv_ns.delete(r)
        for u in self.auth.doc_user():
            self.tv_ns.insert("", "end", values=(u['username'], u['password'], u.get('ten',''), u['role']))

    def chon_ns(self, e):
        v = self.tv_ns.item(self.tv_ns.focus(), 'values')
        if v:
            self.n_u.delete(0,tk.END); self.n_u.insert(0,v[0])
            self.n_p.delete(0,tk.END)
            self.n_t.delete(0,tk.END); self.n_t.insert(0,v[2])
            self.n_r.delete(0,tk.END); self.n_r.insert(0,v[3])

    def them_ns(self):
        self.auth.dang_ky(self.n_u.get(), self.n_p.get(), self.n_r.get(), self.n_t.get())
        self.load_ns()

    def xoa_ns(self):
        if self.n_u.get() != self.user['username']:
            self.auth.xoa_user(self.n_u.get()); self.load_ns()

if __name__ == "__main__":
    app = UngDung()
    app.mainloop()