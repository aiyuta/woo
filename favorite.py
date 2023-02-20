import streamlit as st
import json
import os
import pyperclip


# Function to read data from JSON file
def read_data():
    if not os.path.exists('data.json'):
        # Create an empty JSON file if it does not exist
        with open('data.json', 'w') as f:
            json.dump({}, f)
    with open('data.json') as f:
        data = json.load(f)
    return data

# Function to write data to JSON file
def write_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f)

# Create a Streamlit app
def app():
    # Set the title of the app
    st.title('Favorite Website')
    # Read data from JSON file
    data = read_data()

    # Move the input fields to the sidebar
    with st.sidebar:
        website = st.text_input('Website')
        
        paste_button = st.button('Paste link')
        
        # If the "Paste" button is clicked, paste the contents of the clipboard into the "Link" input field
        if paste_button:
            link = pyperclip.paste()
            st.text_input('Link', value=link)
        else:
            link = st.text_input('Link')
        group = st.text_input('Group')
        if st.button('Submit'):
        # Add the entered data to the data dictionary
            if group not in data:
                data[group] = []
            data[group].append({'website': website, 'link': link})
            # Write the updated data to the JSON file
            write_data(data)

    

    # Display the data in a horizontal way
    max_columns = 7
    for group in data:
        st.header(group)
        website_links = data[group]
        for i in range(0, len(website_links), max_columns):
            cols = st.columns(max_columns)
            for j in range(max_columns):
                if i+j < len(website_links):
                    website_name = website_links[i+j]['website']
                    website_url = website_links[i+j]['link']
                    website_key = f"{group}_{i+j}"
                    with cols[j].container():
                        # Add a CSS rule to hide the button by default
                        st.markdown("""
                            <style>
                                .delete-button {
                                    display: none;
                                }
                                .delete-button:hover {
                                    display: inline-block;
                                }
                            </style>
                        """, unsafe_allow_html=True)
                        # Display the website name and button
                        cols[j].write(f"<a href='{website_url}' target='_blank'>{website_name}</a><button class='delete-button'>x</button>", unsafe_allow_html=True)
                        if cols[j].button('', key=website_key):
                            # Remove the website from the data dictionary
                            website_index = i+j
                            data[group].pop(website_index)
                            # Update the website keys in the data dictionary
                            for k in range(website_index, len(data[group])):
                                old_key = f"{group}_{k+1}"
                                new_key = f"{group}_{k}"
                                data[group][k]['key'] = new_key
                            # Write the updated data to the JSON file
                            write_data(data)
                            # Reload the app to update the displayed data
                            st.experimental_rerun()

        # Remove the group if all websites have been deleted
        if len(website_links) == 0:
            del data[group]
            write_data(data)
            st.experimental_rerun()

# Run the app
if __name__ == '__main__':
    app()