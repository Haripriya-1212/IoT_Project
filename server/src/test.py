from image_to_speed import image_to_speed

def image_to_byte_string(file_path):
    with open(file_path, "rb") as image_file:
        byte_string = image_file.read()
    return byte_string

speed = image_to_speed(image_to_byte_string('./test.jpeg'))

print(speed)