class Select extends Element {
  constructor(x, y, w, id) {
    super(true, false, true, false); // drawable, pointable
    this.x = x;
    this.y = y;
    this.w = w;
    this.id = id;
    this.idx = 0;
    this.item = [];
    this.state = 'IDLE';
  }

  addItem(text) {
    this.item.push(text);
  }

  removeItem(text) {
    for (let i = 0; i < this.item.length; i++) {
      if (this.item[i] == text) {
        this.item.splice(i, 1);
      }
    }
  }

  getItem(idx) {
    return this.item[idx];
  }

  getSelect() {
    return this.idx;
  }

  getSelectItem() {
    return this.getItem(this.idx);
  }

  setSelect(idx) {
    this.idx = idx;
  }
  isInRect_IDLE(x, y) {
    if (this.x < x && x < this.x + this.w) {
      if (this.y < y && y < this.y + 16) {
        return true;
      }
    }
    return false;
  }

  isInRect_SELECT(x, y, i) {
    if (this.x < x && x < this.x + this.w) {
      if (this.y + (i * 16) < y && y < this.y + (i * 16) + 16) {
        return true;
      }
    }
    return false;
  }

  getSelect() {
    return this.item[this.idx];
  }

  onDraw(paint) {
    paint.drawRect(this.x, this.y, this.w, 16, 1, 31, 31, 31, 1.0, 255, 255, 255, 1.0);
    paint.drawRect(this.x + this.w - 16, this.y, 16, 16, 1, 31, 31, 31, 1.0, 195, 195, 195, 1.0);

    paint.ctx.fillStyle = "rgba(0, 0, 0, 1.0)";
    paint.ctx.beginPath();
    paint.ctx.moveTo(this.x + this.w - 16 + 4, this.y + 4);
    paint.ctx.lineTo(this.x + this.w - 4, this.y + 4);
    paint.ctx.lineTo(this.x + this.w - 8, this.y + 16 - 4);
    paint.ctx.closePath();
    paint.ctx.fill();

    if (this.item.length > 0) {
      paint.drawText(this.item[this.idx], this.x + 2, this.y + 16 / 2 + 4.5, 12, 0, 0, 0, 1.0, "left");
    }
    if (this.state == 'SELECT') {
      paint.drawRect(this.x, this.y + 16 - 1, this.w, 16 * this.item.length, 1, 31, 31, 31, 1.0, 255, 255, 255, 1.0);
      paint.drawRect(this.x + 1, this.y + 16 + 16 * this.idx, this.w - 2, 14, 0, 0, 0, 0, 0.0, 127, 255, 255, 1.0);
      for (let i = 0; i < this.item.length; i++) {
        paint.drawText(this.item[i], this.x + 2, this.y + 16 / 2 + 4.5 + (16 * i) + 16, 12, 0, 0, 0, 1.0, "left");
      }
    }
  }

  onPointDown(x, y) {
    if (this.state == 'IDLE') {
      if (this.isInRect_IDLE(x, y)) {
        this.state = 'SELECT';
      }
    }
  }
  onPointMove(x, y) {
    if (this.state == 'SELECT') {
      for (let i = 0; i < this.item.length; i++) {
        if (this.isInRect_SELECT(x, y, i + 1)) {
          this.idx = i;
        }
      }
    }
  }
  onPointUp(x, y) {
    if (this.state == 'SELECT') {
      this.state = 'IDLE';
      if (this.callback == undefined) {
        //console.log('No callback for' + id);
      } else {
        this.callback(this.id);
      }
    }
  }
}
