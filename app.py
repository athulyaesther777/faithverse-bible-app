def generate_verse_image(text, title="FaithVerse"):
    img = Image.new("RGB", (1080, 1080), color=(30, 40, 60))
    draw = ImageDraw.Draw(img)

    # FORCE real font from project
    try:
        font_big = ImageFont.truetype("fonts/PlayfairDisplay-Bold.ttf", 58)
        font_small = ImageFont.truetype("fonts/PlayfairDisplay-Bold.ttf", 26)
    except Exception as e:
        st.error(f"Font load error: {e}")
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    max_width = 900
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font_big)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.strip())

    # Title
    draw.text((60, 50), title, fill="#CCCCCC", font=font_small)

    # Center verse vertically
    total_height = len(lines) * 80
    start_y = (1080 - total_height) // 2

    for i, line in enumerate(lines[:8]):
        bbox = draw.textbbox((0, 0), line, font=font_big)
        text_width = bbox[2] - bbox[0]
        x = (1080 - text_width) // 2
        y = start_y + i * 80

        draw.text((x, y), line, fill="white", font=font_big)

    # Footer
    draw.text((60, 1020), "© FaithVerse", fill="#AAAAAA", font=font_small)

    return img

