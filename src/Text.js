class Text extends Element {
	constructor(text, x, y, w, font_size, id) {
		super(true, false, false, false); // drawable
		this.text = text;
		this.x = x;
		this.y = y;
		this.w = w;
		this.font_size = font_size;
		this.id = id;
		this.r = 0;
		this.g = 0;
		this.b = 0;
		this.a = 1.0;
		this.line = [];
	}

	onDraw(paint) {
		if (this.line.length == 0) {
			this.line.push("");
			for (let i = 0; i < this.text.length; i++) {
				if (this.text.substr(i, 1) == "\n") {
					this.line.push("");
				} else {
					this.line[this.line.length - 1] += this.text.substr(i, 1);
				}
				if (paint.measTextWidth(this.line[this.line.length - 1], this.font_size) > this.w) {
					this.line[this.line.length - 1] = this.line[this.line.length - 1].substr(0, this.line[this.line.length - 1].length - 1);
					i--;
					this.line.push("");
				}
			}
		}

		for (let i = 0; i < this.line.length; i++) {
			paint.drawText(this.line[i], this.x, this.y + (i * this.font_size), this.font_size, this.r, this.g, this.b, this.a, "left");
		}
	}
}