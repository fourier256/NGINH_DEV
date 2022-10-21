class TileMap {
    constructor(tilemap_data, sprite_pool) {
        this.w = tilemap_data.w;
        this.h = tilemap_data.h;
        this.matrix_raw = tilemap_data.matrix.slice();
        this.matrix = [];
        this.tile = [];
        this.sprite_map = [];
        for(let i=0; i<tilemap_data.num_tile; i++) {
            this.tile.push(i);
            this.sprite_map.push(i-1);
        }
        this.sprite_map[0] = 0;
        this.sprite = sprite_pool.getNewSprite(tilemap_data.sprite);
        
        for(let iLayer=0; iLayer<4; iLayer++) {
            this.matrix.push([]);
            for(let iTile=0; iTile<this.tile.length; iTile++) {
                this.matrix[iLayer].push(Array.from(Array(this.h), ()=>Array(this.w).fill(0)));
            }
        }
        
        for(let iLayer=0; iLayer<4; iLayer++) {
            for(let iTile=0; iTile<this.tile.length; iTile++) {
                for(let iX=0; iX<this.w; iX++) {
                    for(let iY=0; iY<this.h; iY++) {
                        let chip = new Arary(4);
                        let raw_x = iX*2;
                        let raw_y = iY*2;
                        let raw_w = this.w*2;
                        chip[0] = ((raw_y+1)*raw_w)+(raw_x+1);
                        chip[1] = ((raw_y+1)*raw_w)+(raw_x+0);
                        chip[2] = ((raw_y+0)*raw_w)+(raw_x+1);
                        chip[3] = ((raw_y+0)*raw_w)+(raw_x+0);
                        
                        for(let iChip=0; iChip<4; iCHip++) {
                            if(matrix_raw[iLayer-1][chip[iChip]]==iTile) {
                                this.matrix[iLayer][iTile][iX][iY] += Math.pow(2, iChip);
                            }
                        }
                    }
                }
            }
        }
    }
    
    setMatrix(layer, x, y, tile) {
        setMatrixRaw(layer, (x+0), (y+0), tile);
        setMatrixRaw(layer, (x+1), (y+0), tile);
        setMatrixRaw(layer, (x+0), (y+1), tile);
        setMatrixRaw(layer, (x+1), (y+1), tile);
        for(let iLayer=0; iLayer<4; iLayer++) {
            for(let iTile=0; iTile<this.tile.length; iTile++) {
                for(let iX=0; iX<this.w; iX++) {
                    for(let iY=0; iY<this.h; iY++) {
                        let chip = new Arary(4);
                        let raw_x = iX*2;
                        let raw_y = iY*2;
                        let raw_w = this.w*2;
                        chip[0] = ((raw_y+1)*raw_w)+(raw_x+1);
                        chip[1] = ((raw_y+1)*raw_w)+(raw_x+0);
                        chip[2] = ((raw_y+0)*raw_w)+(raw_x+1);
                        chip[3] = ((raw_y+0)*raw_w)+(raw_x+0);
                        
                        for(let iChip=0; iChip<4; iCHip++) {
                            if(matrix_raw[iLayer-1][chip[iChip]]==iTile) {
                                this.matrix[iLayer][iTile][iX][iY] += Math.pow(2, iChip);
                            }
                        }
                    }
                }
            }
        }
    }
    
    setMatrixRaw(layer, x_raw, y_raw, tile) {
    	let w_raw = this.w*2;
        let h_raw = this.h*2;
        if(0 <= x_raw && x_raw < w_raw) {
            if(0 <= y_raw && y_raw < h_raw) {
                this.matrix_raw[layer][y_raw*w_raw + x_raw] = tile;
            }
        }
    }
    
    drawTilemap(paint) {
        for(let iLayer=1; iLayer<4; iLayer++) {
            for(let iTile=0; iTile<this.tile.length; iTile++) {
                for(let iX=0; iX<this.w; iX++) {
                    for(let iY=0; iY<this.h; iY++) {
                        this.sprite.drawSpriteFrame(paint, (16*this.sprite_map[iTile])+this.matrix[iLayer][iTile][iX][iY], iX*32, (iY-iLayer+1)*32);
                    }
                }
            }
        }
    }
}