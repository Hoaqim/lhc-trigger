import os, time, requests, numpy as np, streamlit as st
URL = os.environ["STATS_URL"]
st.title("HEP event trigger — live")
slot = st.empty()
while True:
    s = requests.get(URL).json()
    with slot.container():
        a, b = st.columns(2)
        a.metric("Events scored", s["events"])
        b.metric("Signal fraction", s["signal_fraction"])
        st.metric("Live accuracy", s["live_accuracy"])
        if s["scores"]:
            st.bar_chart(np.histogram(s["scores"], bins=20)[0])
    time.sleep(3)