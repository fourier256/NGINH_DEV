from PIL import Image
import numpy as np
import cv2  # OpenCV 라이브러리
from scipy.spatial.distance import cdist

# 타일셋 이미지 로드
tileset_image = Image.open("assets/tileset.png")

# 타일 크기 (16x16)
tile_size = 8

# 타일셋의 가로, 세로 크기 계산
tileset_width, tileset_height = tileset_image.size
tiles_across = tileset_width // tile_size
tiles_down = tileset_height // tile_size

# 타일셋에서 각 타일 추출
def get_tile_histogram(tile_image):
    """타일 이미지에서 히스토그램을 계산"""
    tile_image = tile_image.convert("RGB")  # PIL 이미지에서 RGB로 변환
    tile_cv_image = np.array(tile_image)  # NumPy 배열로 변환
    tile_cv_image = cv2.cvtColor(tile_cv_image, cv2.COLOR_RGB2BGR)  # OpenCV에서 사용하는 BGR로 변환
    
    # BGR 이미지를 OpenCV에서 사용하는 형식으로 전달
    hist = cv2.calcHist([tile_cv_image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()  # 히스토그램을 정규화하여 1차원 배열로 변환
    return hist

# 타일셋의 모든 타일의 히스토그램 계산
tile_histograms = []
for ty in range(tiles_down):
    for tx in range(tiles_across):
        # 타일 이미지 추출
        tile = tileset_image.crop((tx * tile_size, ty * tile_size, (tx + 1) * tile_size, (ty + 1) * tile_size))
        tile_hist = get_tile_histogram(tile)
        tile_histograms.append(tile_hist)

# 타일맵 이미지를 로드
tilemap_image = Image.open("tilemap_all.png")

# 타일맵 크기 계산
img_width, img_height = tilemap_image.size
tiles_across_map = img_width // tile_size
tiles_down_map = img_height // tile_size

# 타일맵에 대한 인덱스를 저장할 배열
tilemap = np.zeros((tiles_down_map, tiles_across_map), dtype=int)

# 타일맵의 각 타일을 분석하고 가장 유사한 타일을 찾기
for y in range(tiles_down_map):
    for x in range(tiles_across_map):
        # 타일맵에서 타일 추출
        tile = tilemap_image.crop((x * tile_size, y * tile_size, (x + 1) * tile_size, (y + 1) * tile_size))
        
        # 타일맵 타일의 히스토그램 계산
        tile_hist = get_tile_histogram(tile)
        
        # 타일셋에서 가장 비슷한 타일을 찾기 위해 히스토그램 차이 계산
        distances = cdist([tile_hist], tile_histograms, metric='euclidean')  # 유클리드 거리 계산
        most_similar_tile_index = np.argmin(distances)  # 가장 유사한 타일의 인덱스를 찾음
        
        # 타일맵에 인덱스를 할당
        tilemap[y][x] = most_similar_tile_index



# 타일맵 데이터를 기준으로 타일셋을 조합하여 이미지를 생성
def generate_image_from_tilemap(tilemap, tileset_image, tile_size, output_path):
    """타일맵 데이터를 기준으로 타일셋으로 이미지를 조합"""
    tileset_width, tileset_height = tileset_image.size
    tiles_across = tileset_width // tile_size
    
    # 타일맵의 크기 계산
    tiles_down_map, tiles_across_map = tilemap.shape
    output_image = Image.new("RGB", (tiles_across_map * tile_size, tiles_down_map * tile_size))
    
    for y in range(tiles_down_map):
        for x in range(tiles_across_map):
            # 타일맵에서 타일 인덱스 가져오기
            tile_index = tilemap[y][x]
            ty = tile_index // tiles_across
            tx = tile_index % tiles_across
            
            # 타일셋에서 해당 타일 추출
            tile = tileset_image.crop((tx * tile_size, ty * tile_size, (tx + 1) * tile_size, (ty + 1) * tile_size))
            
            # 타일을 재구성된 이미지에 삽입
            output_image.paste(tile, (x * tile_size, y * tile_size))
    
    # 최종 이미지를 저장
    output_image.save(output_path)
    print(f"Reconstructed image saved to {output_path}")

def split_into_segments(array, segment_height, segment_width):
    h, w = array.shape
    if h % segment_height != 0 or w % segment_width != 0:
        raise ValueError("Array dimensions are not divisible by segment dimensions.")
    
    segments = []
    for i in range(0, h, segment_height):
        for j in range(0, w, segment_width):
            segment = array[i:i + segment_height, j:j + segment_width]
            segments.append(segment)
    return segments

seg = split_into_segments(tilemap, 22, 32)
for i_map in range(len(seg)) :
    file_out = open('tilemap_' + str(i_map).zfill(3) + '.arr', 'w')
    height = len(seg[i_map])
    width = len(seg[i_map][0])
    file_out.write('W=' + str(width) + '\n')
    file_out.write('H=' + str(height) + '\n')
    for i_y in range(height) :
        for i_x in range(width) :
            file_out.write(str(seg[i_map][i_y][i_x]).zfill(3) + ' ')
        file_out.write('\n')



# 타일맵 데이터를 기반으로 이미지를 생성하여 저장
#output_image_path = "reconstructed_tilemap.png"
#generate_image_from_tilemap(tilemap, tileset_image, tile_size, output_image_path)


# 결과 출력 (타일맵의 인덱스 배열)
#print(tilemap)

