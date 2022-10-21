class Button extends Element {
    
    static STATE = class {
        static IDLE = 0;
        static PUSH = 1;
    }
    
    constructor(x, y, sprite, id, stage) {
        super(true, false, true, false);
        this.x = x;
        this.y = y;
        this.sprite = sprite;
        this.idle_frame = 0;
        this.push_frame = 1;
        this.state = Button.STATE.IDLE;
        this.stage = stage;
    }
    
    isInRect(x, y) {
        if(this.x<x && x<this.x+this.sprite.w*this.sprite.size) {
            if(this.y<y && y<this.y+this.sprite.h+this.sprite.size) {
                return true;
            }
        }
        return false;
    }
    
    setFrame(idle_frame, push_frame) {
        this.idle_frame = idle_frame;
        this.push_frame = push_frame;
    }
    
    onDraw(paint) {
        switch(this.state) {
            case Button.STATE.IDLE :
                this.sprite.drawSpriteFrame(paint, this.idle_frame, x, y);
                break;
            case Button.STATE.PUSH:
                this.sprite.drawSpriteFrame(paint, this.push_frame, x, y);
                break;
        }
    }
    
    onPointDown(x, y) {
        if(this.isInRect(x, y)) {
            this.state = Button.STATE.PUSH;
        }
    }
    
    onPointMove(x, y) {
        if(this.isInRect(x, y)) {
            this.state = Button.STATE.IDLE;
        }
    }
    onPointUp(x, y) {
        if(this.state==Button.STATE.PUSH) {
            this.state = Button.State.IDLE;
            if(this.callback==undefined) {
                Log.logError('No callback for' + id);
            }
            else {
                this.callback(this.id, this.stage);
            }
        }
    }
}