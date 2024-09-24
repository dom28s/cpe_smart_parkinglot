car_track = {
        "is_ajan":[False,True],
        "plate":["A","B"],
        "id":[1,2]
    }
# cls == 2 or cls == 2 or cls == 7


id_inPark =[1,2,3]

for x in car_track["id"]:
    if x in id_inPark:
        sel_id = car_track['id'].index(x)  # หา index ของ id
        if car_track["is_ajan"][sel_id] == True:
            print(car_track["plate"][sel_id])
            print('red')

        if car_track["is_ajan"][sel_id] == False:
            print(car_track["plate"][sel_id])
            print('blue')
while True:
    cls =int(input())
    if id_inPark not in car_track["id"]:
        if cls == 2 or cls == 2 or cls == 7:
            print('blue')
        else:
            print('yellow')

            
        




                            if matching_polygon_index is not None:
                                not_free_space += 1
                                free_space -= 1
                                id_inPark.append(id)

                            print(car_track)
                            if car_track["id"] and car_track["is_ajan"] and car_track["id"] is not None and car_track["is_ajan"] is not None:
                                print(car_track['id'])
                                print(car_track['is_ajan'])
                                for x in car_track["id"]:
                                    if x in id_inPark:
                                        k = car_track['id'].index(x)  # หา index ของ id

                                        if k < len(car_track["is_ajan"]):  # ตรวจสอบว่า index ไม่เกินขอบเขต
                                            if car_track["is_ajan"][k] == True:
                                                car_color = red

                                            if car_track["is_ajan"][k] == False:
                                                car_color = blue

                            if id_inPark not in car_track["id"]:  # ตรวจสอบว่ามี id_inPark ใน car_track หรือไม่
                                if cls == 2 or cls == 2 or cls == 7:
                                    car_color = blue
                                else:
                                    car_color = yellow