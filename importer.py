import requests
import json


API_URL = "https://dummyjson.com/products"

def fetch_and_save_products():
    print("Đang tải dữ liệu từ Internet...")
    response = requests.get(API_URL)
    
    if response.status_code == 200:
        data = response.json()
        products_list = data['products']
        
        my_products = []
        for p in products_list:
            new_p = {
                "id": f"SP{p['id']:03d}",
                "ten_hang": p['title'],
                "so_luong_ton": p['stock'],
                "don_gia": int(p['price'] * 25000), 
                "nha_cung_cap": p['brand'] if 'brand' in p else "No Brand"
            }
            my_products.append(new_p)
            
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(my_products, f, ensure_ascii=False, indent=4)
        
        print(f"Đã lưu thành công {len(my_products)} sản phẩm vào products.json!")
    else:
        print("Lỗi khi tải dữ liệu!")

if __name__ == "__main__":
    fetch_and_save_products()