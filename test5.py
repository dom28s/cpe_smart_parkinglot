import os

if not os.path.exists('plateSave'):
    with open('plateSave', 'w') as file:
        file.write("dsdsd")
else:
    with open('plateSave', 'a') as file:
        file.write("cross_car")