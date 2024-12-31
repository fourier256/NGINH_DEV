from PIL import Image
import numpy as np
import hashlib

#tileset 이미지 열고 각 

# 이미지 파일을 열고
image = Image.open("tilemap.png")

# 이미지 크기 확인
img_width, img_height = image.size

# 타일 크기 (16x16)
tile_size = 8

# 타일의 가로, 세로 개수 계산
tiles_across = img_width // tile_size
tiles_down = img_height // tile_size

# 타일 이미지들을 저장할 딕셔너리 (해시 값으로 비교)
tile_images = {}
tilemap = np.zeros((tiles_down, tiles_across), dtype=int)

def get_tile_hash(tile_image):
    """타일 이미지를 해시값으로 변환하여 고유한 값을 생성"""
    tile_bytes = tile_image.tobytes()  # 이미지를 바이트로 변환
    return hashlib.md5(tile_bytes).hexdigest()

# 타일 인덱스 초기화
tile_index = 0

# 타일을 순차적으로 분석
for y in range(tiles_down):
    for x in range(tiles_across):
        # 타일 이미지 잘라내기
        tile = image.crop((x * tile_size, y * tile_size, (x + 1) * tile_size, (y + 1) * tile_size))
        
        # 타일의 고유 해시 값 생성
        tile_hash = get_tile_hash(tile)
        
        # 동일한 타일이 있으면 이전 인덱스를 재사용
        if tile_hash not in tile_images:
            tile_images[tile_hash] = tile_index
            tile_index += 1
        
        # 해당 위치에 타일 인덱스 할당
        tilemap[y][x] = tile_images[tile_hash]

# 결과 출력 (타일 인덱스 배열)
print(tilemap)
