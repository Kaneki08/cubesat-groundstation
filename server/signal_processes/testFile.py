'''
This file was created with the intent of scripting RX/TX switching between respective GNURADIO flowgraphs.

'''

import time
import sys
from lora_TX import lora_TX
from lora_RX import lora_RX



def main():
    # instantiate lora_TX
    tx_flow = lora_TX()

    print("Starting Lora TX...")
    t3 = time.time()
    tx_flow.start()
    t4 = time.time()

    print(f"Start time: {t4 - t3} seconds.")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping flowgraph...")
        t1 = time.time()
        tx_flow.stop()
        tx_flow.wait()
        t2 = time.time()
    
    print(f"Stop time: {t2 - t1} seconds.")







if __name__ == "__main__":
    main()