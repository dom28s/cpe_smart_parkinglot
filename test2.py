import time

def print_letters():
    for letter in 'ABCDE':
        print(f'Letter: {letter}')
        time.sleep(1)  # รอ 1.5 วินาที

if __name__ == "__main__":
    print_letters()