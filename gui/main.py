import streamlit as st
from streamlit_multipage import MultiPage

app = MultiPage()


def logo():
    st.image("https://avatars.githubusercontent.com/u/45109972?s=200&v=4", width=100)

def create_main_page(header_title):
    st.header(header_title)
    st.write("This is the navigation header.")

def main():
    logo()
    create_main_page("John Connor's Personal Data Collector")
        

if __name__ == "__main__":
    main()
