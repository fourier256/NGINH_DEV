import pygame

class G_SpriteModel:
    def __init__(self, sprite_image, animation_dict):
        self.sprite_image = sprite_image  # Pygame Surface containing the sprite sheet
        self.curr_animation = "work"     # Current animation (default: "work")
        self.curr_direction = "d"       # Current direction (default: "d")
        self.curr_frame = 0              # Current frame index

        # Animation dictionary: keys represent animation states, values are lists of frame indices
        self.animation_dict = animation_dict

    def on_draw(self, screen, x, y):
        # Combine curr_animation and curr_direction to get the correct key
        animation_key = f"{self.curr_animation}_{self.curr_direction}"

        if animation_key in self.animation_dict:
            frame_indices = self.animation_dict[animation_key]
            frame_index = frame_indices[self.curr_frame % len(frame_indices)]

            # Calculate the frame's position and size on the sprite sheet
            #frame_width = self.sprite_image.get_width() // 4  # Assuming 8 columns
            #frame_height = self.sprite_image.get_height() // 4  # Assuming 2 rows
            frame_width = 16  # Assuming 8 columns
            frame_height = 16  # Assuming 2 rows
            frame_rect = pygame.Rect(
                (frame_index % 4) * frame_width,  # Column position
                (frame_index // 4) * frame_height,  # Row position
                frame_width, frame_height
            )

            # Adjust drawing position to align X-axis to center and Y-axis to bottom
            draw_x = x - frame_width // 2
            draw_y = y - frame_height

            # Draw the current frame on the screen
            screen.blit(self.sprite_image, (draw_x, draw_y), frame_rect)

        else:
            raise ValueError(f"Invalid animation key: {animation_key}")
