class G_Object:
    def __init__(self, max_hp, max_mp, speed, x_position, y_position, direction, sprite_model):
        self.max_hp = max_hp
        self.hp = max_hp
        self.max_mp = max_mp
        self.mp = max_mp
        self.speed = speed
        self.x_position = x_position
        self.y_position = y_position
        self.direction = direction
        self.sprite_model = sprite_model

    def on_draw(self, screen):
        if self.sprite_model:
            self.sprite_model.on_draw(screen, self.x_position, self.y_position)

    def on_update(self, delta_time):
        # TODO: Add update logic here
        pass

    def on_clicked(self):
        # TODO: Add click logic here
        pass

    def on_key_down(self, key):
        # TODO: Add key down logic here
        pass

    def on_key_up(self, key):
        # TODO: Add key up logic here
        pass