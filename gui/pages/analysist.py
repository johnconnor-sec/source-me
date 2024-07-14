import streamlit as st 
from langchain_community.llms import Ollama 
import matplotlib.pyplot as plt
import pandas as pd
from pandasai import Agent
# from pandasai.llm.local_llm import LocalLLM
from pandasai import SmartDataframe
from pandasai.exceptions import NoCodeFoundError

llm = Ollama(model="deepseek-coder-v2:latest")

# pandas_ai = PandasAI(llm)

plt.switch_backend('Agg')

uploader_file = st.file_uploader("Upload a CSV file", type= ["csv"])

if uploader_file is not None:
    data = pd.read_csv(uploader_file)
    st.write(data.head(10))
    df = SmartDataframe(data, name="Bank Statements", description="This is my bank statement from June of 2024", config={"llm": llm})
    # agent = Agent(df)
    prompt = st.text_area(f"Enter your prompt for PandasAI:") # agent.chat())

    if st.button("Generate PandasAI Response"):
        if prompt:
            with st.spinner("Generating response..."):
                try:
                    response = df.chat(prompt)
                    st.write("Debugging Info:")
                    st.write(f"Response Type: {type(response)}")
                                            
                    if isinstance(response, list):
                        for item in response:
                            st.write(item)
                    st.write(response)
                except KeyError:
                    st.warning(f"KeyError: {e}, Please enter a valid column name!")
                except NoCodeFoundError:
                    st.warning("No code found for the response! Please enter a valid prompt!")
                except Exception as e:
                    st.warning(f"An error occurred: {e}")
        else:
            st.warning("Please enter a prompt!")
            

                
