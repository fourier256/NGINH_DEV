class Unit {
    constructor() {
        this.name = 'none';
        this.x = 0;
        this.y = 0;
        this.id = 'none';
        this.sprite = null;
        this.move_to_x = 0;
        this.move_to_y = 0;
        this.speed = 1;
    }
    
    updateUnit() {
        this.sprite.animate();
        if(this.move_to_x > this.x) {
            this.sprite.setCurrentAnimation('walk_rr');
            this.x += this.speed;
            if(this.stage.isCollide(this)) {
                this.x -= this.speed;
                this.move_to_x = this.x;
            }
            if(this.move_to_x == this.x) {
                this.sprite.setCurrentAnimation('stand_rr');
            }
        }
        if(this.move_to_x < this.x) {
            this.sprite.setCurrentAnimation('walk_ll');
            this.x -= this.speed;
            if(this.stage.isCollide(this)) {
                this.x += this.speed;
                this.move_to_x = this.x;
            }
            if(this.move_to_x == this.x) {
                this.sprite.setCurrentAnimation('stand_ll');
            }
        }
        if(this.move_to_y < this.y) {
            this.sprite.setCurrentAnimation('walk_uu');
            this.y -= this.speed;
            if(this.stage.isCollide(this)) {
                this.y += this.speed;
                this.move_to_y = this.y;
            }
            if(this.move_to_y == this.y) {
                this.sprite.setCurrentAnimation('stand_uu');
            }
        }
        if(this.move_to_y > this.y) {
            this.sprite.setCurrentAnimation('walk_dd');
            this.y += this.speed;
            if(this.stage.isCollide(this)) {
                this.y -= this.speed;
                this.move_to_y = this.y;
            }
            if(this.move_to_y == this.y) {
                this.sprite.setCurrentAnimation('stand_dd');
            }
        }
    }
    
    drawUnit(paint) {
        this.sprite.drawSprite(paint, this.x, this.y);
        paint.strokeRect(this.x-16, this.y-16, 32, 32, 1, 0, 255, 0, 1);
    }
    
    clone() {
        let unit = new Unit();
        Object.assign(unit, this);
        unit.sprite = new Sprite();
        Object.assign(unit.sprite, this.sprite);
        return unit;
    }
}