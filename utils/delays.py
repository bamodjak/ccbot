import time
import random

def random_delay(min_sec=0.2, max_sec=1.0):
    time.sleep(random.uniform(min_sec, max_sec))
