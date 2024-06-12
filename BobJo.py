import spam
import requests
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageSequence
import io
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from collections import defaultdict
import smtplib
from email.mime.text import MIMEText

# 네이버 클라우드 플랫폼의 클라이언트 ID와 시크릿
client_id = 'YOUR_CLIENT_ID'  # 실제 클라이언트 ID로 대체하세요
client_secret = 'YOUR_CLIENT_SECRET'  # 실제 클라이언트 시크릿으로 대체하세요

# 한글 폰트 설정
font_path = 'C:/Windows/Fonts/malgun.ttf'  # Malgun Gothic 폰트 경로
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rc('font', family=font_name)

# 시/군 코드 매핑
zscode_map = {
    "수원시": "41110",
    "성남시": "41130",
    "의정부시": "41150",
    "안양시": "41170",
    "부천시": "41190",
    "광명시": "41210",
    "평택시": "41220",
    "동두천시": "41250",
    "안산시": "41270",
    "고양시": "41280",
    "과천시": "41290",
    "구리시": "41310",
    "남양주시": "41360",
    "오산시": "41370",
    "시흥시": "41390",
    "군포시": "41410",
    "의왕시": "41430",
    "하남시": "41450",
    "용인시": "41460",
    "파주시": "41480",
    "이천시": "41500",
    "안성시": "41550",
    "김포시": "41570",
    "화성시": "41590",
    "광주시": "41610",
    "양주시": "41630",
    "포천시": "41650",
    "여주시": "41670",
    "연천군": "41800",
    "가평군": "41820",
    "양평군": "41830"
}

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

# 충전기 상태 매핑
charger_status_map = {
    "1": "통신이상",
    "2": "충전대기",
    "3": "충전중",
    "4": "운영중지",
    "5": "점검중",
    "9": "상태미확인"
}

# 전역 변수 설정
charger_data = []
favorites = []
selected_lat = None
selected_lng = None
selected_station_name = None
selected_station_charger_count = 0

# GIF 애니메이션 변수 설정
gif_frames = []
gif_index = 0
gif_label = None

# API URL 설정
url = 'http://apis.data.go.kr/B552584/EvCharger/getChargerInfo'


# API 호출 및 XML 파싱 함수
def fetch_data(zscode):
    params = {
        'serviceKey': 'soQgOYvc8y5bv5jP8tIfni3Lrv4ZcDAk63zxA6k88sGR2vzdP0PhJy7/FRk/RiDA2OmsrOGcypnfZAglrz2wPQ==',
        'pageNo': '1',
        'numOfRows': '30000',
        'zscode': zscode
    }

    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)

    data = []
    for item in root.findall('.//item'):
        statNm = item.find('statNm').text if item.find('statNm') is not None else ''
        statId = item.find('statId').text if item.find('statId') is not None else ''
        chgerId = item.find('chgerId').text if item.find('chgerId') is not None else ''
        chgerType = item.find('chgerType').text if item.find('chgerType') is not None else ''
        addr = item.find('addr').text if item.find('addr') is not None else ''
        location = item.find('location').text if item.find('location') is not None else ''
        stat = item.find('stat').text if item.find('stat') is not None else ''
        useTime = item.find('useTime').text if item.find('useTime') is not None else ''
        busiNm = item.find('busiNm').text if item.find('busiNm') is not None else ''
        parkingFree = item.find('parkingFree').text if item.find('parkingFree') is not None else ''
        limitYn = item.find('limitYn').text if item.find('limitYn') is not None else ''
        limitDetail = item.find('limitDetail').text if item.find('limitDetail') is not None else ''
        lat = item.find('lat').text if item.find('lat') is not None else ''
        lng = item.find('lng').text if item.find('lng') is not None else ''

        parkingFree = "무료" if parkingFree == "Y" else "유료"
        limitYn = "이용자 제한 있음" if limitYn == "Y" else "이용자 제한 없음"

        data.append([statNm, statId, chgerId, chgerType, addr, location, stat, useTime, busiNm, parkingFree, limitYn,
                     limitDetail, lat, lng])

    return data


def fetch_map(lat, lng):
    endpoint = "https://naveropenapi.apigw.ntruss.com/map-static/v2/raster"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }
    _center = f"{lng},{lat}"
    _level = 13
    _w, _h = 500, 400
    _maptype = "basic"
    _format = "png"
    _scale = 1
    _markers = f"type:d|size:mid|pos:{lng} {lat}|color:red"
    _lang = "ko"
    _public_transit = True
    _dataversion = ""

    url = f"{endpoint}?center={_center}&level={_level}&w={_w}&h={_h}&maptype={_maptype}&format={_format}&scale={_scale}&markers={_markers}&lang={_lang}&public_transit={_public_transit}&dataversion={_dataversion}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.content
    else:
        print(f"Error fetching map: {response.status_code}, {response.text}")
        return None


# 지도 버튼 함수
def show_map_popup():
    global selected_lat, selected_lng
    if selected_lat is None or selected_lng is None:
        messagebox.showwarning("경고", "충전소를 선택 후 더블클릭하여 지도를 표시하세요.")
        return

    map_image = fetch_map(selected_lat, selected_lng)
    if map_image:
        map_popup = tk.Toplevel(root)
        map_popup.title("지도 보기")
        img = Image.open(io.BytesIO(map_image))
        img = ImageTk.PhotoImage(img)
        map_label = tk.Label(map_popup, image=img)
        map_label.image = img
        map_label.pack()
    else:
        messagebox.showerror("에러", "지도를 가져오는 데 실패했습니다.")


# 검색 버튼 함수
def search():
    global charger_data
    selected_si = si_combo.get()

    if not selected_si:
        messagebox.showwarning("경고", "시를 선택하세요.")
        return

    zscode = zscode_map[selected_si]
    charger_data = fetch_data(zscode)
    unique_stations = {}
    for row in charger_data:
        if row[0] not in unique_stations:
            unique_stations[row[0]] = row

    filtered_data = list(unique_stations.values())
    filtered_data.sort(key=lambda x: x[0])  # 충전소명을 기준으로 정렬

    for row in tree.get_children():
        tree.delete(row)

    for row in filtered_data:
        tree.insert('', tk.END, values=(row[0],))

    # Using the C extension to count stations
    count = spam.count_stations(filtered_data)
    count_label.config(text=f"검색결과: {count}개")


# 충전소 개수를 그래프로 표시하는 함수
def show_graph():
    global selected_station_name, selected_station_charger_count

    if not selected_station_name or selected_station_charger_count == 0:
        messagebox.showwarning("경고", "충전소를 선택 후 더블클릭하여 충전기 개수를 확인하세요.")
        return

    selected_si = si_combo.get()
    if not selected_si:
        messagebox.showwarning("경고", "시를 선택하세요.")
        return

    zscode = zscode_map[selected_si]
    data = fetch_data(zscode)

    station_counts = defaultdict(int)
    for item in data:
        station_counts[item[0]] += 1

    avg_chargers_per_station = sum(station_counts.values()) / len(station_counts)

    plt.figure(figsize=(8, 6))
    plt.bar(['평균 충전기 수', selected_station_name], [avg_chargers_per_station, selected_station_charger_count],
            color=['skyblue', 'orange'])
    plt.xlabel('구분')
    plt.ylabel('충전기 개수')
    plt.title(f'{selected_si} 내 충전기 개수 비교')
    plt.tight_layout()

    graph_popup = tk.Toplevel(root)
    graph_popup.title("충전기 개수 비교 그래프")

    canvas = tk.Canvas(graph_popup, width=800, height=600)
    canvas.pack()

    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    img = Image.open(img_buf)
    img = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, anchor='nw', image=img)
    canvas.image = img


# 이메일 전송 함수
def send_email():
    sender_email = "sungrok@tukorea.ac.kr"
    receiver_email = "lilspicypepper@gmail.com"
    password = "jxdy yszv hjlf annw"

    subject = "즐겨찾기 충전소 목록"
    body = "즐겨찾기한 충전소 목록입니다:\n\n"

    for fav in favorites:
        body += f"충전소명: {fav[0]}\n주소: {fav[4]}\n상세위치: {fav[5]}\n이용가능시간: {fav[7]}\n운영기관명: {fav[8]}\n주차료: {fav[9]}\n이용자 제한: {fav[10]}\n\n"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        messagebox.showinfo("정보", "이메일이 성공적으로 전송되었습니다.")
    except Exception as e:
        messagebox.showerror("에러", f"이메일 전송 중 오류가 발생했습니다: {str(e)}")


# GIF 애니메이션 함수
def animate_gif():
    global gif_frames, gif_label, gif_index

    gif_index += 1
    gif_index %= len(gif_frames)
    gif_frame = gif_frames[gif_index]

    gif_label.config(image=gif_frame)
    root.after(100, animate_gif)  # 100ms 간격으로 프레임 전환


def load_gif():
    global gif_frames, gif_label, gif_index

    gif = Image.open(gif_path)
    original_frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(gif)]

    desired_width = 100
    desired_height = 100
    # 이미지 크기 조절
    resized_frames = [frame.resize((desired_width, desired_height), Image.LANCZOS) for frame in original_frames]

    gif_frames = [ImageTk.PhotoImage(frame) for frame in resized_frames]
    gif_index = 0

    gif_label = tk.Label(search_frame)
    gif_label.grid(row=0, column=8, rowspan=2, padx=5, pady=5, sticky="e")  # search_frame에 추가하여 오른쪽에 배치
    animate_gif()


# GUI 초기 설정
root = tk.Tk()
root.title("밥줘")
root.geometry("800x800")

# 프레임 설정
search_frame = tk.Frame(root)
search_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

result_frame = tk.Frame(root)
result_frame.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="nsew")  # 상단 여백을 제거

notebook_frame = tk.Frame(root)
notebook_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

button_frame = tk.Frame(root)
button_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_columnconfigure(0, weight=1)

# 시/군 목록
cities = [
    "수원시", "성남시", "의정부시", "안양시", "부천시", "광명시", "평택시", "동두천시", "안산시", "고양시",
    "과천시", "구리시", "남양주시", "오산시", "시흥시", "군포시", "의왕시", "하남시", "용인시", "파주시",
    "이천시", "안성시", "김포시", "화성시", "광주시", "양주시", "포천시", "여주시", "연천군", "가평군", "양평군"
]
cities.sort()

# 시 콤보박스
si_label = tk.Label(search_frame, text="시/군 선택:")
si_label.grid(row=0, column=0, padx=5, sticky="w")
si_combo = ttk.Combobox(search_frame, values=cities)
si_combo.grid(row=0, column=1, padx=5, sticky="ew")

# 검색 결과 개수 라벨
count_label = tk.Label(search_frame, text="")
count_label.grid(row=0, column=2, padx=5, sticky="e")

# 검색 버튼
search_button = tk.Button(search_frame, text="검색", command=search)
search_button.grid(row=0, column=3, padx=5, sticky="e")

# 지도 버튼
map_button = tk.Button(search_frame, text="지도", command=show_map_popup)
map_button.grid(row=0, column=4, padx=5, sticky="e")

# 즐겨찾기 버튼
add_fav_button = tk.Button(search_frame, text="즐겨찾기", command=lambda: add_to_favorites(tree, favorites))
add_fav_button.grid(row=0, column=5, padx=5, sticky="e")

# 충전소 개수 그래프 버튼
graph_button = tk.Button(search_frame, text="그래프", command=show_graph)
graph_button.grid(row=0, column=6, padx=5, sticky="e")

# 이메일 버튼
email_button = tk.Button(search_frame, text="이메일", command=send_email)
email_button.grid(row=0, column=7, padx=5, sticky="e")

# 충전소 목록 내 텍스트 검색창
search_label = tk.Label(search_frame, text="결과 내 검색:")
search_label.grid(row=1, column=0, padx=5, sticky="w")
search_entry = tk.Entry(search_frame)
search_entry.grid(row=1, column=1, columnspan=6, padx=5, pady=5, sticky="ew")


def filter_list(event):
    query = search_entry.get().lower()
    filtered_data = [row for row in charger_data if query in row[0].lower()]

    unique_filtered_data = {}
    for row in filtered_data:
        if row[0] not in unique_filtered_data:
            unique_filtered_data[row[0]] = row

    filtered_data = list(unique_filtered_data.values())
    filtered_data.sort(key=lambda x: x[0])  # 충전소명을 기준으로 정렬

    for row in tree.get_children():
        tree.delete(row)

    for row in filtered_data:
        tree.insert('', tk.END, values=(row[0],))


search_entry.bind("<KeyRelease>", filter_list)

# 테이블 생성 (충전소명만 표시)
notebook = ttk.Notebook(notebook_frame)
notebook.pack(fill=tk.BOTH, expand=True)

tree_frame = ttk.Frame(notebook)
notebook.add(tree_frame, text="충전소 목록")

tree_scroll = tk.Scrollbar(tree_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(tree_frame, columns=('충전소명',), show='headings', height=30, yscrollcommand=tree_scroll.set)  # 높이 조정
tree.heading('충전소명', text='충전소명')
tree.column('충전소명', width=300, minwidth=300)  # 충전소 목록 박스의 최소 너비 설정
tree_scroll.config(command=tree.yview)
tree.pack(fill=tk.BOTH, expand=True)

# 즐겨찾기 목록 페이지
fav_tree_frame = ttk.Frame(notebook)
notebook.add(fav_tree_frame, text="즐겨찾기 목록")

fav_tree_scroll = tk.Scrollbar(fav_tree_frame)
fav_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

fav_tree = ttk.Treeview(fav_tree_frame, columns=('충전소명',), show='headings', height=15,
                        yscrollcommand=fav_tree_scroll.set)  # 높이 조정
fav_tree.heading('충전소명', text='충전소명')
fav_tree.column('충전소명', width=300, minwidth=300)  # 즐겨찾기 목록 박스의 최소 너비 설정
fav_tree_scroll.config(command=fav_tree.yview)
fav_tree.pack(fill=tk.BOTH, expand=True)

# 노트북(탭) 위젯 생성
detail_notebook = ttk.Notebook(button_frame)
detail_notebook.pack(fill=tk.BOTH, expand=True)

# 상세 정보 페이지
details_frame = ttk.Frame(detail_notebook)
detail_notebook.add(details_frame, text='상세 정보')

details_text = tk.Text(details_frame, height=15, width=50)  # 상세 정보 박스의 높이와 너비 설정
details_text.pack(fill=tk.BOTH, expand=True)

# 충전기 상태 페이지
status_frame = ttk.Frame(detail_notebook)
detail_notebook.add(status_frame, text='충전기 상태')

status_text = tk.Text(status_frame, height=15, width=50)  # 충전기 상태 박스의 높이와 너비 설정
status_text.pack(fill=tk.BOTH, expand=True)


# 즐겨찾기 목록에 추가하는 함수
def add_to_favorites(tree, favorites):
    selected_item = tree.focus()
    if selected_item:
        values = tree.item(selected_item, 'values')
        full_info = next((row for row in charger_data if row[0] == values[0]), None)
        if full_info and full_info not in favorites:
            favorites.append(full_info)
            messagebox.showinfo("정보", "즐겨찾기에 추가되었습니다.")
            fav_tree.insert('', tk.END, values=(full_info[0],))
        else:
            messagebox.showwarning("경고", "이미 즐겨찾기에 추가된 항목입니다.")
    else:
        messagebox.showwarning("경고", "추가할 항목을 선택하세요.")


# 상세 정보 표시 함수
def show_details(event):
    global selected_lat, selected_lng, selected_station_name, selected_station_charger_count
    selected_item = event.widget.focus()
    if selected_item:
        values = event.widget.item(selected_item, 'values')
        if event.widget == tree:
            full_infos = [row for row in charger_data if row[0] == values[0]]
        else:
            full_infos = [row for row in favorites if row[0] == values[0]]

        if full_infos:
            # 상세 정보는 충전소 당 하나만 표시
            details_text.delete(1.0, tk.END)
            info = full_infos[0]
            details_text.insert(tk.END, f"충전소명: {info[0]}\n\n")
            details_text.insert(tk.END, f"주소: {info[4]}\n\n")
            details_text.insert(tk.END, f"상세위치: {info[5]}\n\n")
            details_text.insert(tk.END, f"이용가능시간: {info[7]}\n\n")
            details_text.insert(tk.END, f"운영기관명: {info[8]}\n\n")
            details_text.insert(tk.END, f"주차료: {info[9]}\n\n")
            details_text.insert(tk.END, f"이용자 제한: {info[10]}\n\n")
            if info[10] == "이용자 제한 있음":
                details_text.insert(tk.END, f"이용제한 사유: {info[11]}\n\n")

            # 충전기 상태는 여러 개 표시
            status_text.delete(1.0, tk.END)
            for info in full_infos:
                status_text.insert(tk.END, f"충전기 ID: {info[2]}\n")
                status_text.insert(tk.END, f"충전기 타입: {charger_type_map.get(info[3], '알 수 없음')}\n")
                status_text.insert(tk.END, f"충전기 상태: {charger_status_map.get(info[6], '알 수 없음')}\n")
                status_text.insert(tk.END, "-" * 40 + "\n")

            # 지도 좌표 저장
            selected_lat = float(info[12])
            selected_lng = float(info[13])
            selected_station_name = info[0]
            selected_station_charger_count = len(full_infos)


tree.bind("<Double-1>", show_details)
fav_tree.bind("<Double-1>", show_details)

# GIF 파일 경로 설정 및 애니메이션 로드
gif_path = "ChargingAnim.gif"
load_gif()

# GUI 실행
root.mainloop()
