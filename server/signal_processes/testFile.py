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
    rx_flow = lora_RX()

    

    print("Starting Lora TX...")
    tx_flow.start()

    print ("Starting Lora RX...")
    rx_flow.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping flowgraph...")
        tx_flow.stop()
        tx_flow.wait()
        rx_flow.stop()
        rx_flow.wait()

    print(f"Stop time: {t2 - t1} seconds.")







if __name__ == "__main__":
    main()