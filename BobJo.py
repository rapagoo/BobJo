import requests
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, messagebox

# zscode와 시/군 명 매핑
zscode_city_map = {
    "41110": "수원시", "41130": "성남시", "41150": "의정부시", "41170": "안양시", "41190": "부천시",
    "41210": "광명시", "41220": "평택시", "41250": "동두천시", "41270": "안산시", "41280": "고양시",
    "41290": "과천시", "41310": "구리시", "41360": "남양주시", "41370": "오산시", "41390": "시흥시",
    "41410": "군포시", "41430": "의왕시", "41450": "하남시", "41460": "용인시", "41480": "파주시",
    "41500": "이천시", "41550": "안성시", "41570": "김포시", "41590": "화성시", "41610": "광주시",
    "41630": "양주시", "41650": "포천시", "41670": "여주시", "41800": "연천군", "41820": "가평군",
    "41830": "양평군"
}

# 시/군 목록
cities = list(zscode_city_map.values())
cities.sort()

# 충전기 타입 매핑
charger_type_map = {
    "01": "DC차데모",
    "02": "AC완속",
    "03": "DC차데모+AC3상",
    "04": "DC콤보",
    "05": "DC차데모+DC콤보",
    "06": "DC차데모+AC3상+DC콤보",
    "07": "AC3상",
    "08": "DC콤보(완속)"
}

# 전역 변수 설정
global unique_data
unique_data = []

# API 호출 및 XML 파싱 함수
def fetch_data(zscode):
    url = 'http://apis.data.go.kr/B552584/EvCharger/getChargerInfo'
    params = {
        'serviceKey': 'soQgOYvc8y5bv5jP8tIfni3Lrv4ZcDAk63zxA6k88sGR2vzdP0PhJy7/FRk/RiDA2OmsrOGcypnfZAglrz2wPQ==',
        'pageNo': '1',
        'numOfRows': '9999',  # 충분히 큰 값을 설정
        'zscode': zscode
    }

    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)

    # 필요한 정보 추출
    data = []
    for item in root.findall('.//item'):
        statNm = item.find('statNm').text if item.find('statNm') is not None else ''
        statId = item.find('statId').text if item.find('statId') is not None else ''
        chgerId = item.find('chgerId').text if item.find('chgerId') is not None else ''
        chgerType = item.find('chgerType').text if item.find('chgerType') is not None else ''
        addr = item.find('addr').text if item.find('addr') is not None else ''
        lat = item.find('lat').text if item.find('lat') is not None else ''
        lng = item.find('lng').text if item.find('lng') is not None else ''

        location = f"위도: {lat}, 경도: {lng}"

        data.append([statNm, statId, chgerId, chgerType, addr, location])

    # 충전소 이름과 ID를 기준으로 중복 제거
    unique_data_dict = {}
    for row in data:
        key = (row[0], row[1])  # 충전소명과 충전소 ID를 키로 사용
        if key not in unique_data_dict:
            unique_data_dict[key] = row

    global unique_data
    unique_data = list(unique_data_dict.values())

# GUI 초기 설정
root = tk.Tk()
root.title("EV Charger Info")

# 프레임 설정
search_frame = tk.Frame(root)
search_frame.pack(fill=tk.X, padx=10, pady=5)

result_frame = tk.Frame(root)
result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

detail_frame = tk.Frame(root)
detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# 시 콤보박스
si_label = tk.Label(search_frame, text="시:")
si_label.pack(side=tk.LEFT, padx=5)
si_combo = ttk.Combobox(search_frame, values=cities)
si_combo.pack(side=tk.LEFT, padx=5)

# 검색 결과 개수 라벨
count_label = tk.Label(search_frame, text="")
count_label.pack(side=tk.LEFT, padx=5)

# 검색 버튼
def search():
    selected_si = si_combo.get()
    if not selected_si:
        messagebox.showwarning("경고", "시를 선택하세요.")
        return

    zscode = next((code for code, city in zscode_city_map.items() if city == selected_si), None)
    if not zscode:
        messagebox.showerror("에러", "해당 시/군에 대한 zscode를 찾을 수 없습니다.")
        return

    fetch_data(zscode)

    filtered_data = [row for row in unique_data if selected_si in row[4]]
    filtered_data.sort(key=lambda x: x[0])  # 충전소명을 기준으로 정렬

    for row in tree.get_children():
        tree.delete(row)

    for row in filtered_data:
        tree.insert('', tk.END, values=(row[0],))

    count_label.config(text=f"{len(filtered_data)}개의 충전소가 검색되었습니다.")


search_button = tk.Button(search_frame, text="검색", command=search)
search_button.pack(side=tk.LEFT, padx=5)

# 테이블 생성 (충전소명만 표시)
tree_frame = tk.Frame(result_frame)
tree_frame.pack(fill=tk.BOTH, expand=True)

tree_scroll = tk.Scrollbar(tree_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(tree_frame, columns=('충전소명',), show='headings', yscrollcommand=tree_scroll.set)

tree.heading('충전소명', text='충전소명')

tree.column('충전소명', width=400)

tree_scroll.config(command=tree.yview)

tree.pack(fill=tk.BOTH, expand=True)

# 상세 정보 표시 라벨
detail_label = tk.Label(detail_frame, text="상세 정보", font=('Arial', 14))
detail_label.pack(anchor='w')

detail_text = tk.Text(detail_frame, height=10)
detail_text.pack(fill=tk.BOTH, expand=True)

# 즐겨찾기 목록
favorites = []

# 즐겨찾기에 추가하는 함수
def add_to_favorites(tree, favorites):
    selected_item = tree.focus()
    if selected_item:
        values = tree.item(selected_item, 'values')
        full_info = next((row for row in unique_data if row[0] == values[0]), None)
        if full_info and full_info not in favorites:
            favorites.append(full_info)
            messagebox.showinfo("정보", "즐겨찾기에 추가되었습니다.")
        else:
            messagebox.showwarning("경고", "이미 즐겨찾기에 추가된 항목입니다.")
    else:
        messagebox.showwarning("경고", "추가할 항목을 선택하세요.")

# 즐겨찾기 목록 보기 함수
def show_favorites(root, favorites):
    fav_window = tk.Toplevel(root)
    fav_window.title("즐겨찾기 목록")

    fav_tree = ttk.Treeview(fav_window, columns=('충전소명', '충전소 ID', '충전기 ID', '충전기 타입', '주소', '위치'), show='headings')

    fav_tree.heading('충전소명', text='충전소명')
    fav_tree.heading('충전소 ID', text='충전소 ID')
    fav_tree.heading('충전기 ID', text='충전기 ID')
    fav_tree.heading('충전기 타입', text='충전기 타입')
    fav_tree.heading('주소', text='주소')
    fav_tree.heading('위치', text='위치')

    fav_tree.column('충전소명', width=200)
    fav_tree.column('충전소 ID', width=100)
    fav_tree.column('충전기 ID', width=100)
    fav_tree.column('충전기 타입', width=100)
    fav_tree.column('주소', width=200)
    fav_tree.column('위치', width=300)

    for fav in favorites:
        fav_tree.insert('', tk.END, values=fav)

    fav_tree.pack(fill=tk.BOTH, expand=True)

# 상세 정보 표시 함수
def show_details(event):
    selected_item = tree.focus()
    if selected_item:
        values = tree.item(selected_item, 'values')
        full_info = next((row for row in unique_data if row[0] == values[0]), None)
        if full_info:
            detail_text.delete(1.0, tk.END)
            detail_text.insert(tk.END, f"충전소명: {full_info[0]}\n")
            detail_text.insert(tk.END, f"충전기 타입: {charger_type_map.get(full_info[3], '알 수 없음')}\n")
            detail_text.insert(tk.END, f"주소: {full_info[4]}\n")

tree.bind("<Double-1>", show_details)

# 버튼 추가
button_frame = tk.Frame(root)
button_frame.pack(fill=tk.X, expand=True)

add_fav_button = tk.Button(button_frame, text="즐겨찾기에 추가", command=lambda: add_to_favorites(tree, favorites))
add_fav_button.pack(side=tk.LEFT, padx=10, pady=10)

show_fav_button = tk.Button(button_frame, text="즐겨찾기 목록 보기", command=lambda: show_favorites(root, favorites))
show_fav_button.pack(side=tk.LEFT, padx=10, pady=10)

# GUI 실행
root.mainloop()
