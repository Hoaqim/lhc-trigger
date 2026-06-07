import json, time, numpy as np, boto3, streamlit as st

lam = boto3.client("lambda", region_name="eu-central-1")
st.title("HEP event trigger — live")
slot = st.empty()
while True:
    resp = lam.invoke(FunctionName="hep-stats")
    s = json.loads(resp["Payload"].read())
    with slot.container():
        a, b = st.columns(2)
        a.metric("Events scored", s["events"])
        b.metric("Signal fraction", s["signal_fraction"])
        st.metric("Live accuracy", s["live_accuracy"])
        if s["scores"]:
            st.bar_chart(np.histogram(s["scores"], bins=20)[0])
    time.sleep(3)