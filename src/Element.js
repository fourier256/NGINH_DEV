class Element {
  constructor(drawable, updatable, pointable, keyable) {
    this.drawable = drawable;
    this.updateable = updatable;
    this.pointable = pointable;
    this.keyable = keyable;
  }

  onUpdate() {
    if (this.updatable) {
      throw new Error('onUpdate() must be implemented for updatable element');
    } else {
      throw new Error('onUpdate() called for non-updatable element');
    }
  }

  onDraw(paint) {
    if (this.drawable) {
      throw new Error('onDraw() must be implemented for drawable element');
    } else {
      throw new Error('onDraw() called for non-drawable element');
    }
  }

  onPointDown(x, y) {
    if (this.pointable) {
      throw new Error('onPointDown() must be implemented for pointable element');
    } else {
      throw new Error('onPointDown() called for non-pointable element');
    }
  }

  onPointMove(x, y) {
    if (this.pointable) {
      throw new Error('onPointMove() must be implemented for pointable element');
    } else {
      throw new Error('onPointMove() called for non-pointable element');
    }
  }

  onPointUp(x, y) {
    if (this.pointable) {
      throw new Error('onPointUp() must be implemented for pointable element');
    } else {
      throw new Error('onPointUp() called for non-pointable element');
    }
  }

  onKeyDown(key_code) {
    if (this.keyable) {
      throw new Error('onKeyDown() must be implemented for keyable element');
    } else {
      throw new Error('onKeyDown() called for non-keyable element');
    }
  }

  onKeyUp(key_code) {
    if (this.keyable) {
      throw new Error('onKeyUp() must be implemented for keyable element');
    } else {
      throw new Error('onKeyUp() called for non-keyable element');
    }
  }
}
