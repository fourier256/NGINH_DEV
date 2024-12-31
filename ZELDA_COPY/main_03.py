from PIL import Image
import numpy as np
import cv2  # OpenCV 라이브러리
from scipy.spatial.distance import cdist

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


tileset_image = Image.open("assets/tileset.png")

for i_map in range(144) :
    file_in = open('assets/tilemap/tilemap_' + str(i_map).zfill(3) + '.arr', 'r')
    all_contents = file_in.readlines()
    width = 32
    height = 32
    buf = []
    for line in all_contents :
        if line.startswith('W') :
            width = int(line.split('=')[1])
        elif line.startswith('H') :
            height = int(line.split('=')[1])
        else :
            words = line.split()
            for word in words :
                buf.append(int(word))
    map = []
    for i_y in range(height) :
        map.append([])
        for i_x in range(width) :
            map[i_y].append(buf[i_y*width+i_x])

    generate_image_from_tilemap(np.array(map), tileset_image, 8, 'test/tilemap_' + str(i_map).zfill(3) + '.png')