import streamlit as st
import random
import base64
from mutagen import File
import streamlit.components.v1 as components
from mutagen.mp4 import MP4

st.set_page_config(
    page_title="Feelify - Playlist",
    page_icon="Feelify .png",
    layout="wide"
)

# First, update the get_song_duration function to handle m4a files better
def get_song_duration(file_path):
    try:
        audio = File(file_path)
        if hasattr(audio.info, 'length'):
            duration = int(audio.info.length)
        else:
            # For m4a files
            from mutagen.mp4 import MP4
            audio = MP4(file_path)
            duration = int(audio.info.length)
        minutes, seconds = divmod(duration, 60)
        return f"{minutes:02d}:{seconds:02d}"
    except Exception as e:
        return "--:--"

# Initialize session state
for key, default in {
    "liked_songs": [],
    "selected_song": 0,
    "shuffle": False,
    "repeat": False,
    "last_action": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Emotion from query params
emotion_options = ["happy", "sad", "angry", "calm"]
emotion = st.query_params.get("emotion", ["happy"])[0]
if emotion not in emotion_options:
    emotion = "happy"

# --- CSS Styling ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #b3c8cf, #f1f0e8);
    font-family: 'Poppins', sans-serif;
}
.sidebar-title {
    font-size: 26px;
    font-weight: bold;
    color: #89a8b2;
}
.song-button {
    background: #f1f0e8;
    border: 2px solid #b3c8cf;
    color: #000;
    font-size: 20px;
    padding: 14px;
    border-radius: 12px;
    transition: all 0.4s ease;
}
.song-button:hover {
    background: #b3c8cf;
    color: #fff;
    transform: scale(1.05);
}
.control-button {
    background-color: #111827;
    border: none;
    border-radius: 50%;  /* Changed to 50% for circular shape */
    width: 45px;         /* Added fixed width */
    height: 45px;        /* Added fixed height */
    padding: 10px;
    transition: all 0.3s ease-in-out;
    display: flex;
    justify-content: center;
    align-items: center;
}

.control-button:hover {
    box-shadow: 0 0 12px #3b82f6;
    transform: scale(1.2);  /* Increased zoom effect */
    cursor: pointer;
}

.now-playing {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 20px;
    padding: 15px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
}
div[data-testid="stForm"] button {
    background-color: rgba(179, 200, 207, 0.2);
    color: #333;
    padding: 2px 7px;
    margin: -7px 0;
    border-radius: 0;
    font-size: 0.9rem;
    position: relative;
    transition: all 0.3s ease;
    border: none !important;  /* Force remove border */
    outline: none !important; /* Remove outline */
    box-shadow: none !important; /* Remove any shadow */
}

div[data-testid="stForm"] {
    margin: -3px 0;
    padding: 0;
    border: none !important;
    outline: none !important;
}

/* Remove any default Streamlit form styles */
div.stForm > div {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}
div[data-testid="stForm"] button::after {
    right: 8px;
    font-size: 0.85em;
    line-height: 1;      /* Matched line height */
}
div[data-testid="stForm"] button:hover {
    background: rgba(179, 200, 207, 0.5);
    transform: translateX(5px);
}

div[data-testid="stForm"] {
    margin: 0;          /* Remove form margin */
    padding: 0;         /* Remove form padding */
}
}
</style>
""", unsafe_allow_html=True)

# ------------------ Header ------------------
col1, col2 = st.columns([1, 5])
with col1:
    st.image("Feelify .png", width=80)
with col2:
    st.title("🎵 Feelify")
    st.caption("An emotion-based music experience")

# Define Playlists
# Define base GitHub raw URL
BASE_URL = "https://raw.githubusercontent.com/NehaDesai1704/Feelify/main/Music%20web/songs"

playlists = {
    "happy": [
        {"name": "Ishq Hai", "file": f"{BASE_URL}/happy/Ishq-Hai-Official-Music-Video-Mismatched-Season-3-A-Netflix-.m4a"},
        {"name": "Abhi To Party Shuru Hui Hai", "file": f"{BASE_URL}/happy/Abhi-Toh-Party-Shuru-Hui-Hai-FULL-VIDEO-Song-Khoobsurat-Bads.m4a"},
        {"name": "Tum Tak", "file": f"{BASE_URL}/happy/A-R-Rahman-Tum-Tak-Best-Lyric-Video-Raanjhanaa-Sonam-Kapoor-.m4a"},
        {"name": "Gallan Godiyaan", "file": f"{BASE_URL}/happy/Gallan-Goodiyaan-Full-VIDEO-Song-Dil-Dhadakne-Do-T-Series.m4a"},
        {"name": "Morni Banke", "file": f"{BASE_URL}/happy/Guru-Randhawa-Morni-Banke-Video-Badhaai-Ho-Tanishk-Bagchi-Ne.m4a"},
        {"name": "Kala Chashma", "file": f"{BASE_URL}/happy/Kala-Chashma-Baar-Baar-Dekho-Sidharth-M-Katrina-K-Prem-Harde.m4a"},
        {"name": "Kar Gayi Chull", "file": f"{BASE_URL}/happy/Kar-Gayi-Chull-Kapoor-Sons-Sidharth-Malhotra-Alia-Bhatt-Bads.m4a"},
        {"name": "Jenne Laga Hoon", "file": f"{BASE_URL}/happy/Jeene-Laga-Hoon-Lyrical-Ramaiya-Vastavaiya-Girish-Kumar-Shru.m4a"},
        {"name": "Lae Dooba", "file": f"{BASE_URL}/happy/Lae-Dooba-Full-Video-Aiyaary-Sidharth-Malhotra-Rakul-Preet-S.m4a"},
        {"name": "Laung Da Lashkara", "file": f"{BASE_URL}/happy/Laung-Da-Lashkara-Official-full-song-Patiala-House-Feat-Aksh.m4a"},
        {"name": "Love You Zindagi", "file": f"{BASE_URL}/happy/Love-You-Zindagi-Full-Video-Dear-Zindagi-Alia-Bhatt-Shah-Ruk.m4a"},
        {"name": "Main Rang Sharbato Ka", "file": f"{BASE_URL}/happy/Main-Rang-Sharbaton-Ka-Phata-Poster-Nikhla-Hero-I-Shahid-Ile.m4a"},
        {"name": "Nashe Si Chad Gai", "file": f"{BASE_URL}/happy/Nashe-Si-Chadh-Gayi-Song-Befikre-Ranveer-Singh-Vaani-Kapoor-.m4a"},
        {"name": "Nazm Nazm", "file": f"{BASE_URL}/happy/Nazm-Nazm-Lyrical-Bareilly-Ki-Barfi-Kriti-Sanon-Ayushmann-Kh.m4a"},
        {"name": "Manwa Lage", "file": f"{BASE_URL}/happy/OFFICIAL-Manwa-Laage-FULL-VIDEO-Song-Happy-New-Year-Shah-Ruk.m4a"},
        {"name": "Londan Thumakada", "file": f"{BASE_URL}/happy/Queen-London-Thumakda-Full-Video-Song-Kangana-Ranaut-Raj-Kum.m4a"},
        {"name": "Rang Jo Lagyo", "file": f"{BASE_URL}/happy/Rang-Jo-Lagyo-Ramaiya-Vastavaiya-Girish-Kumar-Shruti-Haasan-.m4a"},
        {"name": "Saibo", "file": f"{BASE_URL}/happy/Saibo-Lyrics-Sachin-Jigar-Shreya-Ghosha-Tochi-Raina.m4a"},
        {"name": "Tu Jaane Na", "file": f"{BASE_URL}/happy/Tu-Jaane-Na-Atif-Aslam-Lyrics-Lyrical-Bam-Hindi.m4a"},
        {"name": "Ude Dil Befikre", "file": f"{BASE_URL}/happy/Ude-Dil-Befikre-Full-Song-Befikre-Ranveer-Singh-Vaani-Benny-.m4a"}
    ],
    "sad": [
        {"name": "Agar Tum Sath ho", "file": f"{BASE_URL}/sad/AGAR-TUM-SAATH-HO-Full-4k-song-Tamasha-Ranbir-Kapoor-Deepika.m4a"},
        {"name": "Ae Dil Hai Mushkil", "file": f"{BASE_URL}/sad/Arijit-Singh-Ae-Dil-Hai-Mushkil-Title-Track-Lyrical-Video-Ra.m4a"},
        {"name": "Baatein Ye Kabhi Na", "file": f"{BASE_URL}/sad/Baatein-Ye-Kabhi-Na-Lyrical-Song-Khamoshiyan-Ali-Fazal-Sapna.m4a"},
        {"name": "Bewajah", "file": f"{BASE_URL}/sad/Bewajah-Lyrical-Video-Sanam-Teri-Kasam-Harshvardhan-Mawra-Hi.m4a"},
        {"name": "Bulleya", "file": f"{BASE_URL}/sad/Bulleya-Lyrics-Sultan-Salman-Anushka-Vishal-Shekhar-Irshad-K.m4a"},
        {"name": "Channa Mereya", "file": f"{BASE_URL}/sad/Channa-Mereya-Lyric-Video-Ae-Dil-Hai-Mushkil-Karan-Johar-Ran.m4a"},
        {"name": "Raanjhan", "file": f"{BASE_URL}/sad/Do-Patti-Raanjhan-Full-Video-Kriti-Sanon-Shaheer-Sheikh-Para.m4a"},
        {"name": "Hamari Adhuri Kahani", "file": f"{BASE_URL}/sad/Hamari-Adhuri-Kahani-Lyrical-Song-Arjit-Singh-Emraan-Hashmi-.m4a"},
        {"name": "Humdard", "file": f"{BASE_URL}/sad/Humdard-Arijit-Singh-Ek-villain-Jo-Tu-Mera-Humdard-Hai.m4a"},
        {"name": "Kaun Tujhe", "file": f"{BASE_URL}/sad/KAUN-TUJHE-Lyrical-M-S-DHONI-THE-UNTOLD-STORY-Amaal-Mallik-P.m4a"},
        {"name": "Lo Maaan Liya", "file": f"{BASE_URL}/sad/Lo-maan-liya-lyrics-Arijith-shing-lo-maan-liya-humne-song-ly.m4a"},
        {"name": "Meray Pass Tum Ho", "file": f"{BASE_URL}/sad/Meray-Paas-Tum-Ho-OST-Rahat-Fateh-Ali-Khan-Humayun-Saeed-Aye.m4a"},
        {"name": "Phir Bhi Tumko Chaahunga", "file": f"{BASE_URL}/sad/Phir-Bhi-Tumko-Chaahunga-Full-Song-Arijit-Singh-Arjun-K-Shra.m4a"},
        {"name": "Sanam Teri Kasam", "file": f"{BASE_URL}/sad/Sanam-Teri-Kasam-Lyrical-Video-Harshvardhan-Mawra-Ankit-Tiwa.m4a"},
        {"name": "Tabah Ho Gaye", "file": f"{BASE_URL}/sad/Tabah-Ho-Gaye-Lyrics-by-Shreya-Ghoshal.m4a"},
        {"name": "Sun Saaiyan", "file": f"{BASE_URL}/sad/Teri-Aarju-Na-Mita-Sake-Qurban-Masroor-Fateh-Ali-Khan-sunsai.m4a"},
        {"name": "Tu Hi Ho", "file": f"{BASE_URL}/sad/tum-hi-ho-song-lyrics.m4a"},
        {"name": "Banjaara", "file": f"{BASE_URL}/sad/Banjaara-Full-Video-Song-Ek-Villain-Shraddha-Kapoor-Siddhart.m4a"},
        {"name": "Kalank", "file": f"{BASE_URL}/sad/Kalank-Title-Track-Lyrical-Alia-Bhatt-Varun-Dhawan-Arijit-Si.m4a"},
        {"name": "Saaiyaan", "file": f"{BASE_URL}/sad/Saaiyaan-Lyrical-Kareen-Kapoor-Rahat-Fateh-Ali-Khan-Salim-Su.m4a"}
    ],
    "angry": [
        {"name": "Bolo Har Har Har", "file": f"{BASE_URL}/angry/BOLO-HAR-HAR-HAR-Video-Song-SHIVAAY-Title-Song-Ajay-Devgn-Mi.m4a"},
        {"name": "Brothers Anthem", "file": f"{BASE_URL}/angry/Brothers-Anthem-Lyric-Video-Brothers-Akshay-Kumar-Sidharth-M.m4a"},
        {"name": "Chal Utth Bandeya", "file": f"{BASE_URL}/angry/Chal-Utth-Bandeya-Full-Song-with-Lyrics-DO-LAFZON-KI-KAHANI-.m4a"},
        {"name": "Dangal", "file": f"{BASE_URL}/angry/Dangal-Title-Track-Lyrical-Video-Dangal-Aamir-Khan-Pritam-Am.m4a"},
        {"name": "Dhaakad", "file": f"{BASE_URL}/angry/Dhaakad-Dangal-Aamir-Khan-Pritam-Amitabh-Bhattacharya-Raftaa.m4a"},
        {"name": "Chak Lein De", "file": f"{BASE_URL}/angry/Full-Video-Chak-Lein-De-Chandni-Chowk-To-China-Akshay-Kumar-.m4a"},
        {"name": "Get Ready To Fight", "file": f"{BASE_URL}/angry/GET-READY-TO-FIGHT.m4a"},
        {"name": "Ganpat", "file": f"{BASE_URL}/angry/Ganpat-Full-Song-Shoot-Out-At-Lokhandwala.m4a"},
        {"name": "Ghamand Kar", "file": f"{BASE_URL}/angry/Ghamand-Kar-Song-Tanhaji-The-Unsung-Warrior-Ajay-Kajol-Saif-.m4a"},
        {"name": "Jee Karda", "file": f"{BASE_URL}/angry/Jee-Karda-Official-Full-Song-Badlapur-Varun-Dhawan-Yami-Gaut.m4a"},
        {"name": "Mila Toh Marega", "file": f"{BASE_URL}/angry/MILA-TOH-MAREGA.m4a"},
        {"name": "Mera Intkam Dekhegi", "file": f"{BASE_URL}/angry/Mera-Intkam-Dekhegi-Shaadi-Mein-Zaroor-Aana-Rajkummar-R-Krit.m4a"},
        {"name": "Aarambh", "file": f"{BASE_URL}/angry/Piyush-Mishra-Aarambh-Lyrical-Video-Song-Gulaal-K-K-Menon-Ab.m4a"},
        {"name": "Sadda Haq", "file": f"{BASE_URL}/angry/Sadda-Haq-Full-Video-Song-Rockstar-Ranbir-Kapoor.m4a"},
        {"name": "Kar Har Maidan Fateh", "file": f"{BASE_URL}/angry/Sanju-KAR-HAR-MAIDAAN-FATEH-Full-Video-Song-Ranbir-Kapoor-Ra.m4a"},
        {"name": "Soorma Anthem", "file": f"{BASE_URL}/angry/Soorma-Anthem-Full-Video-Soorma-Diljit-Taapsee-Shankar-Mahad.m4a"},
        {"name": "Sultan", "file": f"{BASE_URL}/angry/Sultan-Title-Song-Salman-Khan-Anushka-Sharma-Sukhwinder-Sing.m4a"},
        {"name": "Ziddi dil", "file": f"{BASE_URL}/angry/Ziddi-Dil-Full-Video-MARY-KOM-Feat-Priyanka-Chopra-Vishal-Da.m4a"}
    ],
    "rock": [
        {"name": "Afghan Jalebi", "file": f"{BASE_URL}/rock/Afghan-Jalebi-Ya-Baba-FULL-VIDEO-Song-Phantom-Saif-Ali-Khan-.m4a"},
        {"name": "Badtameez Dil", "file": f"{BASE_URL}/rock/Badtameez-Dil-Full-Song-HD-Yeh-Jawaani-Hai-Deewani-PRITAM-Ra.m4a"},
        {"name": "Balam Pichkari", "file": f"{BASE_URL}/rock/Balam-Pichkari-Full-Song-Video-Yeh-Jawaani-Hai-Deewani-PRITA.m4a"},
        {"name": "Bhaag D K Bose", "file": f"{BASE_URL}/rock/Bhaag-D-K-Bose-Aandhi-Aayi-Ram-Sampath-Imraan-Khan-Vir-Das-K.m4a"},
        {"name": "Bismil", "file": f"{BASE_URL}/rock/Bismil-Haider-Full-Video-Song-Official-Shahid-Kapoor-Shraddh.m4a"},
        {"name": "Dance Basanti", "file": f"{BASE_URL}/rock/Dance-Basanti-Official-Song-Ungli-Emraan-Hashmi-Shraddha-Kap.m4a"},
        {"name": "Desi Girl", "file": f"{BASE_URL}/rock/Desi-Girl-Full-Video-Dostana-John-Abhishek-Priyanka-Sunidhi-.m4a"},
        {"name": "Dilbar", "file": f"{BASE_URL}/rock/DILBAR-Lyrical-Satyameva-Jayate-John-Abraham-Nora-Fatehi-Tan.m4a"},
        {"name": "Hookah Bar", "file": f"{BASE_URL}/rock/Full-Video-Hookah-Bar-Khiladi-786-Akshay-Kumar-Asin-Himesh-R.m4a"},
        {"name": "Masakali", "file": f"{BASE_URL}/rock/Full-Video-Masakali-Delhi-6-Abhishek-Bachchan-Sonam-Kapoor-A.m4a"},
        {"name": "Mauja Hi Mauja", "file": f"{BASE_URL}/rock/Full-Video-Mauja-Hi-Mauja-Jab-We-Met-Shahid-kapoor-Kareena-K.m4a"},
        {"name": "Lets Nacho", "file": f"{BASE_URL}/rock/Let-s-Nacho-Kapoor-Sons-Sidharth-Alia-Fawad-Badshah-Benny-Da.m4a"},
        {"name": "Malang", "file": f"{BASE_URL}/rock/Malang-Song-DHOOM-3-Aamir-Khan-Katrina-Kaif-Siddharth-Mahade.m4a"},
        {"name": "Manali Trance", "file": f"{BASE_URL}/rock/Manali-Trance-Yo-Yo-Honey-Singh-Neha-Kakkar-The-Shaukeens-Li.m4a"},
        {"name": "Manma Emotion Jaage", "file": f"{BASE_URL}/rock/Manma-Emotion-Jaage-Dilwale-Varun-Dhawan-Kriti-Sanon-Party-A.m4a"},
        {"name": "Offo", "file": f"{BASE_URL}/rock/Offo-Full-Video-Song-2-States-Arjun-Kapoor-Alia-Bhatt-Amitab.m4a"},
        {"name": "Pretty Woman", "file": f"{BASE_URL}/rock/Pretty-Woman-Full-Video-Kal-Ho-Naa-Ho-Shah-Rukh-Khan-Preity-.m4a"},
        {"name": "Rock-N_Roll", "file": f"{BASE_URL}/rock/Rock-N-Roll-Soniye-Best-Video-KANK-Amitabh-Bachchan-Shah-Ruk.m4a"},
        {"name": "Sher Aaya Sher", "file": f"{BASE_URL}/rock/Sher-Aaya-Sher-Gully-Boy-Siddhant-Chaturvedi-Ranveer-Singh-A.m4a"},
        {"name": "Udd daa Punjab", "file": f"{BASE_URL}/rock/Ud-daa-Punjab-Full-Video-Udta-Punjab-Vishal-Dadlani-Amit-Tri.m4a"},
        {"name": "Mujhko Yaad Sataye Teri", "file": f"{BASE_URL}/rock/Mujhko-Yaad-Sataye-Teri-Lyrical-Video-Song-Phir-Hera-Pheri-A.m4a"}
    ],
    "neutral": [
        {"name": "Ilahli", "file": f"{BASE_URL}/neutral/ILAHI-FULL-SONG-WITH-LYRICS-YEH-JAWAANI-HAI-DEEWANI-PRITAM-R.m4a"},
        {"name": "Piya Tose Naina", "file": f"{BASE_URL}/neutral/Piya-Tose-Naina-Laage-Re-Cover-Jonita-Gandhi-feat-Keba-Jerem.m4a"},
        {"name": "Tu Jo Mila", "file": f"{BASE_URL}/neutral/Tu-Jo-Mila-Full-Song-with-LYRICS-K-K-Pritam-Salman-Khan-Hars.m4a"},
        {"name": "Ve kamleya", "file": f"{BASE_URL}/neutral/Ve-Kamleya-Rocky-Aur-Rani-Kii-Prem-Kahaani-Ranveer-Alia-Prit.m4a"},
        {"name": "Manwa Laage", "file": f"{BASE_URL}/neutral/OFFICIAL-Manwa-Laage-FULL-VIDEO-Song-Happy-New-Year-Shah-Ruk.m4a"},
        {"name": "Qaafirana", "file": f"{BASE_URL}/neutral/Qaafirana-Kedarnath-Sushant-Rajput-Sara-Ali-Khan-Arijit-Sing.m4a"},
        {"name": "Safarnama", "file": f"{BASE_URL}/neutral/Safarnama-Video-Song-Tamasha-Ranbir-Kapoor-Deepika-Padukone-.m4a"},
        {"name": "Saibo", "file": f"{BASE_URL}/neutral/Saibo-Lyric-Video-Shor-In-The-City-Radhika-Apte-Tusshar-Kapo.m4a"},
        {"name": "sajde", "file": f"{BASE_URL}/neutral/Sajde-Full-Song-Kill-Dil-Ranveer-Parineeti-Arijit-Singh-Nihi.m4a"},
        {"name": "Sajni", "file": f"{BASE_URL}/neutral/Sajni-Song-Arijit-Singh-Ram-Sampath-Laapataa-Ladies-Aamir-Kh.m4a"},
        {"name": "Samjhawan", "file": f"{BASE_URL}/neutral/Samjhawan-Lyric-Video-Humpty-Sharma-Ki-Dulhania-Varun-Alia-A.m4a"},
        {"name": "Shayad", "file": f"{BASE_URL}/neutral/Shayad-Love-Aaj-Kal-Kartik-Sara-Arushi-Pritam-Arijit-Singh.m4a"},
        {"name": "Tujh Mein Rab Dikhta Hai", "file": f"{BASE_URL}/neutral/Tujh-Mein-Rab-Dikhta-Hai-Song-Rab-Ne-Bana-Di-Jodi-Shah-Rukh-.m4a"},
        {"name": "Aashiq Tera", "file": f"{BASE_URL}/neutral/Aashiq-Tera-Official-Song-Happy-Bhag-Jayegi-Diana-Penty-Abha.m4a"},
        {"name": "Aazaadiyan", "file": f"{BASE_URL}/neutral/Aazaadiyan-Pairon-Ki-Bediyan.m4a"},
        {"name": "Maahi Ve", "file": f"{BASE_URL}/neutral/A-R-Rahman-Maahi-Ve-Full-Song-Audio-Highway-Alia-Bhatt-Rande.m4a"},
        {"name": "Tere Bina", "file": f"{BASE_URL}/neutral/A-R-Rahman-Tere-Bina-Best-Video-Guru-Aishwarya-Rai-Abhishek-.m4a"},
        {"name": "Darkhaast", "file": f"{BASE_URL}/neutral/DARKHAAST-Full-Video-Song-SHIVAAY-Arijit-Singh-Sunidhi-Chauh.m4a"},
        {"name": "Mast Magan", "file": f"{BASE_URL}/neutral/Mast-Magan-Full-Song-with-Lyrics-2-States-Arijit-Singh-Arjun.m4a"},
        {"name": "Dil Dhadkane Do", "file": f"{BASE_URL}/neutral/Dil-Dhadakne-Do-Full-Video-Song-Zindagi-Na-Milegi-Dobara-Hri.m4a"}
    ]
}

# --- Sidebar ---
st.sidebar.markdown("<div class='sidebar-title'>🎭 Emotion Selection</div>", unsafe_allow_html=True)
selected_emotion = st.sidebar.selectbox("Select an Emotion", playlists.keys())
songs = playlists[selected_emotion]
current_song = songs[st.session_state.selected_song]

# --- Liked Songs ---
st.sidebar.markdown("### 💖 Liked Songs")
if not st.session_state.liked_songs:
    st.sidebar.info("No liked songs yet.")
else:
    for idx, liked_song in enumerate(st.session_state.liked_songs):
        if st.sidebar.button(f"🎧 {liked_song['name']}", key=f"liked_{idx}"):
            for i, s in enumerate(songs):
                if s["name"] == liked_song["name"]:
                    st.session_state.selected_song = i
                    st.rerun()

# --- Audio Player ---
# Add this import at the top with other imports
import requests
import io

def autoplay_audio(file_path, song_name):
    try:
        if file_path.startswith('http'):
            # For URLs, download the content first
            response = requests.get(file_path)
            response.raise_for_status()
            audio_data = response.content
            # Skip duration check for now
            duration = "--:--"

        else:
            # For local files
            with open(file_path, "rb") as f:
                audio_data = f.read()
                duration = "--:--"

        b64 = base64.b64encode(audio_data).decode()
        
        html = f"""
        <div style="background-color: #e5e1de; padding:15px; border-radius:20px; box-shadow: 0 8px 25px #89a8b2;">
            <b>🎶 Now Playing: {song_name}</b> <span style="color: #666;">({duration})</span>
            <audio controls autoplay style="width:100%;margin-top:10px">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        </div>
        """
        components.html(html, height=130)
    except Exception as e:
        st.error(f"Error playing {song_name}: {str(e)}")
        html = f"""
        <div style="background-color: #ffe6e6; padding:15px; border-radius:20px;">
            <b>⚠️ Error Playing: {song_name}</b>
            <p>The audio file could not be loaded.</p>
        </div>
        """
        components.html(html, height=130)

autoplay_audio(current_song["file"], current_song["name"])

# --- Controls ---
col1, col2, col3, col4, col5= st.columns(5)
with col1:
    if st.button("⏮️", key="prev_btn", help="Previous Song"):
        st.session_state.last_action = "prev"
        st.session_state.selected_song = (st.session_state.selected_song - 1) % len(songs)
        st.rerun()
with col2:
    if st.button("🔀", key="shuffle_btn", help="Shuffle Playlist"):
        st.session_state.shuffle = not st.session_state.shuffle
        st.toast(f"Shuffle {'Enabled' if st.session_state.shuffle else 'Disabled'}")
        st.rerun()
with col3:
    if st.button("🔁", key="repeat_btn", help="Repeat Current"):
        st.session_state.repeat = not st.session_state.repeat
        st.toast(f"Repeat {'Enabled' if st.session_state.repeat else 'Disabled'}")
        st.rerun()
with col4:
    if st.button("⏭️", key="next_btn", help="Next Song"):
        st.session_state.last_action = "next"
        if st.session_state.repeat:
            pass  # Stay on current
        elif st.session_state.shuffle:
            next_song = random.randint(0, len(songs) - 1)
            while next_song == st.session_state.selected_song and len(songs) > 1:
                next_song = random.randint(0, len(songs) - 1)
            st.session_state.selected_song = next_song
        else:
            st.session_state.selected_song = (st.session_state.selected_song + 1) % len(songs)
        st.rerun()
with col5:
    liked = any(s['name'] == current_song['name'] for s in st.session_state.liked_songs)

    if st.button("❤️" if liked else "🤍", key=f"like_{st.session_state.selected_song}", help="Like this song"):
        if liked:
            st.session_state.liked_songs = [s for s in st.session_state.liked_songs if s['name'] != current_song['name']]
        else:
            st.session_state.liked_songs.append(current_song)
        st.rerun()


st.markdown("</div>", unsafe_allow_html=True)

# --- Playlist Display ---
for i, song in enumerate(songs):
    is_active = i == st.session_state.selected_song
    with st.form(f"song_{i}"):
        if st.form_submit_button(f"🎶 {song['name']}", use_container_width=True):
            st.session_state.selected_song = i
            st.rerun()
        st.markdown("""
            <style>
            div[data-testid="stForm"] button {
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)

        # Update the sidebar styling
        st.markdown("""
        <style>
        section[data-testid="stSidebar"] {
            background-color: #e5e1de;
            border-radius: 20px;
            box-shadow: 0 8px 25px #89a8b2;
            padding: 20px;
        }
        
        /* Style for the selectbox in sidebar */
        section[data-testid="stSidebar"] .stSelectbox {
            background-color: rgba(137, 168, 178, 0.3);
            border-radius: 10px;
            padding: 5px;
            margin: 10px 0;
        }
        
        section[data-testid="stSidebar"] .stSelectbox > div {
            background-color: white !important;
            border-radius: 8px !important;
            border: 2px solid #89a8b2 !important;
            padding: 5px !important;
        }
        
        section[data-testid="stSidebar"] .stSelectbox:hover > div {
            border-color: #6a8994 !important;
            box-shadow: 0 0 10px rgba(137, 168, 178, 0.3) !important;
        }
        </style>
        """, unsafe_allow_html=True)
