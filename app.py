import streamlit as st
import pandas as pd
import random
import os
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="FaithVerse – Bible & Study App", layout="wide")

# =========================
# IMAGE GENERATOR
# =========================
def generate_verse_image(text, title="FaithVerse"):
    img = Image.new("RGB", (900, 500), color=(44, 62, 80))
    draw = ImageDraw.Draw(img)

    FONT_PATH = "fonts/Montserrat-Italic-VariableFont_wght.ttf"

try:
    font_big = ImageFont.truetype(FONT_PATH, 64)
    font_small = ImageFont.truetype(FONT_PATH, 36)
except Exception as e:
    st.error(f"Font load failed: {e}")
    font_big = ImageFont.load_default()
    font_small = ImageFont.load_default()


    words = text.split()
    lines, line = [], ""
    for word in words:
        if len(line + word) < 40:
            line += word + " "
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)

    y = 120
    for l in lines[:8]:
        draw.text((50, y), l.strip(), fill="white", font=font_big)
        y += 45

    draw.text((50, 30), title, fill="lightgray", font=font_small)
    draw.text((50, 460), "© FaithVerse", fill="lightgray", font=font_small)
    return img

# =========================
# BIBLE BOOK ORDER
# =========================
BIBLE_BOOK_ORDER = [
    "Genesis","Exodus","Leviticus","Numbers","Deuteronomy",
    "Joshua","Judges","Ruth","1 Samuel","2 Samuel","1 Kings","2 Kings",
    "1 Chronicles","2 Chronicles","Ezra","Nehemiah","Esther","Job","Psalms",
    "Proverbs","Ecclesiastes","Song of Solomon","Isaiah","Jeremiah",
    "Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah","Jonah",
    "Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi",
    "Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians",
    "Galatians","Ephesians","Philippians","Colossians","1 Thessalonians",
    "2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon","Hebrews",
    "James","1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"
]

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_bible():
    df = pd.read_csv("data/bible_data_set.csv")
    df.columns = [c.strip().lower() for c in df.columns]
    return df

@st.cache_data
def load_naves():
    return pd.read_csv("data/NavesTopicalDictionary.csv")

@st.cache_data
def load_relationships():
    return pd.read_csv("data/BibleData-PersonRelationship.csv")

@st.cache_data
def load_events():
    return pd.read_csv("data/BibleData-Event.csv")

bible_df = load_bible()
naves_df = load_naves()
rel_df = load_relationships()
events_df = load_events()

# =========================
# SIDEBAR NAVIGATION
# =========================
st.sidebar.title("✝️ FaithVerse")
page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Home", 
        "📖 Read Bible", 
        "👤 People Explorer", 
        "🔎 Bible Search", 
        "🎵 Worship Songs",
        "🙏 Prayer Wall",
        "📊 Prayer Analytics"
    ]
)

# =========================
# HOME
# =========================
if page == "🏠 Home":
    st.title("🙏 God Is With You")
    st.info("✨ *'The Lord himself goes before you and will be with you.' — Deuteronomy 31:8*")

    moods = {
        "Happy 😊": ["joy", "rejoice", "glad"],
        "Sad 😔": ["comfort", "heal", "broken"],
        "Anxious 😰": ["fear", "peace", "anxious"],
        "Angry 😡": ["anger", "forgive", "peace"],
        "Calm 😌": ["rest", "peace", "still"],
        "Down 😞": ["hope", "strength", "renew"]
    }

    selected_mood = st.selectbox("Select your mood", list(moods.keys()))
    keywords = moods[selected_mood]

    mood_matches = bible_df[
        bible_df["text"].str.contains("|".join(keywords), case=False, na=False)
    ]

    sample = mood_matches.sample(min(5, len(mood_matches))) if not mood_matches.empty else bible_df.sample(5)

    st.markdown("### 📜 Verses for You")
    for _, row in sample.iterrows():
        st.success(f"**{row['book']} {row['chapter']}:{row['verse']}** — {row['text']}")

    st.markdown("### 🖼️ Generate Verse Image")
    if st.button("Generate Image for First Verse"):
        first = sample.iloc[0]
        verse_text = f"{first['book']} {first['chapter']}:{first['verse']} - {first['text']}"
        img = generate_verse_image(verse_text)
        st.image(img)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("⬇️ Download Verse Image", buf.getvalue(), "faithverse_verse.png", "image/png")

# =========================
# READ BIBLE
# =========================
elif page == "📖 Read Bible":
    st.title("📖 Read the Holy Bible")
    available_books = [b for b in BIBLE_BOOK_ORDER if b in bible_df["book"].unique()]

    book = st.selectbox("Select Book", available_books)
    chapter = st.selectbox("Select Chapter", sorted(bible_df[bible_df["book"] == book]["chapter"].unique()))

    chapter_df = bible_df[(bible_df["book"] == book) & (bible_df["chapter"] == chapter)].sort_values("verse")
    for _, row in chapter_df.iterrows():
        st.markdown(f"**{int(row['verse'])}.** {row['text']}")

# =========================
# PEOPLE EXPLORER
# =========================
elif page == "👤 People Explorer":
    st.title("👤 Bible People Explorer")
    person_name = st.text_input("Search Bible Person")

    if person_name:
        matches = naves_df[naves_df["subject"].astype(str).str.contains(person_name, case=False, na=False)]
        for _, row in matches.iterrows():
            st.subheader(row["subject"])
            for l in row["entry"].split("\n")[:8]:
                st.write(f"• {l.strip()}")

        rel_text = rel_df.astype(str).agg(" ".join, axis=1)
        st.dataframe(rel_df[rel_text.str.contains(person_name, case=False, na=False)].head(10))

        event_text = events_df.astype(str).agg(" ".join, axis=1)
        st.dataframe(events_df[event_text.str.contains(person_name, case=False, na=False)].head(10))

# =========================
# BIBLE SEARCH
# =========================
elif page == "🔎 Bible Search":
    st.title("🔎 Search the Bible")
    query = st.text_input("Search word or phrase")

    if query:
        results = bible_df[bible_df["text"].str.contains(query, case=False, na=False)]
        for _, row in results.head(20).iterrows():
            st.write(f"📖 **{row['book']} {row['chapter']}:{row['verse']}** — {row['text']}")

# =========================
# WORSHIP SONGS
# =========================
elif page == "🎵 Worship Songs":
    st.title("🎵 Worship Songs — Athulya Esther")
    song_file = "data/athulya_original_worship.txt"

    if os.path.exists(song_file):
        songs_text = open(song_file, "r", encoding="utf-8").read()
        songs = songs_text.split("\n---\n")
        titles = [s.split("\n")[0] for s in songs]

        selected_song = st.selectbox("Select a Song", titles)

        for song in songs:
            if song.startswith(selected_song):
                st.text(song)

                st.markdown("### 🖼️ Generate Worship Image")
                if st.button("Generate Worship Image"):
                    preview = song.split("\n")[1]
                    img = generate_verse_image(preview, title="Worship by Athulya Esther")
                    st.image(img)
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button("⬇️ Download Worship Image", buf.getvalue(), "worship_image.png", "image/png")
                break

# =========================
# PRAYER WALL
# =========================
elif page == "🙏 Prayer Wall":
    st.title("🙏 Prayer Wall (Anonymous & Faith-Based)")
    prayer_file = "data/prayers.csv"

    # Ensure folder exists
    os.makedirs("data", exist_ok=True)

    # Ensure file exists and is valid
    if not os.path.exists(prayer_file):
        pd.DataFrame(
            columns=["name","prayer","status","testimony","date"]
        ).to_csv(prayer_file, index=False)

    # Safe load with fallback
    try:
        prayers_df = pd.read_csv(prayer_file)
    except Exception:
        st.warning("⚠️ Prayer file was corrupted. Resetting prayer wall safely.")
        prayers_df = pd.DataFrame(
            columns=["name","prayer","status","testimony","date"]
        )
        prayers_df.to_csv(prayer_file, index=False)

    # =========================
    # SUBMIT PRAYER
    # =========================
    st.markdown("## 📝 Submit a Prayer")
    name = st.text_input("Name (optional or Anonymous)")
    prayer_text = st.text_area("Your Prayer Request")

    if st.button("🙏 Submit Prayer"):
        if prayer_text.strip():
            new_row = {
                "name": name if name else "Anonymous",
                "prayer": prayer_text,
                "status": "Waiting on God",
                "testimony": "",
                "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
            }
            prayers_df = pd.concat(
                [prayers_df, pd.DataFrame([new_row])],
                ignore_index=True
            )
            prayers_df.to_csv(prayer_file, index=False)
            st.success("🤍 Your prayer has been shared. The community is praying with you.")
        else:
            st.error("Please enter a prayer request.")

    # =========================
    # WAITING ON GOD
    # =========================
    st.markdown("## 🕊️ Waiting on God")
    waiting = prayers_df[prayers_df["status"] == "Waiting on God"]

    if waiting.empty:
        st.info("No prayers yet. Be the first to submit 🙏")
    else:
        for _, row in waiting.iterrows():
            st.info(f"🙏 **{row['name']}** — {row['prayer']}")
            st.caption(f"📅 {row['date']}")

    # =========================
    # GOD'S PLAN IS DIFFERENT
    # =========================
    st.markdown("## 🌱 God’s Plan is Different")
    different = prayers_df[prayers_df["status"] == "God’s Plan is Different"]

    if different.empty:
        st.caption("None yet. Trusting God’s wisdom 🤍")
    else:
        for _, row in different.iterrows():
            st.warning(f"🌱 **{row['name']}** — {row['prayer']}")
            st.caption(f"📅 {row['date']}")

    # =========================
    # PRAISE REPORTS
    # =========================
    st.markdown("## 🌟 Praise Reports (Answered)")
    answered = prayers_df[prayers_df["status"] == "Answered – Praise"]

    if answered.empty:
        st.caption("No praise reports yet. We believe they are coming 🙏")
    else:
        for _, row in answered.iterrows():
            st.success(f"🌟 **{row['name']}** — {row['testimony']}")
            st.caption("Original Prayer:")
            st.write(row["prayer"])
            st.caption(f"📅 {row['date']}")


# =========================
# PRAYER ANALYTICS
# =========================
elif page == "📊 Prayer Analytics":
    st.title("📊 Prayer Analytics (Ministry View)")
    prayer_file = "data/prayers.csv"

    if not os.path.exists(prayer_file):
        st.warning("No prayer data yet.")
    else:
        try:
            prayers_df = pd.read_csv(prayer_file)
        except Exception:
            st.error("Prayer data is corrupted. No analytics available.")
            st.stop()

        st.metric("Total Prayers", len(prayers_df))
        st.metric("Waiting on God", (prayers_df["status"] == "Waiting on God").sum())
        st.metric("God’s Plan Different", (prayers_df["status"] == "God’s Plan is Different").sum())
        st.metric("Answered (Praise)", (prayers_df["status"] == "Answered – Praise").sum())

        if "date" in prayers_df.columns:
            prayers_df["date_only"] = pd.to_datetime(
                prayers_df["date"], errors="coerce"
            ).dt.date

            trend = prayers_df.groupby("date_only").size()
            st.line_chart(trend)


# =========================
# FOOTER
# =========================
st.markdown("""
---
📚 Bible datasets by **Brady Stephenson (Kaggle)**  
License: CC BY-NC-SA 3.0 — Non-Commercial  

🎵 Original Worship Songs © Athulya Esther  
🙏 FaithVerse Ministry App
""")
