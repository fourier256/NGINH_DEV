class Stage {
  constructor() {
    this.element = [];
    this.drawable = [];
    this.updatable = [];
    this.pointable = [];
    this.keyable = [];
    this.trigger = [];
    this.tilemap = null;
    this.unit = [];
  }

  addNewTextButton(text, x, y, w, h, id) {
    let new_element = new TextButton(text, x, y, w, h, id);
    new_element.setCallback(this.onButtonClick);
    this.element.push(new_element);
    this.drawable.push(new_element);
    this.pointable.push(new_element);
  }

  addNewButton(x, y, sprite, id) {
    let new_element = new Button(x, y, sprite, id);
    new_element.setCallback(this.onButtonClick);
    this.element.push(new_element);
    this.drawable.push(new_element);
    this.pointable.push(new_element);
  }

  addNewTextEdit(text, x, y, w, h, id) {
    let new_element = new TextEdit(text, x, y, w, h, id);
    this.element.push(new_element);
    this.drawable.push(new_element);
    this.updatable.push(new_element);
    this.pointable.push(new_element);
    this.keyable.push(new_element);
  }
  addNewText(text, x, y, w, font_size, id) {
    let new_element = new Text(text, x, y, w, font_size, id);
    this.element.push(new_element);
    this.drawable.push(new_element);
  }

  addNewSelect(x, y, w, id) {
    let new_element = new Select(x, y, w, id);
    this.element.push(new_element);
    this.drawable.push(new_element);
    this.pointable.push(new_element);
  }

  getElement(id) {
    for (let i = 0; i < this.element.length; i++) {
      if (this.element[i].id == id) {
        return this.element[i];
      }
    }
  }

  onInitialize(stage_data, unit_pool, sprite_model_pool, sprite_animation_pool, sprite_pool) {
    this.tilemap = new TileMap(stage_data.tilemap, sprite_pool);
    for (let i = 0; i < stage_data.unitmap.length; i++) {
    //for (let i = 0; i < 1; i++) {
      let name = stage_data.unitmap[i].name;
      let x = stage_data.unitmap[i].x;
      let y = stage_data.unitmap[i].y;
      let id = stage_data.unitmap[i].id;
      this.unit.push(new Unit(unit_pool, sprite_model_pool, sprite_animation_pool, sprite_pool, name, x, y, id))
    }
  }

  onUpdate() {
    for (let i = 0; i < this.updatable.length; i++) {
      this.updatable[i].onUpdate();
    }
    for (let i = 0; i < this.unit.length; i++) {
      this.unit[i].updateUnit();
    }
  }
  onDraw(paint) {
    this.tilemap.drawTilemap(paint);
    this.unit.sort(function(a, b) {
      return a.y - b.y;
    }); // z index sorting
    for (let i = 0; i < this.unit.length; i++) {
      this.unit[i].drawUnit(paint);
    }

    this.unit[0].sprite_model.sprite_animation[0].drawSpriteAnimation(paint);
    this.unit[0]
    //paint.drawImage('tileset', 0, 0, 32, 32, 32, 32, 32, 32);
    //for(let i=0; i<this.drawable.length; i++) {
    // this.drawable[i].onDraw(paint);
    //}
  }

  onPointDown(x, y) {
    for (let i = 0; i < this.pointable.length; i++) {
      this.pointable[i].onPointDown(x, y);
    }
  }

  onPointMove(x, y) {
    for (let i = 0; i < this.pointable.length; i++) {
      this.pointable[i].onPointMove(x, y);
    }
  }

  onPointUp(x, y) {
    for (let i = 0; i < this.pointable.length; i++) {
      this.pointable[i].onPointUp(x, y);
    }
  }

  onKeyDown(key_code) {
    for (let i = 0; i < this.keyable.length; i++) {
      this.keyable[i].onKeyDown(key_code);
    }
  }

  onKeyUp(key_code) {
    for (let i = 0; i < this.keyable.length; i++) {
      this.keyable[i].onKeyUp(key_code);
    }
  }

  onButtonClick(id) {
    //for(let i=0; i<this.trigger.length; i++) {
    // if(this.trigger[i].event.keyword=="ui_button_click" && this.trigger[i].event.id==id) {
    // parseTrigger(this.trigger[i]);
    // }
    //}
  }
  onSelect(id) {
    //for(let i=0; i<this.trigger.length; i++) {
    // if(this.trigger[i].event.keyword=="ui_select" && this.trigger[i].event.id==id) {
    // parseTrigger(this.trigger[i]);
    // }
    //}
  }
  onText(id) {
    //for(let i=0; i<this.trigger.length; i++) {
    // if(this.trigger[i].event.keyword=="ui_select" && this.trigger[i].event.id==id) {
    // parseTrigger(this.trigger[i]);
    // }
    //}
  }

  parseTrigger(trigger) {

  }
}
