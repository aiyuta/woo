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
import os
from groq import Groq

@st.cache_data(show_spinner=False)
def gemini(input):

    genai.configure(api_key="AIzaSyAbPr_KmwtP7tBU2nsIc1Jve4qZDTJJlWk")
    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    response = model.generate_content(input)
    
    return response.text
    
def groq(input,input_key ):
    client = Groq(
    api_key=input_key,
)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": input,
            }
        ],
        model="Llama3-70b-8192",
    )
    #mixtral-8x7b-32768
    return chat_completion.choices[0].message.content
    
def nvidia_gemma_7b(input):   
    invoke_url = "https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions/1361fa56-61d7-4a12-af32-69a3825746fa"
    fetch_url_format = "https://api.nvcf.nvidia.com/v2/nvcf/pexec/status/"
    
    headers = {
        "Authorization": "Bearer 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",
        "Accept": "application/json",
    }
    
    payload = {
      "messages": [
        {
          "content": input,
          "role": "user"
        }
      ],
      "temperature": 0.3,
      "top_p": 0.7,
      "max_tokens": 1024,
      "seed": 42,
      "bad": None,
      "stop": None,
      "stream": False
    }
    
    # re-use connections
    session = requests.Session()    
    response = session.post(invoke_url, headers=headers, json=payload)    
    while response.status_code == 202:
        request_id = response.headers.get("NVCF-REQID")
        fetch_url = fetch_url_format + request_id
        response = session.get(fetch_url, headers=headers)
    
    response.raise_for_status()
    response_body = response.json()
    return response_body['choices'][0]['message']['content']

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
def deepseek(prompts):
    client = OpenAI(api_key = 'sk-824baeab952b43a4be4ce96173baf807', base_url="https://api.deepseek.com/v1")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content":prompts},
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
def get_random_keys():
    with open("word_data.json") as f:
        data = json.load(f)

    keys = list(data.keys())
    
    # Filter to only single word keys
    keys = [k for k in keys if len(k.split()) == 1] 

    random_keys = random.sample(keys, 5)
    return " ".join(random_keys)

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

def generate_paragraph_randomly():
    keys = get_random_keys()    
    prompt = "create a paragraph based on the keywords provided directly, no any comments:"
    try:
        paragraph = groq(prompt + ":" + keys,input_key)        
        st.write("generated by groq")
    except:
        try:
            paragraph = gemini(prompt + ":" + keys)        
            st.write("generated by gemini")
        except:
            paragraph = nvidia_gemma_7b(prompt + ":" + keys)
            st.write("generated by nvidia")
    st.write(keys)             
    st.write(paragraph)

def delete_keyword(file_path: str, keyword: str) -> None:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found.")
    
    with open(file_path, "r") as f:
        data: Dict[str, any] = json.load(f)       
   
    
    delete_button = st.button("Delete")
    if delete_button:
        del data[keyword]
        
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


st.markdown("<h1 style='text-align:center;'> WORD Scraper </h1>", unsafe_allow_html=True)
# record and play
col5, col6 = st.columns([2, 15])
with col5:
    audio_bytes =audio_recorder(text=' ',pause_threshold=3)
with col6:
    if audio_bytes:
        st.audio(audio_bytes,format='audio/wav')
# input the key
input_key = st.text_input('Enter your api_key')
# search
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

col_del, col_mem = st.columns([2, 2])
with col_del:
    try:
        delete_keyword('word_data.json', keyword)
    except Exception as e:
        st.error(str(e))
with col_mem:
    memorize_button = st.button("memorize")
    try:
        res = groq("help me memorize the word:" + keyword,input_key)
    except:
        pass
if memorize_button:
        try:          
            
            st.write(res)
        except :
            pass
    
    





if search:   
    if keyword[0] == ',':
        keyword = keyword[1:]
        try:
            response = groq(keyword,input_key)
            st.write("generated by groq")
        except:
            #response = gemini(keyword)
            #st.write("generated by gemini")
            response =deepseek(keyword)
            #st.write("generated by deepseek")
        st.write(response)         
    else:
        # Display the audio 
        link = prounc(keyword)
        col3, col4 = st.columns([2, 2])
        with col3:
            st.audio(link, format='audio/mp3')  
        with col4:
            st.markdown(f'[Full Definition](https://www.merriam-webster.com/dictionary/{keyword})')    
        
        # display search result
        try:
            with open("word_data.json") as f: 
                data = json.load(f)      
                if keyword in data:
                    st.write(data[keyword])
                else:
                    
                    len_keyword = keyword.split()
                    
                    if len(len_keyword) == 1:
                        lookup = "You are a kind helpful dictionary assistant.return me with the phonetic, explanation ,root and 5 sentences,display them with breakline.the keyword is"  
                    else:
                        lookup  = "please explain and provide 10 sentences based on the key words, display with a breakline "
                    
                    #response =  chatgpt(keyword,lookup)
                    prompts = lookup + ":" + keyword
                    try:
                        response = groq(prompts,input_key)
                        st.write("generated by groq")
                    except:
                        #response = gemini(prompts)
                        #st.write("generated by gemini")
                        response =deepseek(prompts)
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
            try:
                page_img = requests.get(f"https://unsplash.com/s/photos/{keyword}")
                soup = BeautifulSoup(page_img.content, 'lxml')
                rows = soup.find_all("img", class_='ApbSI vkrMA')
                
                src_list = [row["src"] for row in rows]
                unique_list = []
                for item in src_list:
                    if item not in unique_list:
                        unique_list.append(item)           
            
                for i, list in enumerate(unique_list):
                    # Check if the row order is 1, 3, or 5
                    if (i + 1) % 2 != 0:                       
                        st.image(list)
            except:
                pass
        with col2:      
            try:
                page_img = requests.get(f"https://unsplash.com/s/photos/{keyword}")
                soup = BeautifulSoup(page_img.content, 'lxml')
                rows = soup.find_all("img", class_='ApbSI vkrMA')
                
                src_list = [row["src"] for row in rows]
                unique_list = []
                for item in src_list:
                    if item not in unique_list:
                        unique_list.append(item)
               
                for i, list in enumerate(unique_list):
                    # Check if the row order is 1, 3, or 5
                    if (i + 1) % 2 != 1:                      
                        st.image(list)
            except:
                pass
# random learning
if st.button("Random_learning"):
    generate_paragraph_randomly()



# sidebar
# download and random
note_dolo_to_json()
if st.sidebar.button("Random learning"):
    generate_paragraph_randomly()
    
