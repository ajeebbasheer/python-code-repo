import threading

chopstick_a = threading.Lock()
chopstick_b = threading.Lock()
chopstick_c = threading.Lock()

sushi_count = 5000

def philosopher(name, first_chopstick, second_chopstick):
    global sushi_count
    sushi_eaten = 0
    while sushi_count > 0: # eat sushi until it all gone.
        with first_chopstick:
            with second_chopstick:
                if sushi_count > 0:
                    sushi_count -= 1
                    sushi_eaten += 1
                    print(f"{name} took a sushi..{sushi_count} remaining..")
    print(f"{name} eaten {sushi_eaten} sushies..")

if __name__ == "__main__":
    for thread in range(50): #150 people
        threading.Thread(target=philosopher, args=('Barron', chopstick_a, chopstick_b)).start()
        threading.Thread(target=philosopher, args=('Olivia', chopstick_a, chopstick_b)).start()
        threading.Thread(target=philosopher, args=('Steve', chopstick_a, chopstick_b)).start()
