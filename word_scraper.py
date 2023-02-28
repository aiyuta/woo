import streamlit as st
import requests
from bs4 import BeautifulSoup
import re


st.markdown("<h1 style='text-align:center;'> WORD Scraper </h1>", unsafe_allow_html=True)
with st.form("Search"):
    keyword = st.text_input("Enter your Keyword")
    search = st.form_submit_button("search")
    html_code = f"""
        <a id="yg-widget-0" class="youglish-widget" data-query="{keyword}" data-lang="english" data-zones="all,us,uk,aus" data-components="8415" data-bkg-color="theme_light"  rel="nofollow" href="https://youglish.com">Visit YouGlish.com</a>
        <script async src="https://youglish.com/public/emb/widget.js" charset="utf-8"></script>
    """
    st.components.v1.html(html_code, height=600)
placeholder = st.empty()


@st.cache_data(show_spinner=False)
def prounc(search_keyword):
    try:
        page_prounc = requests.get(f"https://www.merriam-webster.com/dictionary/{search_keyword}")    
        soup = BeautifulSoup(page_prounc.text, 'html.parser')
        json_script = soup.find('script', type='application/ld+json')
        json_data = json_script.string.strip()    
        match = re.search(r'"contentURL": "([^"]+)"', json_data)
        if match:
            audio_url = match.group(1)
        return audio_url
    except Exception as e:
        pass

if search:
    # Display the audio and images
    link = prounc(keyword)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.audio(link, format='audio/mp3')
        page_img = requests.get(f"https://unsplash.com/s/photos/{keyword}")
        soup = BeautifulSoup(page_img.content, 'lxml')
        rows = soup.find_all("div", class_='ripi6')
        for row in rows:
            figures = row.find_all('figure')
            img = figures[0].find('img', class_="tB6UZ a5VGX")
            list = img["srcset"].split("?")
            st.image(list[0])
    with col2:
        st.markdown('[Definition](https://www.merriam-webster.com/dictionary/{keyword})')
        page_img = requests.get(f"https://unsplash.com/s/photos/{keyword}")
        soup = BeautifulSoup(page_img.content, 'lxml')
        rows = soup.find_all("div", class_='ripi6')
        for row in rows:
            figures = row.find_all('figure')
            img = figures[1].find('img', class_="tB6UZ a5VGX")
            list = img["srcset"].split("?")
            st.image(list[0])

