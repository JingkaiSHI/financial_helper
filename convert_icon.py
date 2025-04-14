
import os
import sys

# Path to your ICO file
ico_file = "financial_icon.ico"

# Create iconset folder
os.system("mkdir -p MyIcon.iconset")

# Convert ICO to PNG (using sips)
os.system(f"sips -s format png {ico_file} --out temp_icon.png")

# Generate different sizes
sizes = [16, 32, 128, 256, 512]
for size in sizes:
    os.system(f"sips -z {size} {size} temp_icon.png --out MyIcon.iconset/icon_{size}x{size}.png")
    os.system(f"sips -z {size*2} {size*2} temp_icon.png --out MyIcon.iconset/icon_{size}x{size}@2x.png")

# Create icns file
os.system("iconutil -c icns MyIcon.iconset -o icon.icns")

# Clean up
os.system("rm -rf MyIcon.iconset temp_icon.png")

print("Icon converted successfully: icon.icns")

