import time
import pygame

pygame.init()
pygame.joystick.init()
print("Controllers found:", pygame.joystick.get_count())
if pygame.joystick.get_count() == 0:
    raise SystemExit("No controller detected. Connect it and try again.")

j = pygame.joystick.Joystick(0)
print("Name:", j.get_name())
print("Axes:", j.get_numaxes(), "Buttons:", j.get_numbuttons(), "Hats:", j.get_numhats())
print("Move sticks and press buttons. Ctrl+C to stop.\n")

try:
    while True:
        pygame.event.pump()
        axes = [round(j.get_axis(i), 2) for i in range(j.get_numaxes())]
        pressed = [i for i in range(j.get_numbuttons()) if j.get_button(i)]
        hat = j.get_hat(0) if j.get_numhats() else None
        print(f"axes {axes} buttons {pressed} hat {hat}      ", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    pass