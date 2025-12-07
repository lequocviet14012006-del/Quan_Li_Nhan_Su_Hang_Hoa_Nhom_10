import tkinter as tk
from tkinter import ttk, messagebox
import json, os
from datetime import datetime
import requests

# ==============================
# CẤU HÌNH FILE DỮ LIỆU
# ==============================
FILE_USER = "users.json"
FILE_SP   = "san_pham.json"
FILE_HD   = "hoa_don.json"
FILE_SP_BAK = "san_pham_backup.json"   # backup dùng cho nút QUAY LẠI (Undo) khi xóa kho


class UngDung:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Phần Mềm Quản Lý Bán Hàng (Pro Simple)")
        self.root.geometry("1000x700")

        # trạng thái phiên làm việc (không global)
        self.nguoi_dang_nhap = None
        self.gio_hang = []          # [{id, ten, sl, gia, tt}]

        # chế độ thao tác
        self.che_do_kho = ""
        self.che_do_ns = ""

        # placeholders widget (để tránh None trong lúc tạo UI)
        self.entry_user = self.entry_pass = self.combo_role = None

        self.tree_ban_hang = None
        self.tree_gio = None
        self.lbl_tong_tien = None

        self.tree_lich_su = None

        self.e_k_ma = self.e_k_ten = self.e_k_sl = self.e_k_gia = None
        self.tree_kho = None

        self.e_n_ma = self.e_n_user = self.e_n_pass = None
        self.e_n_ten = self.e_n_ngay = self.e_n_luong = None
        self.c_n_role = None
        self.tree_ns = None

        self.khoi_tao_du_lieu()
        self.hien_thi_manh_hinh_login()

    # ==============================
    # TIỆN ÍCH FILE JSON + CHUẨN HÓA DỮ LIỆU
    # ==============================
    def doc_file(self, ten_file):
        if not os.path.exists(ten_file):
            return []
        try:
            with open(ten_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def ghi_file(self, ten_file, du_lieu):
        with open(ten_file, "w", encoding="utf-8") as f:
            json.dump(du_lieu, f, ensure_ascii=False, indent=4)

    def khoi_tao_du_lieu(self):
        # users mặc định
        if not os.path.exists(FILE_USER):
            users = [
                {"ma_nv": "NV000", "username": "admin", "password": "123", "role": "admin",
                 "ten": "Quản Trị Viên", "ngay_vao_lam": "2020-01-01", "luong": 2000000},
                {"ma_nv": "NV001", "username": "nv1", "password": "123", "role": "user",
                 "ten": "Nhân Viên", "ngay_vao_lam": "2022-01-01", "luong": 1800000},
            ]
            self.ghi_file(FILE_USER, users)

        # products + invoices mặc định rỗng
        if not os.path.exists(FILE_SP):
            self.ghi_file(FILE_SP, [])
        if not os.path.exists(FILE_HD):
            self.ghi_file(FILE_HD, [])

        # Chuẩn hóa dữ liệu nếu file đã tồn tại nhưng thiếu key
        self.chuan_hoa_users()
        self.chuan_hoa_products()

    def chuan_hoa_users(self):
        ds = self.doc_file(FILE_USER)
        thay_doi = False

        # Bảo đảm mỗi bản ghi có ma_nv (nếu thiếu sẽ tự sinh NVxxx)
        used = set()
        for u in ds:
            if "ma_nv" in u and u["ma_nv"]:
                used.add(u["ma_nv"])

        def next_nv():
            i = 0
            while True:
                code = f"NV{str(i).zfill(3)}"
                if code not in used:
                    used.add(code)
                    return code
                i += 1

        for u in ds:
            if not u.get("ma_nv"):
                u["ma_nv"] = next_nv()
                thay_doi = True

            # chuẩn key cũ/khác tên (nếu có) -> ưu tiên giữ nguyên, nhưng đảm bảo tồn tại
            u.setdefault("username", u.get("user", ""))
            u.setdefault("password", u.get("pass", ""))
            u.setdefault("role", "user")
            u.setdefault("ten", "")
            u.setdefault("ngay_vao_lam", u.get("ngay_vao", "2000-01-01"))
            u.setdefault("luong", 1500000)

        if thay_doi:
            self.ghi_file(FILE_USER, ds)

    def chuan_hoa_products(self):
        ds = self.doc_file(FILE_SP)
        thay_doi = False
        for p in ds:
            # cho phép file cũ dùng "ma" thay "id"
            if "id" not in p and "ma" in p:
                p["id"] = p["ma"]
                thay_doi = True
            if "ten" not in p and "name" in p:
                p["ten"] = p["name"]
                thay_doi = True
            p.setdefault("sl", 0)
            p.setdefault("gia", 0)
        if thay_doi:
            self.ghi_file(FILE_SP, ds)

    # ==============================
    # ĐĂNG NHẬP / ĐĂNG XUẤT
    # ==============================
    def dang_nhap(self):
        user = (self.entry_user.get() or "").strip()
        pw = (self.entry_pass.get() or "").strip()
        role = (self.combo_role.get() or "").strip()

        ds = self.doc_file(FILE_USER)
        tim = next((u for u in ds if u.get("username") == user and u.get("password") == pw), None)

        if not tim:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu")
            return
        if tim.get("role") != role:
            messagebox.showerror("Lỗi", "Sai vai trò (Role)")
            return

        self.nguoi_dang_nhap = tim
        self.gio_hang = []
        messagebox.showinfo("Xin chào", f"Chào mừng {tim.get('ten','')}")
        self.hien_thi_manh_hinh_chinh()

    def dang_xuat(self):
        self.nguoi_dang_nhap = None
        self.gio_hang = []
        self.hien_thi_manh_hinh_login()

    # ==============================
    # GIAO DIỆN LOGIN
    # ==============================
    def xoa_man_hinh(self):
        for w in self.root.winfo_children():
            w.destroy()

    def hien_thi_manh_hinh_login(self):
        self.xoa_man_hinh()

        khung = tk.Frame(self.root)
        khung.pack(pady=50)

        tk.Label(khung, text="ĐĂNG NHẬP HỆ THỐNG", font=("Arial", 16, "bold")).pack(pady=10)

        tk.Label(khung, text="Username:").pack()
        self.entry_user = tk.Entry(khung)
        self.entry_user.pack()

        tk.Label(khung, text="Password:").pack()
        self.entry_pass = tk.Entry(khung, show="*")
        self.entry_pass.pack()

        tk.Label(khung, text="Vai trò:").pack()
        self.combo_role = ttk.Combobox(khung, values=["admin", "user"], state="readonly")
        self.combo_role.current(1)
        self.combo_role.pack(pady=5)

        tk.Button(khung, text="Đăng nhập", bg="blue", fg="white", command=self.dang_nhap).pack(pady=10)

    # ==============================
    # MÀN HÌNH CHÍNH (TABS)
    # ==============================
    def hien_thi_manh_hinh_chinh(self):
        self.xoa_man_hinh()

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        menu_ht = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hệ thống", menu=menu_ht)

        if self.nguoi_dang_nhap and self.nguoi_dang_nhap.get("role") == "admin":
            menu_ht.add_command(label="Tải API Sản phẩm", command=self.nap_du_lieu_api)
        menu_ht.add_separator()
        menu_ht.add_command(label="Đăng xuất", command=self.dang_xuat)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        tab_ban = tk.Frame(notebook)
        notebook.add(tab_ban, text="Bán Hàng")
        self.xay_dung_tab_ban_hang(tab_ban)

        tab_ls = tk.Frame(notebook)
        notebook.add(tab_ls, text="Lịch Sử Hóa Đơn")
        self.xay_dung_tab_lich_su(tab_ls)

        if self.nguoi_dang_nhap.get("role") == "admin":
            tab_kho = tk.Frame(notebook)
            notebook.add(tab_kho, text="Quản Lý Kho")
            self.xay_dung_tab_kho(tab_kho)

            tab_ns = tk.Frame(notebook)
            notebook.add(tab_ns, text="Quản Lý Nhân Sự")
            self.xay_dung_tab_nhan_su(tab_ns)

    # ==============================
    # TAB BÁN HÀNG
    # ==============================
    def xay_dung_tab_ban_hang(self, parent):
        f_trai = tk.LabelFrame(parent, text="Danh sách sản phẩm")
        f_trai.pack(side="left", fill="both", expand=True)

        self.tree_ban_hang = ttk.Treeview(f_trai, columns=("id", "ten", "sl", "gia"), show="headings")
        for c, t, w in [("id", "Mã", 70), ("ten", "Tên SP", 200), ("sl", "Tồn kho", 80), ("gia", "Giá bán", 120)]:
            self.tree_ban_hang.heading(c, text=t)
            self.tree_ban_hang.column(c, width=w)
        self.tree_ban_hang.pack(fill="both", expand=True)
        self.tree_ban_hang.bind("<Double-1>", self.them_vao_gio)

        f_phai = tk.LabelFrame(parent, text="Giỏ hàng")
        f_phai.pack(side="right", fill="both", expand=True)

        self.tree_gio = ttk.Treeview(f_phai, columns=("ten", "sl", "tt"), show="headings")
        self.tree_gio.heading("ten", text="Tên SP")
        self.tree_gio.heading("sl", text="SL Mua")
        self.tree_gio.heading("tt", text="Thành tiền")
        self.tree_gio.pack(fill="both", expand=True)

        self.lbl_tong_tien = tk.Label(f_phai, text="Tổng: 0 VNĐ", fg="red", font=("Arial", 14))
        self.lbl_tong_tien.pack(pady=5)

        tk.Button(f_phai, text="THANH TOÁN", bg="orange", command=self.thanh_toan).pack(fill="x")
        tk.Button(f_phai, text="Xóa giỏ hàng", command=self.xoa_gio_hang).pack(fill="x")

        self.load_data_ban_hang()

    def load_data_ban_hang(self):
        if not self.tree_ban_hang:
            return
        for i in self.tree_ban_hang.get_children():
            self.tree_ban_hang.delete(i)

        ds_sp = self.doc_file(FILE_SP)
        for sp in ds_sp:
            self.tree_ban_hang.insert("", "end",
                                      values=(sp.get("id"), sp.get("ten"), sp.get("sl"), f"{sp.get('gia',0):,}"))

        # Đồng bộ giỏ: loại bỏ mặt hàng đã bị xóa khỏi kho (để tránh “mơ” hàng không tồn tại)
        id_con_lai = {sp.get("id") for sp in ds_sp}
        self.gio_hang = [m for m in self.gio_hang if m.get("id") in id_con_lai]
        self.cap_nhat_gio()

    def them_vao_gio(self, event=None):
        if not self.tree_ban_hang:
            return
        chon = self.tree_ban_hang.focus()
        if not chon:
            return

        id_sp, ten, ton_kho_str, gia_str = self.tree_ban_hang.item(chon, "values")
        ton_kho = int(ton_kho_str)
        gia = int(str(gia_str).replace(",", ""))

        top = tk.Toplevel(self.root)
        top.title("Chọn số lượng")
        tk.Label(top, text=f"Mua: {ten}").pack(padx=10, pady=6)

        e_sl = tk.Entry(top)
        e_sl.pack(padx=10, pady=6)
        e_sl.focus()

        def xac_nhan():
            try:
                sl_mua = int(e_sl.get())
                if sl_mua <= 0:
                    messagebox.showerror("Lỗi", "Số lượng phải > 0")
                    return
                if sl_mua > ton_kho:
                    messagebox.showerror("Lỗi", "Không đủ hàng trong kho")
                    return

                for m in self.gio_hang:
                    if m.get("id") == id_sp:
                        m["sl"] += sl_mua
                        m["tt"] = m["sl"] * m["gia"]
                        break
                else:
                    self.gio_hang.append({"id": id_sp, "ten": ten, "sl": sl_mua, "gia": gia, "tt": sl_mua * gia})

                self.cap_nhat_gio()
                top.destroy()
            except Exception:
                messagebox.showerror("Lỗi", "Nhập sai số lượng")

        tk.Button(top, text="OK", command=xac_nhan).pack(padx=10, pady=10)

    def cap_nhat_gio(self):
        if not self.tree_gio:
            return
        for i in self.tree_gio.get_children():
            self.tree_gio.delete(i)

        tong = 0
        for m in self.gio_hang:
            tong += m.get("tt", 0)
            self.tree_gio.insert("", "end", values=(m.get("ten"), m.get("sl"), f"{m.get('tt',0):,}"))

        if self.lbl_tong_tien:
            self.lbl_tong_tien.config(text=f"Tổng: {tong:,} VNĐ")

    def xoa_gio_hang(self):
        self.gio_hang = []
        self.cap_nhat_gio()

    def thanh_toan(self):
        if not self.gio_hang:
            return

        ds_sp = self.doc_file(FILE_SP)
        map_sp = {sp.get("id"): sp for sp in ds_sp}

        # kiểm tra lỗi (đúng yêu cầu: nếu SP đã bị xóa khỏi kho -> báo lỗi)
        loi = []
        for m in self.gio_hang:
            pid = m.get("id")
            if pid not in map_sp:
                loi.append(f"- {m.get('ten')} (đã bị xóa khỏi kho)")
            else:
                if m.get("sl", 0) > map_sp[pid].get("sl", 0):
                    loi.append(f"- {m.get('ten')} (không đủ tồn kho: cần {m.get('sl')} còn {map_sp[pid].get('sl',0)})")

        if loi:
            messagebox.showerror("Lỗi thanh toán", "Không thể thanh toán:\n" + "\n".join(loi))
            self.load_data_ban_hang()
            return

        # Lưu hóa đơn
        ds_hd = self.doc_file(FILE_HD)
        ma_hd = f"HD{len(ds_hd)+1:03d}"
        tong_tien = sum(x.get("tt", 0) for x in self.gio_hang)

        hd_moi = {
            "ma": ma_hd,
            "nguoi": self.nguoi_dang_nhap.get("ten"),
            "nguoi_username": self.nguoi_dang_nhap.get("username"),
            "ngay": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tong": tong_tien,
            "chitiet": self.gio_hang
        }
        ds_hd.append(hd_moi)
        self.ghi_file(FILE_HD, ds_hd)

        # Trừ kho
        for m in self.gio_hang:
            pid = m.get("id")
            map_sp[pid]["sl"] = map_sp[pid].get("sl", 0) - m.get("sl", 0)
        self.ghi_file(FILE_SP, list(map_sp.values()))

        messagebox.showinfo("OK", "Thanh toán thành công!")
        self.xoa_gio_hang()
        self.load_data_ban_hang()
        self.load_lich_su()

    # ==============================
    # TAB LỊCH SỬ HÓA ĐƠN
    # ==============================
    def xay_dung_tab_lich_su(self, parent):
        tk.Button(parent, text="Làm mới", command=self.load_lich_su).pack(pady=4)
        tk.Button(parent, text="Xem chi tiết", bg="yellow", command=self.xem_chi_tiet_hoa_don).pack(pady=4)

        self.tree_lich_su = ttk.Treeview(parent, columns=("ma", "nguoi", "ngay", "tong"), show="headings")
        for c, t, w in [("ma", "Mã HĐ", 90), ("nguoi", "Người lập", 160), ("ngay", "Ngày giờ", 170), ("tong", "Tổng tiền", 130)]:
            self.tree_lich_su.heading(c, text=t)
            self.tree_lich_su.column(c, width=w)
        self.tree_lich_su.pack(fill="both", expand=True)

        self.load_lich_su()

    def load_lich_su(self):
        if not self.tree_lich_su:
            return
        for i in self.tree_lich_su.get_children():
            self.tree_lich_su.delete(i)

        ds = self.doc_file(FILE_HD)
        for hd in ds:
            self.tree_lich_su.insert("", "end", values=(hd.get("ma"), hd.get("nguoi"), hd.get("ngay"), f"{hd.get('tong',0):,}"))

    def xem_chi_tiet_hoa_don(self):
        if not self.tree_lich_su:
            return
        chon = self.tree_lich_su.focus()
        if not chon:
            return
        ma_hd = self.tree_lich_su.item(chon, "values")[0]

        ds = self.doc_file(FILE_HD)
        hd = next((x for x in ds if x.get("ma") == ma_hd), None)
        if not hd:
            return

        top = tk.Toplevel(self.root)
        top.title(f"Chi tiết {ma_hd}")
        tk.Label(top, text=f"Hóa đơn: {ma_hd}  |  {hd.get('ngay','')}").pack(padx=10, pady=6)

        tv = ttk.Treeview(top, columns=("ten", "sl", "gia"), show="headings")
        tv.heading("ten", text="Tên"); tv.heading("sl", text="SL"); tv.heading("gia", text="Giá")
        tv.pack(fill="both", expand=True, padx=10, pady=6)

        for sp in hd.get("chitiet", []):
            tv.insert("", "end", values=(sp.get("ten"), sp.get("sl"), f"{sp.get('gia',0):,}"))

    # ==============================
    # TAB QUẢN LÝ KHO (ADMIN) + UNDO XÓA
    # ==============================
    def xay_dung_tab_kho(self, parent):
        f = tk.Frame(parent)
        f.pack(pady=5)

        tk.Label(f, text="Mã:").grid(row=0, column=0); self.e_k_ma = tk.Entry(f); self.e_k_ma.grid(row=0, column=1)
        tk.Label(f, text="Tên:").grid(row=0, column=2); self.e_k_ten = tk.Entry(f); self.e_k_ten.grid(row=0, column=3)
        tk.Label(f, text="SL:").grid(row=0, column=4); self.e_k_sl = tk.Entry(f); self.e_k_sl.grid(row=0, column=5)
        tk.Label(f, text="Giá:").grid(row=0, column=6); self.e_k_gia = tk.Entry(f); self.e_k_gia.grid(row=0, column=7)

        tk.Button(f, text="Thêm mới", command=self.kho_chuan_bi_them).grid(row=1, column=0, columnspan=2)
        tk.Button(f, text="Sửa", command=self.kho_chuan_bi_sua).grid(row=1, column=2, columnspan=2)
        tk.Button(f, text="Xóa", command=self.kho_xoa).grid(row=1, column=4, columnspan=2)
        tk.Button(f, text="Lưu lại", bg="green", fg="white", command=self.kho_luu).grid(row=1, column=6, columnspan=2)

        # NÚT QUAY LẠI (UNDO) chỉ phục hồi sau thao tác XÓA
        tk.Button(f, text="Quay lại (Undo)", bg="orange", command=self.kho_undo).grid(row=2, column=0, columnspan=4, pady=6)

        self.tree_kho = ttk.Treeview(parent, columns=("id", "ten", "sl", "gia"), show="headings")
        for c, t, w in [("id", "Mã", 90), ("ten", "Tên", 200), ("sl", "SL", 90), ("gia", "Giá", 120)]:
            self.tree_kho.heading(c, text=t); self.tree_kho.column(c, width=w)
        self.tree_kho.pack(fill="both", expand=True)
        self.tree_kho.bind("<<TreeviewSelect>>", self.kho_chon_dong)

        self.load_kho()

    def load_kho(self):
        if not self.tree_kho:
            return
        for i in self.tree_kho.get_children():
            self.tree_kho.delete(i)

        ds = self.doc_file(FILE_SP)
        for sp in ds:
            self.tree_kho.insert("", "end", values=(sp.get("id"), sp.get("ten"), sp.get("sl"), f"{sp.get('gia',0):,}"))

    def kho_chon_dong(self, event=None):
        if not self.tree_kho:
            return
        chon = self.tree_kho.focus()
        if not chon:
            return
        v = self.tree_kho.item(chon, "values")
        self.e_k_ma.config(state="normal")
        self.e_k_ma.delete(0, tk.END); self.e_k_ma.insert(0, v[0])
        self.e_k_ten.delete(0, tk.END); self.e_k_ten.insert(0, v[1])
        self.e_k_sl.delete(0, tk.END); self.e_k_sl.insert(0, v[2])
        self.e_k_gia.delete(0, tk.END); self.e_k_gia.insert(0, str(v[3]).replace(",", ""))

    def kho_chuan_bi_them(self):
        self.che_do_kho = "them"
        self.e_k_ma.config(state="normal")
        for e in (self.e_k_ma, self.e_k_ten, self.e_k_sl, self.e_k_gia):
            e.delete(0, tk.END)
        self.e_k_ma.focus()

    def kho_chuan_bi_sua(self):
        if not self.tree_kho or not self.tree_kho.selection():
            messagebox.showerror("Lỗi", "Chọn dòng để sửa")
            return
        self.che_do_kho = "sua"
        self.e_k_ma.config(state="readonly")

    def kho_xoa(self):
        if not self.tree_kho or not self.tree_kho.selection():
            return

        id_xoa = self.tree_kho.item(self.tree_kho.selection()[0], "values")[0]
        if not messagebox.askyesno("Xóa", "Chắc chắn xóa?"):
            return

        ds = self.doc_file(FILE_SP)

        # BACKUP trước khi xóa (chỉ tác động khi XÓA)
        self.ghi_file(FILE_SP_BAK, ds)

        ds = [x for x in ds if x.get("id") != id_xoa]
        self.ghi_file(FILE_SP, ds)

        self.load_kho()
        self.load_data_ban_hang()

    def kho_undo(self):
        if not os.path.exists(FILE_SP_BAK):
            messagebox.showerror("Lỗi", "Không có backup để phục hồi (chưa có thao tác xóa nào).")
            return

        ds_bak = self.doc_file(FILE_SP_BAK)
        self.ghi_file(FILE_SP, ds_bak)

        messagebox.showinfo("Undo", "Đã phục hồi kho từ bản backup trước khi xóa.")
        self.load_kho()
        self.load_data_ban_hang()

    def kho_luu(self):
        id_sp = (self.e_k_ma.get() or "").strip()
        ten = (self.e_k_ten.get() or "").strip()
        try:
            sl = int(self.e_k_sl.get())
            gia = int(self.e_k_gia.get())
        except Exception:
            messagebox.showerror("Lỗi", "SL và Giá phải là số")
            return

        ds = self.doc_file(FILE_SP)

        if self.che_do_kho == "them":
            if any(x.get("id") == id_sp for x in ds):
                messagebox.showerror("Lỗi", "Trùng mã sản phẩm")
                return
            ds.append({"id": id_sp, "ten": ten, "sl": sl, "gia": gia})

        elif self.che_do_kho == "sua":
            found = False
            for x in ds:
                if x.get("id") == id_sp:
                    x["ten"], x["sl"], x["gia"] = ten, sl, gia
                    found = True
                    break
            if not found:
                messagebox.showerror("Lỗi", "Không tìm thấy mã để sửa")
                return
            self.e_k_ma.config(state="normal")

        else:
            messagebox.showerror("Lỗi", "Chưa chọn chế độ (Thêm/Sửa)")
            return

        self.ghi_file(FILE_SP, ds)
        self.che_do_kho = ""
        self.load_kho()
        self.load_data_ban_hang()

    # ==============================
    # TAB QUẢN LÝ NHÂN SỰ (ADMIN)
    # ==============================
    def xay_dung_tab_nhan_su(self, parent):
        f = tk.Frame(parent)
        f.pack(pady=5)

        tk.Label(f, text="Mã NV").grid(row=0, column=0); self.e_n_ma = tk.Entry(f); self.e_n_ma.grid(row=0, column=1)
        tk.Label(f, text="User").grid(row=0, column=2); self.e_n_user = tk.Entry(f); self.e_n_user.grid(row=0, column=3)
        tk.Label(f, text="Pass").grid(row=0, column=4); self.e_n_pass = tk.Entry(f); self.e_n_pass.grid(row=0, column=5)

        tk.Label(f, text="Tên").grid(row=1, column=0); self.e_n_ten = tk.Entry(f); self.e_n_ten.grid(row=1, column=1)
        tk.Label(f, text="Role").grid(row=1, column=2); self.c_n_role = ttk.Combobox(f, values=["admin", "user"]); self.c_n_role.grid(row=1, column=3)
        tk.Label(f, text="Ngày vào").grid(row=1, column=4); self.e_n_ngay = tk.Entry(f); self.e_n_ngay.grid(row=1, column=5)
        tk.Label(f, text="Lương").grid(row=1, column=6); self.e_n_luong = tk.Entry(f); self.e_n_luong.grid(row=1, column=7)

        tk.Button(f, text="Thêm NV", command=self.ns_chuan_bi_them).grid(row=2, column=0, columnspan=2)
        tk.Button(f, text="Sửa NV", command=self.ns_chuan_bi_sua).grid(row=2, column=2, columnspan=2)
        tk.Button(f, text="Xóa NV", command=self.ns_xoa).grid(row=2, column=4, columnspan=2)
        tk.Button(f, text="Lưu NV", bg="green", fg="white", command=self.ns_luu).grid(row=2, column=6, columnspan=2)

        self.tree_ns = ttk.Treeview(parent, columns=("ma", "user", "ten", "role", "luong"), show="headings")
        for c in ["ma", "user", "ten", "role", "luong"]:
            self.tree_ns.heading(c, text=c)
        self.tree_ns.pack(fill="both", expand=True)
        self.tree_ns.bind("<<TreeviewSelect>>", self.ns_chon_dong)

        self.load_ns()

    def load_ns(self):
        ds = self.doc_file(FILE_USER)

        if not self.tree_ns:
            return
        for i in self.tree_ns.get_children():
            self.tree_ns.delete(i)

        for u in ds:
            ma = u.get("ma_nv")
            if not ma:
                continue
            username = u.get("username", "")
            ten = u.get("ten", "")
            role = u.get("role", "")
            luong = u.get("luong", "")
            self.tree_ns.insert("", "end", values=(ma, username, ten, role, luong))

    def ns_chon_dong(self, event=None):
        if not self.tree_ns:
            return
        chon = self.tree_ns.focus()
        if not chon:
            return

        ma_nv = self.tree_ns.item(chon, "values")[0]
        ds = self.doc_file(FILE_USER)
        u = next((x for x in ds if x.get("ma_nv") == ma_nv), None)
        if not u:
            return

        self.e_n_ma.config(state="normal")
        self.e_n_ma.delete(0, tk.END); self.e_n_ma.insert(0, u.get("ma_nv", ""))
        self.e_n_user.delete(0, tk.END); self.e_n_user.insert(0, u.get("username", ""))
        self.e_n_pass.delete(0, tk.END); self.e_n_pass.insert(0, u.get("password", ""))
        self.e_n_ten.delete(0, tk.END); self.e_n_ten.insert(0, u.get("ten", ""))
        self.c_n_role.set(u.get("role", ""))
        self.e_n_ngay.delete(0, tk.END); self.e_n_ngay.insert(0, u.get("ngay_vao_lam", ""))
        self.e_n_luong.delete(0, tk.END); self.e_n_luong.insert(0, str(u.get("luong", "")))

    def ns_chuan_bi_them(self):
        self.che_do_ns = "them"
        for e in (self.e_n_ma, self.e_n_user, self.e_n_pass, self.e_n_ten, self.e_n_ngay, self.e_n_luong):
            e.delete(0, tk.END)
        self.c_n_role.set("")
        self.e_n_ma.config(state="normal")
        self.e_n_ma.focus()

    def ns_chuan_bi_sua(self):
        if not self.tree_ns or not self.tree_ns.selection():
            messagebox.showerror("Lỗi", "Chọn nhân sự để sửa")
            return
        self.che_do_ns = "sua"
        self.e_n_ma.config(state="readonly")

    def ns_xoa(self):
        if not self.tree_ns or not self.tree_ns.selection():
            return
        ma = self.tree_ns.item(self.tree_ns.selection()[0], "values")[0]
        if not messagebox.askyesno("Xóa", "Chắc chắn xóa nhân sự này?"):
            return
        ds = [x for x in self.doc_file(FILE_USER) if x.get("ma_nv") != ma]
        self.ghi_file(FILE_USER, ds)
        self.load_ns()

    def ns_luu(self):
        ma = (self.e_n_ma.get() or "").strip()
        username = (self.e_n_user.get() or "").strip()
        pw = (self.e_n_pass.get() or "").strip()
        ten = (self.e_n_ten.get() or "").strip()
        role = (self.c_n_role.get() or "").strip()
        ngay = (self.e_n_ngay.get() or "").strip()
        try:
            luong = int(self.e_n_luong.get())
        except Exception:
            messagebox.showerror("Lỗi", "Lương phải là số")
            return

        if luong < 1500000:
            messagebox.showerror("Lỗi", "Lương phải >= 1.500.000")
            return

        try:
            datetime.strptime(ngay, "%Y-%m-%d")
        except Exception:
            messagebox.showerror("Lỗi", "Ngày vào làm phải dạng YYYY-MM-DD")
            return

        ds = self.doc_file(FILE_USER)
        nguoi = {
            "ma_nv": ma,
            "username": username,
            "password": pw,
            "role": role,
            "ten": ten,
            "ngay_vao_lam": ngay,
            "luong": luong
        }

        if self.che_do_ns == "them":
            if any(x.get("ma_nv") == ma for x in ds):
                messagebox.showerror("Lỗi", "Trùng mã nhân viên")
                return
            ds.append(nguoi)

        elif self.che_do_ns == "sua":
            found = False
            for i, x in enumerate(ds):
                if x.get("ma_nv") == ma:
                    ds[i] = nguoi
                    found = True
                    break
            if not found:
                messagebox.showerror("Lỗi", "Không tìm thấy mã nhân viên để sửa")
                return
            self.e_n_ma.config(state="normal")

        else:
            messagebox.showerror("Lỗi", "Chưa chọn chế độ (Thêm/Sửa)")
            return

        self.ghi_file(FILE_USER, ds)
        self.che_do_ns = ""
        self.load_ns()
        messagebox.showinfo("OK", "Lưu nhân sự thành công")

    # ==============================
    # NẠP DỮ LIỆU TỪ API (ADMIN)
    # ==============================
    def nap_du_lieu_api(self):
        try:
            url = "https://api.npoint.io/881fe47e8b6245bbe49a"
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data_api = resp.json()

            if isinstance(data_api, list):
                products = data_api
            else:
                products = data_api.get("products", data_api.get("items", []))

            ds_moi = []
            for i, sp in enumerate(products):
                id_ = sp.get("id") or sp.get("ID") or sp.get("ma") or f"API_{i}"
                ten = sp.get("ten") or sp.get("name") or sp.get("title") or sp.get("product_name") or "No Name"
                sl = int(sp.get("sl") or sp.get("stock") or sp.get("quantity") or 0)
                gia = int(sp.get("gia") or sp.get("price") or 0)
                ds_moi.append({"id": str(id_), "ma": str(id_), "ten": ten, "sl": sl, "gia": gia})

            self.ghi_file(FILE_SP, ds_moi)
            messagebox.showinfo("API", f"Đã nhập {len(ds_moi)} sản phẩm từ API")
            self.load_kho()
            self.load_data_ban_hang()

        except Exception as e:
            messagebox.showerror("Lỗi API", str(e))

    # ==============================
    def chay(self):
        self.root.mainloop()


if __name__ == "__main__":
    UngDung().chay()
