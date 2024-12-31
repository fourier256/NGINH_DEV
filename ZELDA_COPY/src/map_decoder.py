import json

# JSON 파일 읽기
with open('assets/map/map_00.json', 'r') as file:
    data = json.load(file)

# W, H 값 추출
W = data["tilemap"]["W"]
H = data["tilemap"]["H"]

# tilemap 데이터를 1차원 배열에서 2차원 배열로 변환
tilemap = [
    data["tilemap"]["tilemap"][i * W:(i + 1) * W] for i in range(H)
]

print(tilemap)