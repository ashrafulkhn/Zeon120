import logging
import time
from typing import Optional
from can import Message

from power_120kw.factory_reader import FactoryReader
from caninterface import CanInterface
from power_120kw.persistent_communication import set_status_update
from exceptions import ConfigException

logger = logging.getLogger(__name__)

def read_all_can_data(message: Message) -> None:
    """
    Process CAN message data using appropriate reader.
    
    Args:
        message: CAN message to process
    """
    try:
        reader = FactoryReader.create_reader(message.arbitration_id, message.data)
        if reader:
            reader.read_input_data()
    except Exception as e:
        logger.error(f"Error processing CAN message: {e}")
        raise

def read_from_can(timeout: float = 1.0) -> None:
    """
    Read messages from CAN bus with timeout.
    
    Args:
        timeout: Maximum time to wait for messages in seconds
    """
    bus = CanInterface.bus_instance
    if not bus:
        raise ConfigException("CAN bus not initialized")
    
    start_time = time.time()
    messages_processed = 0
    
    try:
        while time.time() - start_time < timeout:
            message = bus.recv(timeout=0.1)
            if message:
                read_all_can_data(message)
                messages_processed += 1
            
        logger.debug(f"Processed {messages_processed} CAN messages in {time.time() - start_time:.2f} seconds")
    except Exception as e:
        logger.error(f"Error reading from CAN bus: {e}")
        raise

def perform_action() -> None:
    """
    Main action function for dynamic power sharing.
    
    Raises:
        ConfigException: If configuration is invalid
        Exception: For other unexpected errors
    """
    try:
        logger.info("Starting dynamic power sharing action")
        set_status_update()
        read_from_can()
        logger.info("Dynamic power sharing action completed successfully")
    except Exception as e:
        logger.error(f"Failed to perform dynamic sharing action: {e}")
        raise