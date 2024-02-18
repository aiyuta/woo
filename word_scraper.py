import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from audio_recorder_streamlit import audio_recorder
import datetime
import json
import openai as ai
from openai import OpenAI
import google.generativeai as genai
import random

@st.cache_data(show_spinner=False)
def gemini(input):

    genai.configure(api_key="AIzaSyAbPr_KmwtP7tBU2nsIc1Jve4qZDTJJlWk")
    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    response = model.generate_content(input)
    
    return response.text

def chatgpt(user_text,road):
    Model = 'gpt-3.5-turbo'
    completion = ai.ChatCompletion.create(
        model = Model,
        max_tokens = 2000,
        messages=[
            {"role": "system", "content": road},
            {"role":"user","content":user_text},
        ],
        temperature = 0.75,
    )  
    response= (
        completion ["choices"][0]
        .get('message')
        .get('content')
        .encode('utf8')
        .decode()
    )
    return response
def openroute(usertext,road):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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"
    )

    completion = client.chat.completions.create(
    extra_headers={    
    },
    model="mistralai/mixtral-8x7b-instruct",
    messages=[
        {
        "role": "user",
        "content": usertext +":" + road,
        },
            ],
    )
    return(completion.choices[0].message.content)
def deepseek(usertext,road):
    client = OpenAI(api_key = 'sk-824baeab952b43a4be4ce96173baf807', base_url="https://api.deepseek.com/v1")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": usertext +":" + road},
        ]
    )
    return response.choices[0].message.content

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


st.markdown("<h1 style='text-align:center;'> WORD Scraper </h1>", unsafe_allow_html=True)
api_key = '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'

col5, col6 = st.columns([2, 15])
with col5:
    audio_bytes =audio_recorder(text=' ',pause_threshold=3)
with col6:
    if audio_bytes:
        st.audio(audio_bytes,format='audio/wav')


with st.form("Search"):
    keyword = st.text_input("Enter your Keyword")
    search = st.form_submit_button("search")

    display_youglish = st.checkbox("Display YouGlish")

    if display_youglish:
        html_code = f"""
            <a id="yg-widget-0" class="youglish-widget" data-query="{keyword}" data-lang="english" data-zones="all,us,uk,aus" data-components="8415" data-bkg-color="theme_light"  rel="nofollow" href="https://youglish.com">Visit YouGlish.com</a>
            <script async src="https://youglish.com/public/emb/widget.js" charset="utf-8"></script>
        """
        placeholder = st.empty()
        st.components.v1.html(html_code, height=600)

if search:
    

    # Display the audio 
    link = prounc(keyword)
    col3, col4,col7 = st.columns([3, 2, 2])
    with col3:
        st.audio(link, format='audio/mp3')  
    with col4:
        st.markdown(f'[Full Definition](https://www.merriam-webster.com/dictionary/{keyword})') 
    with col7:
        with open("word_data.json") as f:
          data = json.load(f)      
          if keyword in data:
            delete_button = st.button("Delete")
            if delete_button:
              # del data[keyword]
              # st.write("delete")
    # Display the content generated by gpt-3.5-turbo
    try:
        with open("word_data.json") as f: 
            data = json.load(f)      
            if keyword in data:
                st.write(data[keyword])
            else:
                ai.api_key= api_key
                len_keyword = keyword.split()
                
                if len(len_keyword) == 1:
                    lookup = "You are a kind helpful dictionary assistant.return me with the phonetic, explanation ,root and 5 sentences,display them with a breakline"  
                else:
                    lookup  = "please explain and provide 10 sentences based on the key words, display with a breakline "
                
                #response =  chatgpt(keyword,lookup)
                
                try:
                    response = gemini(lookup + ":" + keyword)
                    st.write("generated by gemini")
                except:
                    response =deepseek(lookup,keyword)
                    st.write("generated by deepseek")
                st.write(response)         
                # save to dictionary
                data[keyword] = "\n"+response
                # save to data file
                with open("word_data.json", "w") as f:
                    json.dump(data, f, indent=4)
    except:
        st.write("API problem!")
    
    # Display the images
    col1, col2 = st.columns([2, 2])
    with col1:             
        page_img = requests.get(f"https://unsplash.com/s/photos/{keyword}")
        soup = BeautifulSoup(page_img.content, 'lxml')
        rows = soup.find_all("div", class_='ripi6')
        try:
            for row in rows:
                figures = row.find_all('figure')
                img = figures[0].find('img', class_="tB6UZ a5VGX")
                list = img["srcset"].split("?")
                st.image(list[0])
        except:
            pass
    with col2:        
        page_img = requests.get(f"https://unsplash.com/s/photos/{keyword}")
        soup = BeautifulSoup(page_img.content, 'lxml')
        rows = soup.find_all("div", class_='ripi6')
        try:
            for row in rows:
                figures = row.find_all('figure')
                img = figures[1].find('img', class_="tB6UZ a5VGX")
                list = img["srcset"].split("?")
                st.image(list[0])
        except:
            pass


def note_dolo_to_json():
    # Define a default value for the text box
    default_text = ""

    # Define a dictionary to store the JSON data
    with open("word_data.json") as f: 
        data = json.load(f)

    # Create a text box for the user to input text
    text_box = st.sidebar.text_input("Note here:", value=default_text)

    # Create a submit button
    if st.sidebar.button("Submit"):
        # Get the current time and format it as a string
        now = datetime.datetime.now()
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # Add the text box value to the data dictionary with the current time as the key
        data[time_str] = text_box
         # Save the data to a JSON file
        with open("word_data.json", "w") as f:
            json.dump(data, f, indent=4)

    # Convert the data dictionary to a JSON string
    json_str = json.dumps(data, indent=4)

    # Create a download button for the JSON file
    st.sidebar.download_button(
        label="Download Note",
        data=json_str,
        file_name="word_data.json",
        mime="application/json",
    )
def get_random_keys():
    with open("word_data.json") as f:
        data = json.load(f)

    keys = list(data.keys())
    
    # Filter to only single word keys
    keys = [k for k in keys if len(k.split()) == 1] 

    random_keys = random.sample(keys, 5)
    return ",".join(random_keys)



note_dolo_to_json()
if st.sidebar.button("Random learning"):
    keys = get_random_keys()
    
    prompt = "create a paragraph based on the keywords provided directly, no any comments:"
    try:
        paragraph = gemini(prompt + ":" + keys)
        st.write("generated by gemini")
    except:
        paragraph =deepseek(prompt,keyword)
        st.write("generated by deepseek")
    st.write(keys)             
    st.write(paragraph)
