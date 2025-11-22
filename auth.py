
import json


class Cay:
    def __init__(self,ma_cay="",ten_cay="",tuyen_duong="",chieu_cao=0.0,duong_kinh_than=0.0,tinh_trang=""):
        self.ma_cay=ma_cay
        self.ten_cay=ten_cay
        self.tuyen_duong=tuyen_duong
        self.chieu_cao=chieu_cao
        self.duong_kinh_than=duong_kinh_than
        self.tinh_trang=tinh_trang
    def to_dict(self):
        return {"Ma_cay":self.ma_cay,"Ten_cay":self.ten_cay,"Tuyen_duong":self.tuyen_duong,"Chieu_cao":self.chieu_cao,"Duong_kinh_than":self.duong_kinh_than,"Tinh_trang":self.tinh_trang}
    def __str__(self):
        return f"{self.ma_cay:<10}{self.ten_cay:<10}{self.tuyen_duong:<25}{self.chieu_cao:<10}{self.duong_kinh_than:<10}{self.tinh_trang:<20}"
class Danh_Sach_Cay:
    def __init__(self):
        self.Danh_sach=[]
    def read_file_json(self,ten_file):
        try:
            with open(ten_file,'r',encoding='utf-8') as f:
                du_lieu=json.load(f)
                self.Danh_sach=[Cay(cay["ma_cay"],cay["ten_cay"],cay["tuyen_duong"],cay["chieu_cao"],cay["duong_kinh_than"],cay["tinh_trang"])for cay in du_lieu]
                print("Đọc file thành công")
        except FileNotFoundError:
            print("Không tìm thấy file")
        except ValueError as loi:
            print("Lỗi: ",loi)
    def write_file_json(self,ten_file):
        try:
            with open(ten_file,'w',encoding='utf-8')as f:
                json.dump([cay.to_dict() for cay in self.Danh_sach],f,ensure_ascii=False,indent=4)
                print("Đã ghi thành công")
        except ValueError as loi:
            print("Lỗi: ",loi)
    def infor(self):
        if not self.Danh_sach:
            print("Danh Sách Rỗng")
        else:
            print(f"{'Mã Cây:':<10}{'Tên Cây:':<10}{'Tuyến Đường:':<25}{'Chiều Cao:':<10}{'Đường kính thân:':<10}{'Tình Trạng:':<10}")
            for cay in self.Danh_sach:
                print(cay)
    def add(self):
        ma=input("Nhập mã cây: ")
        for cay in self.Danh_sach:
            if cay.ma_cay.lower()==ma.lower():
                print("Mã này đã trùng với 1 cây trong danh sách")
                return
        ten_cay=input("Nhập Tên Cây: ")
        tuyen_duong=input("Nhập tuyến đường: ")
        try:
            chieu_cao=float(input("Nhập chiều cao: "))
            if chieu_cao<0:
                raise ValueError
        except ValueError:
            print("Chiều cao phải là số dương >0")
            return
        try:
            duong_kinh_than=float(input("Nhập đường kính thân: "))
            if duong_kinh_than<0:
                raise ValueError
        except ValueError:
            print("Đường kính phải là số dương >0")
            return
        tinh_trang=input("Nhập tình trạng: ")
        self.Danh_sach.append(Cay(ma,ten_cay,tuyen_duong,chieu_cao,duong_kinh_than,tinh_trang))
        print("Đã thêm thành công")
    def update_infor(self):
        flag=False
        ma=input("Nhập mã cây để kiểm tra: ")
        for cay in self.Danh_sach:
            if cay.ma_cay.lower()==ma.lower():
                cay.ten_cay=input("Nhập lại Tên Cây: ")
                cay.tuyen_duong=input("Nhập lại tuyến đường: ")
                cay.chieu_cao=float(input("Nhập lại chiều cao: "))
                cay.duong_kinh_than=float(input("Nhập lịa đường kính thân: "))
                cay.tinh_trang=input("Nhập lại tình trang: ")
                print("Đã cập nhật thành công")
                flag=True
        if flag==False:
            print("Không tìm thấy mã: ",ma)

    def delete(self):
        flag=False
        ma=input("Nhập mã cây để xóa: ")
        for cay in self.Danh_sach:
            if cay.ma_cay.lower()==ma.lower():
                self.Danh_sach.remove(cay)
                flag=True
                print("Đã xóa thành công")
        if flag==False:
            print("Không tìm thấy mã: ",ma)
    def look_for(self):
        flag=False
        ma=input("Nhập mã cây hoặc tên cây để tìm: ")
        for cay in self.Danh_sach:
            if cay.ma_cay.lower()==ma.lower() or cay.ten_cay.lower()==ma.lower():
                print(cay)
                flag=True
        if flag==False:
            print("Không tìm thấy: ",ma)
    def sum_chieu_cao(self):
        tong=sum(cay.chieu_cao for cay in self.Danh_sach)
        return tong
    def min_max(self):
        minn=min(self.Danh_sach,key=lambda x:x.chieu_cao)
        maxx=max(self.Danh_sach,key=lambda x:x.chieu_cao)
        print("Cây có chiều cao thấp nhất là: ")
        print(f"{'Mã Cây:':<10}{'Tên Cây:':<10}{'Tuyến Đường:':<25}{'Chiều Cao:':<10}{'Đường kính thân:':<10}{'Tình Trạng:':<10}")
        print(minn)
        print("Cây có chiều cao cao nhất là: ")
        print(f"{'Mã Cây:':<10}{'Tên Cây:':<10}{'Tuyến Đường:':<25}{'Chiều Cao:':<10}{'Đường kính thân:':<10}{'Tình Trạng:':<10}")
        print(maxx)
    def thong_ke_tuyen_duong(self):
        thong_ke={}
        for cay in self.Danh_sach:
            if cay.tuyen_duong in thong_ke:
                thong_ke[cay.tuyen_duong]+=1
            else:
                thong_ke[cay.tuyen_duong]=1
        print ("Kết quả thống kê: ")
        for key,value in thong_ke.items():
            print(f"{key}:{value}")
    def sort_descending(self):
        self.Danh_sach.sort(key=lambda x:x.chieu_cao,reverse=True)
        print("Đã sắp xếp thành công")
    # def write(self):
    #     self.write_file_json("cayxanh.json")
    #     print("Đã ghi thành công")
    def top3_max_chieu_cao(self):
        ds=Danh_Sach_Cay()
        self.Danh_sach.sort(key=lambda x:x.chieu_cao,reverse=True)
        for cay in range(min(3,len(self.Danh_sach))):
            ds.Danh_sach.append(self.Danh_sach[cay])
        return ds
    def Average(self):
        tong=sum(cay.chieu_cao for cay in self.Danh_sach)
        return tong//len(self.Danh_sach)
    def write_cham_soc(self):
        ds=Danh_Sach_Cay()
        for cay in self.Danh_sach:
            if cay.tinh_trang.lower()!="bình thường":
                ds.Danh_sach.append(cay)
        return ds
    def nhap_thong_ke(self):
        thong_ke={}
        tuyen_duong=input("Nhập tên tuyến đường cần thống kê: ")
        for cay in self.Danh_sach:
            if cay.tuyen_duong.lower()==tuyen_duong.strip().lower():
                print(f"Thông tin cây trông trên tuyến {tuyen_duong} là: ")
                if tuyen_duong in thong_ke:
                    thong_ke[tuyen_duong]+=1
                else:
                    thong_ke[tuyen_duong]=1
                print(cay)
        print("Số lượng thống kê: ")
        for key,value in thong_ke.items():
            print(f"{key}:{value}")
    def thong_ke_cao20m(self):
        thong_ke={}
        for cay in self.Danh_sach:
            if cay.chieu_cao>20:
                if cay.ten_cay in thong_ke:
                    thong_ke[cay.ten_cay]+=1
                else:
                    thong_ke[cay.ten_cay]=1
        print("Kết quả thống kê: ")
        for key,value in thong_ke.items():
            print(f"{key}:{value}")
    def ty_le(self):
        dem=0
        for cay in self.Danh_sach:
            if cay.tinh_trang.lower()!="bình thường":
                dem+=1
        return (dem/len(self.Danh_sach))*100
    def max_duong_kinh_than(self):
        return max(self.Danh_sach,key=lambda x:x.duong_kinh_than)
    def liet_ke_tuyen_duong(self):
        self.Danh_sach.sort(key=lambda x: x.tuyen_duong)
        print("Đã sắp xếp thành công")
        self.infor()
    def dem(self):
        thong_ke={"Bình thường":0,"Bất thường":0}
        for cay in self.Danh_sach:
            if cay.tinh_trang.lower()=="bình thường":
                thong_ke["Bình thường"]+=1
            else:
                thong_ke["Bất thường"]+=1
        print("Kết quả thống kê: ")
        for key,value in thong_ke.items():
            print(f"{key}:{value}")
    def xuat_ds_theo_khoang(self):
        flag=False
        x=float(input("Nhập khoảng bắt đầu: "))
        y=float(input("Nhập khoảng kết thúc: "))
        for cay in self.Danh_sach:
            if cay.chieu_cao>=x and cay.chieu_cao<=y:
                print(f"Những Cây có chiều cao khoảng từ {x} tới {y} là: ")
                print(cay)
                flag=True
        if flag==False:
            print(f"Không có cây nào có chiều cao ở khoảng {x} tới {y}: ")
    def sum_duong_kinh_than(self):
        return sum(cay.duong_kinh_than for cay in self.Danh_sach)
    def look_for_cay(self):
        flag=False
        ma=input("Nhập tên cây để tìm: ")
        for cay in self.Danh_sach:
            if  cay.ten_cay.lower()==ma.lower():
                print(cay)
                flag=True
        if flag==False:
            print("Không tìm thấy cây: ",ma)
    def cham_soc_dat_biet(self):
        tu_khoa=['sâu bệnh','gãy','nghiêng','lụi','hư gốc']
        ds=[cay for cay in self.Danh_sach if any( tu in cay.tinh_trang.lower() for tu in tu_khoa)]
        if not ds:
            print("Không có cây nào cả")
        else:
            for cay in ds:
                print (cay)
    def ky_tu_bat_ky(self):
        x=input("Nhập từ cần tìm: ").lower()
        ds=[cay for cay in self.Danh_sach if x in cay.ten_cay.lower()]
        if not ds:
            print("Không có cây nào cả")
        else:
            for cay in ds:
                print (cay)
if __name__=="__main__":
    danh_sach=Danh_Sach_Cay()
    while True:
        print("=" * 70)
        print("CHƯƠNG TRÌNH QUẢN LÝ CÂY XANH".center(70))
        print("=" * 70)
        print("1.  Đọc dữ liệu từ file JSON - Nạp danh sách cây xanh từ cayxanh.json.")
        print("2.  Hiển thị danh sách cây xanh - In bảng gồm: mã, tên, tuyến đường, chiều cao, đường kính, tình trạng.")
        print("3.  Thêm cây mới - Nhập thông tin và thêm cây vào danh sách.")
        print("4.  Cập nhật thông tin cây xanh - Sửa tên, tuyến đường, chiều cao, đường kính, tình trạng theo mã.")
        print("5.  Xóa cây xanh - Xóa cây khỏi danh sách theo mã.")
        print("6.  Tìm kiếm cây theo mã hoặc tên - Hiển thị thông tin cây phù hợp.")
        print("7.  Tính tổng chiều cao toàn bộ cây xanh - Tính tổng chieu_cao trong danh sách.")
        print("8.  Tìm cây cao nhất / thấp nhất - Xuất thông tin cây cao nhất và thấp nhất.")
        print("9.  Thống kê số lượng cây theo tuyến đường - Đếm số cây trên mỗi tuyến đường.")
        print("10. Sắp xếp danh sách theo chiều cao giảm dần - Hiển thị danh sách cây từ cao → thấp.")
        print("11. Ghi dữ liệu ra file JSON - Lưu danh sách hiện tại xuống cayxanh.json.")
        print("12. Xuất file top 3 cây cao nhất - Lọc 3 cây cao nhất, ghi ra top3_cayxanh.json.")
        print("13. Tính chiều cao trung bình của cây xanh - Trung bình = tổng chiều cao / số cây.")
        print("14. Liệt kê cây cần chăm sóc đặc biệt - Lọc cây có tinh_trang chứa: 'sâu bệnh', 'gãy', 'nghiêng', 'lụi', 'hư gốc'.")
        print("15. Ghi danh sách cây cần chăm sóc ra file JSON - Xuất ra cay_can_cham_soc.json.")
        print("16. Thống kê cây theo tuyến đường nhập từ bàn phím - Người dùng nhập tên tuyến, chương trình đếm và hiển thị cây trồng trên tuyến đó.")
        print("17. Thống kê số lượng cây cao hơn 20 m - Đếm và liệt kê tất cả cây có chieu_cao > 20.")
        print("18. Tính tỷ lệ cây cần chăm sóc đặc biệt (%) - = (Số cây có tình trạng ≠ 'Bình thường') / tổng số cây × 100.")
        print("19. Tìm cây có đường kính thân lớn nhất - Hiển thị thông tin cây có duong_kinh_than lớn nhất.")
        print("20. Liệt kê cây theo tên tuyến đường (A → Z) - Sắp xếp theo tuyen_duong tăng dần rồi in danh sách.")
        print("21. Đếm số cây 'Bình thường' và 'Bất thường' - Thống kê 2 nhóm tình trạng chính.")
        print("22. Xuất danh sách cây có chiều cao nằm trong khoảng nhập vào - Ví dụ: từ 5 m → 10 m.")
        print("23. Tính tổng đường kính thân của toàn bộ cây - Tổng tất cả giá trị duong_kinh_than.")
        print("24. Xuất danh sách cây có cùng loại (tên cây) - Nhập 'Bằng lăng' → liệt kê tất cả cây Bằng lăng.")
        print("25. Tìm cây có tên chứa chuỗi ký tự bất kỳ - Ví dụ nhập 'phượng' → hiển thị 'Phượng vĩ'.")
        print("=" * 70)
        choice=input("Nhập lựa chọn của bạn: ")
        if choice=="1":
            danh_sach.read_file_json("cay.json")
        elif choice=="2":
            danh_sach.infor()
        elif choice=="3":
            danh_sach.add()
        elif choice=="4":
            danh_sach.update_infor()
        elif choice=="5":
            danh_sach.delete()
        elif choice=="6":
            danh_sach.look_for()
        elif choice=="7":
            print(f"Tổng chiều cao của toàn bộ cây xanh: {danh_sach.sum_chieu_cao()}")
        elif choice=="8":
            danh_sach.min_max()
        elif choice=="9":
            danh_sach.thong_ke_tuyen_duong()
        elif choice=="10":
            danh_sach.sort_descending()
        elif choice=="11":
            danh_sach.write_file_json("cayxanh.json")
        elif choice=="12":
            top3=danh_sach.top3_max_chieu_cao()
            top3.write_file_json("top3_cayxanh.json")
            top3.infor()
        elif choice=="13":
            print(f"Trung bình chiều cao của toàn bộ cây xanh: {danh_sach.Average()}")
        elif choice=="14":
            danh_sach.cham_soc_dat_biet()
        elif choice=="15":
            cham_soc=danh_sach.write_cham_soc()
            cham_soc.write_file_json("cay_can_cham_soc.json")
        elif choice=="16":
            danh_sach.nhap_thong_ke()
        elif choice=="17":
            danh_sach.thong_ke_cao20m()
        elif choice=="18":
            print(f"Tỷ lệ cây cần chăm sóc đặc biệt là: {danh_sach.ty_le()}%")
        elif choice=="19":
            print("Cây có đường kính lớn nhất là: ")
            print(danh_sach.max_duong_kinh_than())
        elif choice=="20":
            danh_sach.liet_ke_tuyen_duong()
        elif choice=="21":
            danh_sach.dem()
        elif choice=="22":
            danh_sach.xuat_ds_theo_khoang()
        elif choice=="23":
            print(f"Tổng đường kính thân của toàn bộ cây là: {danh_sach.sum_duong_kinh_than()}")
        elif choice=="24":
            danh_sach.look_for_cay()
        elif choice=="25":
            danh_sach.ky_tu_bat_ky()
        elif choice=="0":
            break

