class Core {

	render() {
		this.draw(this.paint);
		requestAnimationFrame(render);
	}

	constructor(config) {
		this.canvas = document.createElement("canvas")
		this.ctx = this.canvas.getContext("2d")
		this.paint = new Paint(this.ctx);
		this.canvas.width = 640;
		this.canvas.height = 480;
		document.body.appendChild(this.canvas);

		this.load = config.scene.load;
		this.initialize = config.scene.initialize;
		this.draw = config.scene.draw;
		this.update = config.scene.update

		this.canvas.addEventListener('mousedown', (event) => {
			config.scene.event.onPointDown(event.offsetX, event.offsetY);
		});
		this.canvas.addEventListener('mouseup', (event) => {
			config.scene.event.onPointUp(event.offsetX, event.offsetY);
		});
		this.canvas.addEventListener('mousemove', (event) => {
			config.scene.event.onPointMove(event.offsetX, event.offsetY);
		});
		this.canvas.addEventListener('touchstart', (event) => {
			let bcr = event.target.getBoundingClientRect();
			let x = event.targetTouches[0].clientX - bcr.x;
			let y = event.targetTouches[0].clientY - bcr.y;
			config.scene.event.onPointDown(x, y);
		});
		this.canvas.addEventListener('touchend', (event) => {
			let bcr = event.target.getBoundingClientRect();
			let x = event.targetTouches[0].clientX - bcr.x;
			let y = event.targetTouches[0].clientY - bcr.y;
			config.scene.event.onPointUp(x, y);
		});
		this.canvas.addEventListener('touchmove', (event) => {
			let bcr = event.target.getBoundingClientRect();
			let x = event.targetTouches[0].clientX - bcr.x;
			let y = event.targetTouches[0].clientY - bcr.y;
			config.scene.event.onPointMove(x, y);
		});
		window.addEventListener('keydown', (event) => {
			let key_code = event.keyCode;
			config.scene.event.onKeyDown(key_code);
		}, true);

		window.addEventListener('keyup', (event) => {
			let key_code = event.keyCode;
			config.scene.event.onKeyUp(key_code);
		}, true);

		//setInterval(() => this.update(), 10);
		setInterval(() => this.update(), 10);
	}
	start() {
		this.draw();
	}
}