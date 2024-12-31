data = {
    "link" : {
        "image":"assets/img/link.png",
        "animation_dict" : {
            "work_d": [0, 1],
            "work_u": [2, 3],
            "work_r": [4, 5],
            "work_l": [6, 7],
            "attack_d": [8],
            "attack_u": [9],
            "attack_r": [10],
            "attack_l": [11],
            "win": [12]
        }
    },
    "enemy_01" : {
        "image":"assets/img/enemy_01.png",
        "animation_dict" : {
            "work_d": [0, 1],
            "work_u": [2, 3],
            "work_r": [4, 5],
            "work_l": [6, 7],
            "attack_d": [0],
            "attack_u": [2],
            "attack_r": [4],
            "attack_l": [6]
        }
    },
    "enemy_02" : {
        "image":"assets/img/enemy_02.png",
        "animation_dict" : {
            "work_d": [0, 1],
            "work_u": [2, 3],
            "work_r": [4, 5],
            "work_l": [6, 7],
            "attack_d": [0],
            "attack_u": [2],
            "attack_r": [4],
            "attack_l": [6]
        }
    },
    "enemy_03" : {
        "image":"assets/img/enemy_03.png",
        "animation_dict" : {
            "work_d": [0, 1],
            "work_u": [2, 3],
            "work_r": [4, 5],
            "work_l": [6, 7],
            "attack_d": [0],
            "attack_u": [2],
            "attack_r": [4],
            "attack_l": [6]
        }
    },
    "enemy_04" : {
        "image":"assets/img/enemy_04.png",
        "animation_dict" : {
            "work_d": [0, 1],
            "work_u": [2, 3],
            "work_r": [4, 5],
            "work_l": [6, 7],
            "attack_d": [0],
            "attack_u": [2],
            "attack_r": [4],
            "attack_l": [6]
        }
    }
}


def get_image(model_name) :
    return data[model_name]['image']
    
def get_animation_dict(model_name) :
    return data[model_name]['animation_dict']
