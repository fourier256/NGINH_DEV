import pygame
import json

class G_TileMap:
    def __init__(self, tileset_image, map_file):
        self.tileset_image = tileset_image  # Pygame Surface containing the sprite sheet
        with open('assets/map/map_00.json', 'r') as file:
            data = json.load(file)

        # W, H 값 추출
        W = data["tilemap"]["W"]
        H = data["tilemap"]["H"]

        # tilemap 데이터를 1차원 배열에서 2차원 배열로 변환
        self.tilemap_arr = [
            data["tilemap"]["tilemap"][i * W:(i + 1) * W] for i in range(H)
        ]

    def on_draw(self, screen):
        frame_width = 8
        frame_height = 8
        for iY in range(len(self.tilemap_arr)) :
            for iX in range(len(self.tilemap_arr[iY])) :
                frame_index = self.tilemap_arr[iY][iX]
                #frame_index = 63
                frame_rect = pygame.Rect(
                    (frame_index % 64) * frame_width,  # Column position
                    (frame_index // 64) * frame_height,  # Row position
                    frame_width, frame_height
                )
                # Adjust drawing position to align X-axis to center and Y-axis to bottom
                draw_x = iX*8
                draw_y = iY*8
                # Draw the current frame on the screen
                screen.blit(self.tileset_image, (draw_x, draw_y), frame_rect)