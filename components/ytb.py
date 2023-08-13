import streamlit as st
import os
import json
import shutil
import wget
from pytube import YouTube
from youtubesearchpython import VideosSearch, Suggestions, ResultMode
from st_keyup import st_keyup
from streamlit_extras.stateful_button import button as sf_button

THIS_PATH = os.path.abspath(__file__)
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(THIS_PATH)), "outputs")
IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(THIS_PATH)), "images")
SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(THIS_PATH)), "saves")
suggestions = Suggestions(language = "vi", region = "VN")

def search_ytb(query, limit = 20):
    searchs = VideosSearch(query, region = "VN", limit = limit)
    searchs = searchs.result()["result"]
    return [{
        "type": s["type"],
        "title": s["title"],
        "publishedTime": s["publishedTime"],
        "duration": s["duration"],
        "viewCount": s["viewCount"]["text"],
        "thumbnails": s["thumbnails"][0]["url"],
        "link": s["link"]
    } for s in searchs]

def suggest_ytb(query):
    response = json.loads(suggestions.get(query, mode = ResultMode.json))
    return response["result"]
    
def get_url_n_save(path, mp3 = True):
    shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, mode = 0o777, exist_ok = True)
    yt = YouTube(path)
    if mp3:
        video = yt.streams.filter(only_audio=True).first()
    else:
        video = yt.streams.get_by_resolution("720p")
    out_file = video.download(output_path=OUTPUT_DIR)
    new_file = os.path.join(OUTPUT_DIR, f"{st.session_state['name']}.mp4")
    if mp3:
        new_file = os.path.join(OUTPUT_DIR, f"{st.session_state['name']}.mp3")
    os.rename(out_file, new_file)
    return new_file

def init():
    save_dir = os.path.join(SAVE_DIR, st.session_state["name"])
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, mode = 0o777, exist_ok = True)
    col1, col2 = st.columns([10, 1])
    with col2:
        show_vid = st.checkbox("Show videos")
        
    with col1:
        tab1, tab2, tab3 = st.tabs(["Youtube search", "Listen now", "Downloaded"])
        with tab1:
            text_input = st_keyup("Query", debounce = 100)
            with st.expander("Suggestions", True):
                st.markdown("\n\n".join(suggest_ytb(text_input)))
            if st.button("Submit", "case2"):
                images = []
                captions = []
                st.toast("Processing your search ...")
                searchs = search_ytb(text_input)
                shutil.rmtree(IMAGE_DIR)
                os.makedirs(IMAGE_DIR, mode = 0o777, exist_ok = True)
                for idx, search in enumerate(searchs):
                    wget.download(search["thumbnails"], os.path.join(IMAGE_DIR, f"i{idx}.jpg"))
                    images.append(os.path.join(IMAGE_DIR, f"i{idx}.jpg"))
                    captions.append(f'{search["title"]} | {search["duration"]} | {search["viewCount"]} | {search["link"]}')
                st.image(images, caption = captions, width = 200)
            
        with tab2:
            text_input = st.text_input("URL or Query")
            col3, col4 = st.columns([5, 1])
            if sf_button("Submit", key = "case1"):
                st.toast("Processing your video ...")
                if text_input.startswith("https://youtube.com/"):
                    file = get_url_n_save(text_input, not show_vid)
                    name_to_suggest = text_input
                else:
                    search = search_ytb(text_input)[0]
                    link = search["link"]
                    name_to_suggest = search["title"]
                    file = get_url_n_save(link, not show_vid)

                st.toast("Done!", icon = "🎉")
                with col3:
                    if show_vid:
                        st.video(file)
                    else:
                        st.audio(file)
                    if st.button("Save", "save"):
                        f_dst = name_to_suggest + "." + file.rsplit("/", 1)[-1].rsplit(".", 1)[-1]
                        dst = os.path.join(save_dir, f_dst)
                        st.info(f"Saved to {dst}")
                        shutil.copyfile(file, dst)
                with col4:
                    images = []
                    captions = []
                    st.toast("Processing your search ...")
                    searchs = search_ytb(name_to_suggest, 5)
                    shutil.rmtree(IMAGE_DIR)
                    os.makedirs(IMAGE_DIR, mode = 0o777, exist_ok = True)
                    for idx, search in enumerate(searchs):
                        wget.download(search["thumbnails"], os.path.join(IMAGE_DIR, f"i{idx}.jpg"))
                        images.append(os.path.join(IMAGE_DIR, f"i{idx}.jpg"))
                        captions.append(f'{search["title"]} | {search["duration"]} | {search["viewCount"]} | {search["link"]}')
                    st.image(images, caption = captions, width = 200)

        with tab3:
            for n in os.listdir(save_dir):
                fp = os.path.join(save_dir, n)
                if sf_button(n, key = n):
                    if fp.endswith(".mp3"):
                        st.audio(fp)
                    else:
                        st.video(fp)
            
def main():
    init()

if __name__ == "__main__":
    main()
