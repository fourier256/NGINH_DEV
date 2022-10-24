class SpritePool {
	constructor() {
		this.pool = [];
	}

	onInitialize(sprite_pool_data) {
		for (let i = 0; i < sprite_pool_data.length; i++) {
			
			let name = sprite_pool_data[i].name;
			let img_name = sprite_pool_data[i].img_name;
			let w = sprite_pool_data[i].w;
			let h = sprite_pool_data[i].h;
			let n_frame_x = sprite_pool_data[i].n_frame_x;
			let n_frame_y = sprite_pool_data[i].n_frame_y;
			let size = sprite_pool_data[i].size;

			let sprite = new Sprite();
			sprite.name = name;
			sprite.img_name = img_name;
			sprite.w = w;
			sprite.h = h;
			sprite.n_frame_x = n_frame_x;
			sprite.n_frame_y = n_frame_y;
			sprite.size = size;

			if(typeof(sprite_pool_data[i].animation_set.stand_ll)!='undefined') {
				sprite.animation_set.stand_ll.fps = sprite_pool_data[i].animation_set.stand_ll.fps;
				sprite.animation_set.stand_ll.frames = sprite_pool_data[i].animation_set.stand_ll.frames.slice();
			}
			if(typeof(sprite_pool_data[i].animation_set.stand_rr)!='undefined') {
				sprite.animation_set.stand_rr.fps = sprite_pool_data[i].animation_set.stand_rr.fps;
				sprite.animation_set.stand_rr.frames = sprite_pool_data[i].animation_set.stand_rr.frames.slice();
			}
			if(typeof(sprite_pool_data[i].animation_set.stand_up)!='undefined') {
				sprite.animation_set.stand_up.fps = sprite_pool_data[i].animation_set.stand_up.fps;
				sprite.animation_set.stand_up.frames = sprite_pool_data[i].animation_set.stand_up.frames.slice();
			}
			if(typeof(sprite_pool_data[i].animation_set.stand_dn)!='undefined') {
				sprite.animation_set.stand_dn.fps = sprite_pool_data[i].animation_set.stand_dn.fps;
				sprite.animation_set.stand_dn.frames = sprite_pool_data[i].animation_set.stand_dn.frames.slice();
			}
			if(typeof(sprite_pool_data[i].animation_set.walk_ll)!='undefined') {
				sprite.animation_set.walk_ll.fps = sprite_pool_data[i].animation_set.walk_ll.fps;
				sprite.animation_set.walk_ll.frames = sprite_pool_data[i].animation_set.walk_ll.frames.slice();
			}
			if(typeof(sprite_pool_data[i].animation_set.walk_rr)!='undefined') {
				sprite.animation_set.walk_rr.fps = sprite_pool_data[i].animation_set.walk_rr.fps;
				sprite.animation_set.walk_rr.frames = sprite_pool_data[i].animation_set.walk_rr.frames.slice();
			}
			if(typeof(sprite_pool_data[i].animation_set.walk_up)!='undefined') {
				sprite.animation_set.walk_up.fps = sprite_pool_data[i].animation_set.walk_up.fps;
				sprite.animation_set.walk_up.frames = sprite_pool_data[i].animation_set.walk_up.frames.slice();
			}
			if(typeof(sprite_pool_data[i].animation_set.walk_dn)!='undefined') {
				sprite.animation_set.walk_dn.fps = sprite_pool_data[i].animation_set.walk_dn.fps;
				sprite.animation_set.walk_dn.frames = sprite_pool_data[i].animation_set.walk_dn.frames.slice();
			}

			this.pool.push(sprite);
		}
	}

	getNewSprite(name) {
		for (let i = 0; i < this.pool.length; i++) {
			if (name == this.pool[i].name) {
				let sprite = new Sprite();
				Object.assign(sprite, this.pool[i]);
				return sprite;
			}
		}
		return new Sprite();
	}
}
