async def add_row(message_text: str):
    data = message_text.split(',')
    logging.info(f"Parsing message text: {message_text}")
    return data[0], data[1], data[2]
