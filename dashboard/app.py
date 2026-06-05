import os, time, requests, numpy as np, streamlit as st
INF = os.environ["INFERENCE_URL"]
st.title("HEP event trigger — live")
slot = st.empty()
while True:
    s = requests.get(f"{INF}/stats").json()
    with slot.container():
        a, b, c = st.columns(3)
        a.metric("Events/sec", s["events_per_sec"])
        b.metric("Signal fraction", s["signal_fraction"])
        c.metric("Live accuracy", s["live_accuracy"])
        if s["scores"]:
            st.bar_chart(np.histogram(s["scores"], bins=20)[0])
    time.sleep(1)