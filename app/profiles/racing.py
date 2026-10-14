def get_racing_profile():
    return {
        "name": "Racing",
        "mapping": {
            "OPEN_PALM": "w",      # Accelerate
            "FIST": "s",           # Brake / Reverse
            "PALM_LEFT": "a",      # Steer Left
            "PALM_RIGHT": "d",     # Steer Right
            "TWO_FINGERS": "space" # E-Brake / Nitro
        }
    }
