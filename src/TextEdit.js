class TextEdit extends Element {
	constructor(text, x, y, w, h, id) {
		super(true, true, true, true, true); // drawable, updatable, pointable, keyable
		this.text = text;
		this.x = x;
		this.y = y;
		this.w = w;
		this.h = h;
		this.state = 'IDLE';
		this.id = id;
		this.update_duration = 0;
		this.frame = 1;
	}

	setCallback(callback) {
		this.callback = callback;
	}

	setText(text) {
		this.text = text;
	}

	getText() {
		return this.text;
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
		if (this.state == 'IDLE' || this.state == 'PUSHED') {
			paint.drawRect(this.x, this.y, this.w, this.h, 1, 0, 0, 0, 1.0, 255, 255, 255, 1.0);
		} else if (this.state == 'FOCUS') {
			paint.drawRect(this.x, this.y, this.w, this.h, 2, 0, 0, 0, 1.0, 255, 255, 255, 1.0);
			if (this.frame == 1) {
				paint.drawRect(this.x + paint.measTextWidth(this.text, 12) + 6, this.y + this.h / 2 - 6, 1, 12, 0, 0, 0, 0, 1.0, 0, 0, 0, 1.0);
			}
		}
		paint.drawText(this.text, this.x + 4, this.y + this.h / 2 + 4.5, 12, 0, 0, 0, 1.0, "left");
	}

	onUpdate() {
		this.update_duration++;
		if (this.update_duration == 60) {
			this.update_duration = 0;
			this.frame++;
			if (this.frame == 2) {
				this.frame = 0;
			}
		}
	}

	onPointDown(x, y) {
		if (this.isInRect(x, y)) {
			this.state = 'PUSHED';
		} else {
			this.state = 'IDLE'
			if (this.callback == undefined) {
				console.log('No callback for' + id);
			} else {
				this.callback(this.id);
			}
		}
	}
	onPointMove(x, y) {
		if (this.state == 'PUSHED') {
			if (!this.isInRect(x, y)) {
				this.state = 'IDLE';
				//document.getElementById('viertual_keyboard_caller').blur();
				if (this.callback == undefined) {
					console.log('No callback for' + id);
				} else {
					this.callback(this.id);
				}
			}
		}
	}
	onPointUp(x, y) {
		if (this.state == 'PUSHED') {
			this.state = 'FOCUS';
			//document.getElementById('viertual_keyboard_caller').focus();
		}
	}
	onKeyDown(key_code) {
		if (this.state == 'FOCUS') {
			let alphabet = 'abcdefghijklmnopqrstuvwxyz';
			let number = '0123456789';
			let underbar = '_';

			if (64 < key_code && key_code < 91) {
				this.text += alphabet.substr(key_code - 65, 1);
			} else if (47 < key_code && key_code < 58) {
				this.text += number.substr(key_code - 48, 1);
			} else if (key_code == 189) {
				this.text += underbar;
			} else if (key_code == 8) {
				if (this.text.length > 0) {
					this.text = this.text.substr(0, this.text.length - 1);
				}
			} else if (key_code == 13) {
				this.state = 'IDLE';
				//document.getElementById('viertual_keyboard_caller').blur();
				if (this.callback == undefined) {
					console.log('No callback for' + id);
				} else {
					this.callback(this.id);
				}
			}
		}
		//console.log('key down : '+key_code);
	}

	onKeyUp(key_code) {
		//console.log('key up : '+key_code);
	}
}