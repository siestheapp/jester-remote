from PIL import Image

# Change the filename below to your screenshot PNG path if needed
filename = "Screenshot 2025-05-19 at 10.58.10 PM.png"

try:
    img = Image.open(filename)
    img.show()
    print("Pillow successfully opened the PNG file.")
except Exception as e:
    print(f"Pillow failed to open the PNG file: {e}") 