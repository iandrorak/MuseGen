''' 
#### Streamlit App ####
'''

#### Import libraries
import streamlit as st
import model
from PIL import Image

### App config
### Header
image = Image.open('Muse_Gen.png')
st.image(image)

st.markdown("""MUSIC GENERATION""")

st.markdown("---")


### Content
st.subheader("About the project")
st.markdown("""
With this application you can generate a brand new music according to a selected theme.
> Make a choice below and let the magic happen.
""")

st.subheader("Create your music")

col1, col2 = st.columns(2)
melody = ['Sad','Dance']

with col1:

  # with st.form("Select your theme"):
    choice = st.selectbox('Pick one', melody)
    input_midi_data, theme = model.create_input(choice)
    generate = st.button("Generate")

with col2:

    if generate:
        with st.spinner("Generating..."):
          extracted_16 = model.gen_interpolation(input_midi_data,theme)
          g_16bar_mean,  interp_model= model.gen_final(extracted_16,theme)

          st.text("play your song")
          wav_file = model.sequence_to_wav_file(g_16bar_mean, theme) 
          st.audio(wav_file, format='wav') 
