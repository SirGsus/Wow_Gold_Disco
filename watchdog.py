"""Watchdog to do something against the bot facing in the wrong direction and getting killed"""
import cv2
import window_grabber


def check_combat(window_name):
    """Checks if the player is currently within combat and takes actions if needed"""
    game_window = window_grabber.GameCapture(window_name)
    in_combat = False
    game_window_detected = True

    while True:
        frame = game_window.grab_screen(shift_x=336.5, shift_y=226.5, activation_range_x=10, activation_range_y=6)
        loc = window_grabber.match_template(frame, cv2.imread('templates/non_combat.png', 1))

        if loc == (0, 2) and in_combat == False:
            in_combat = True
            game_window_detected = True
            print("Player in combat.")

        elif loc == (1, 1) and in_combat == True:
            in_combat = False
            game_window_detected = True
            print("End of combat.")

        elif loc == (0, 0) and game_window_detected == True:
            game_window_detected = False
            print("Game window not active!")



window_name = 'World of Warcraft'
check_combat(window_name)