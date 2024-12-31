data = {
    "link" : {
        "model":"link",
        "hp" : 10,
        "mp" : 4,
        "speed": 4
    },
    "enemy_01" : {
        "model":"enemy_01",
        "hp" : 10,
        "mp" : 4,
        "speed": 4
    },
    "enemy_02" : {
        "model":"enemy_02",
        "hp" : 10,
        "mp" : 4,
        "speed": 4
    },
    "enemy_03" : {
        "model":"enemy_03",
        "hp" : 10,
        "mp" : 4,
        "speed": 4
    },
    "enemy_04" : {
        "model":"enemy_04",
        "hp" : 10,
        "mp" : 4,
        "speed": 4
    }
}

def get_hp(object_name) :
    return data[object_name]['hp']

def get_mp(object_name) :
    return data[object_name]['mp']

def get_speed(object_name) :
    return data[object_name]['speed']

def get_model(object_name) :
    return data[object_name]['model']

