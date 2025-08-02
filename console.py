import time

def print_to_console(message: str):
    """
    Prints a time stamped message to console
    
    Parameters:
    message (str): The message to print
    
    Returns: 
    None
    """
    print(f"[{time.strftime('%X')}] {message}")