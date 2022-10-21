class TextButton extends Element {
	constructor(text, x, y, w, h, stage, id) {
		super(true, false, true, false); // drawable, pointable
		this.text = text;
		this.x = x;
		this.y = y;
		this.w = w;
		this.h = h;
		this.id = id;
        this.stage = stage;
		this.state = 'IDLE'
	}

	setCallback(callback) {
		this.callback = callback;
	}

	isInRect(x, y) {
		if (this.x < x && x < this.x + this.w) {
			if (this.y < y && y < this.y + this.h) {
				return true;
			}
		}
		return false;
	}

	onDraw(paint) {
		//let width = parseInt(paint.measTextWidth(this.text, 12))+16;
		//let height = parseInt(paint.measTextHeight(this.text, 12))+8;
		let width = 100;
		let height = 10;
		if (this.state == 'IDLE') {
			paint.drawRect(this.x, this.y, this.w, this.h, 1, 127, 127, 127, 1.0, 195, 195, 195, 1.0);
			paint.drawText(this.text, this.x + (this.w / 2), this.y + this.h / 2 + 4.5, 12, 0, 0, 0, 1.0, "center");
		} else {
			paint.drawRect(this.x, this.y, this.w, this.h, 1, 127, 127, 127, 1.0, 175, 175, 175, 1.0);
			paint.drawText(this.text, this.x + (this.w / 2), this.y + this.h / 2 + 4.5, 12, 0, 0, 0, 1.0, "center");
		}
	}

	onPointDown(x, y) {
		if (this.isInRect(x, y)) {
			this.state = 'PUSHED';
		}
	}
	onPointMove(x, y) {
		if (!this.isInRect(x, y)) {
			this.state = 'IDLE';
		}
	}
	onPointUp(x, y) {
		if (this.state == 'PUSHED') {
			this.state = 'IDLE';
			if (this.callback == undefined) {
				console.log('No callback for' + id);
			} else {
				this.callback(this.id, this.stage);
			}
		}
	}
}