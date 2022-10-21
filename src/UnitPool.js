class UnitPool {
    constructor() {
        this.pool = [];
    }
    
    onInitialize(unit_pool_data, sprite_pool) {
        for(let i=0; i<unit_pool_data.length; i++) {
            let unit = new Unit();
            unit.name = unit_pool_data[i].name;
            unit.sprite = sprite_pool.getNewSprite(unit_pool_data[i].sprite_name);
            this.pool.push(unit);
        }
    }
    
    getNewUnit(name) {
        for(let i=0; i<this.pool.length; i++) {
            if(name==this.pool[i].name) {
                return this.pool[i].clone();
            }
        }
        return new Unit();
    }
}