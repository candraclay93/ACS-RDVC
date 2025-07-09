import can
import threading
import time
from random import randint

# Shared flag for thread control
running = True

def can_receiver(filter_ids=[0x70]):
    """Thread function to receive CAN messages with optional filtering"""
    with can.interface.Bus(channel='vcan0', bustype='socketcan') as bus:
        while running:
            message = bus.recv(timeout=1.0)
            
            if message is not None:
                if filter_ids is None or message.arbitration_id in filter_ids:
                    print(f"\nReceived: ID {hex(message.arbitration_id)}, Data: {message.data}")

def can_transmitter(specific_ids):
    """Thread function to transmit to specific CAN IDs"""
    with can.interface.Bus(channel='vcan0', bustype='socketcan') as bus:
        while running:
            for can_id in specific_ids:
                # Generate some random data (8 bytes)
                data = [randint(0, 255) for _ in range(8)]
                
                msg = can.Message(
                    arbitration_id=can_id,
                    data=data,
                    is_extended_id=False
                )
                
                try:
                    bus.send(msg)
                    print(f"Sent to {hex(can_id)}: {data}", end='\r')  # Overwrite line
                except can.CanError:
                    print(f"Failed to send to {hex(can_id)}")
                
                # Small delay between messages
                time.sleep(0.1)
            
            # Delay between full cycles
            time.sleep(0.5)

if __name__ == "__main__":
    # Specific CAN IDs we want to transmit to
    target_ids = [0x100, 0x101, 0x102, 0x103]
    
    try:
        # Create and start threads
        receiver_thread = threading.Thread(target=can_receiver)
        transmitter_thread = threading.Thread(target=can_transmitter, args=(target_ids,))
        
        receiver_thread.start()
        transmitter_thread.start()
        
        # Wait for threads (they'll run until KeyboardInterrupt)
        receiver_thread.join()
        transmitter_thread.join()
        
    except KeyboardInterrupt:
        print("\nStopping threads...")
        running = False
        receiver_thread.join()
        transmitter_thread.join()
        print("Stopped cleanly")