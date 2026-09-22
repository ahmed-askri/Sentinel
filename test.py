from PIL import Image, ImageDraw, ImageFont

# 1. Create a new image with a background color matching your original image
background_color = (244, 246, 250) # Approximate hex #F4F6FA
img = Image.new('RGB', (120, 50), color=background_color)

# 2. Initialize ImageDraw
draw = ImageDraw.Draw(img)

# 3. Load a serif font (adjust path to a font file on your system if necessary)
# Example for Windows: "times.ttf" or "georgia.ttf"
try:
    font = ImageFont.truetype("times.ttf", 40)
except IOError:
    font = ImageFont.load_default()

# 4. Add the new text
text_color = (30, 30, 30) # Dark gray/black
draw.text((10, 5), "52", fill=text_color, font=font)

# 5. Save the output
img.save('image_13_42.png')
print("Image saved as image_13_42.png")