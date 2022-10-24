class Sprite {
	constructor() {
		this.w = 32;
		this.h = 32;
		this.n_frame_x = 1;
		this.n_frame_y = 1;
		this.img_name = 'none';
		this.name = 'none';
		this.size = 1.0;
		this.current_frame = 0;
		this.animation_set = new AnimationSet();
		this.current_animation = this.animation_set.stand_ll;
		this.animation_latency_count = 0;
		this.animation_latency = 100/this.current_animation.fps;
	}

	setSize(size) {
		this.size = size;
	}

	setCurrentAnimation(animation) {
		console.log(animation);
		if(animation != this.current_animation.name) {
			if(animation == 'stand_ll')		{this.current_animation = this.animation_set.stand_ll;}
			else if(animation == 'stand_rr'){this.current_animation = this.animation_set.stand_rr;}
			else if(animation == 'stand_up'){this.current_animation = this.animation_set.stand_up;}
			else if(animation == 'stand_dn'){this.current_animation = this.animation_set.stand_dn;}
			else if(animation == 'walk_ll')	{this.current_animation = this.animation_set.walk_ll;}
			else if(animation == 'walk_rr')	{this.current_animation = this.animation_set.walk_rr;}
			else if(animation == 'walk_up')	{this.current_animation = this.animation_set.walk_up;}
			else if(animation == 'walk_dn')	{this.current_animation = this.animation_set.walk_dn;}
			this.current_frame = 0;
			this.animation_latency_count = 0;
			this.animation_latency = 100/this.current_animation.fps;
		}
	}

	animate() {
		this.animation_latency_count++;
		if(this.animation_latency_count >= this.animation_latency) {
			this.current_frame++;
			if(this.current_frame >= this.current_animation.frames.length) {
				this.current_frame = 0;
			}
			this.animation_latency_count = 0;
		}
	}

	drawSprite(paint, x, y) {
		let frame = this.current_animation.frames[this.current_frame];
		let sx = (frame % this.n_frame_x) * this.w;
		let sy = parseInt(frame / this.n_frame_x) * this.h;
		paint.drawImage(this.img_name, sx, sy, this.w, this.h, x, y, this.w*this.size, this.h*this.size);
	}

	drawSpriteFrame(paint, frame, x, y) {
		let sx = (frame % this.n_frame_x) * this.w;
		let sy = parseInt(frame / this.n_frame_x) * this.h;
		paint.drawImage(this.img_name, sx, sy, this.w, this.h, x, y, this.w*this.size, this.h*this.size);
	}
}
