class Paint {
  constructor(ctx) {
    this.ctx = ctx;
    this.image_name_pool = [];
    this.image_pool = [];
  }

  loadImage(name, src) {
    this.image_name_pool.push(name);
    this.image_pool.push(new Image());
    this.image_pool[this.image_pool.length - 1].src = src;
  }

  drawRect(x, y, w, h, sw, sr, sg, sb, sa, fr, fg, fb, fa) {
    this.ctx.lineWidth = sw;
    this.ctx.strokeStyle = "rgba(" + sr + "," + sg + "," + sb + "," + sa + ")";
    this.ctx.fillStyle = "rgba(" + fr + "," + fg + "," + fb + "," + fa + ")";
    this.ctx.fillRect(x, y, w, h);
    if (sw != 0) {
      this.ctx.strokeRect(x + sw / 2, y + sw / 2, w - sw, h - sw);
    }
  }

  drawText(text, x, y, size, r, g, b, a, align) {
    this.ctx.fillStyle = "rgba(" + r + "," + g + "," + b + "," + a + ")";
    this.ctx.font = size + "px Sans serif";
    this.ctx.textAlign = align;
    this.ctx.fillText(text, x, y);
  }

  measTextWidth(text, size) {
    this.ctx.font = size + "px Sans serif";
    return this.ctx.measureText(text).width;
  }

  measTextHeight(text, size) {
    return size - 3;
  }

  drawImage(name, sx, sy, sw, sh, dx, dy, dw, dh) {
    for (let i = 0; i < this.image_name_pool.length; i++) {
      if (this.image_name_pool[i] == name) {
        this.ctx.drawImage(this.image_pool[i], sx, sy, sw, sh, dx, dy, dw, dh);
      }
    }
  }
}
