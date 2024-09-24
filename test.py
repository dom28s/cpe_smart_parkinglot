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

            
        




                           