# app.py
# ------------------------------------------------------------------
# Streamlit page that embeds a small HTML/JS client to:
#   • fetch /session    (served by backend.py)
#   • open RTCPeerConnection
#   • stream mic audio to gpt-4o-realtime-preview
#   • play remote audio + log data-channel events
#
# Run with:
#   streamlit run app.py --server.port 8501
# ------------------------------------------------------------------
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Realtime WebRTC Demo", layout="centered")
st.title("🎙️ OpenAI Realtime (WebRTC) Demo")

st.write(
    "Click **Connect & Talk** – give mic permission – and start speaking. "
    "The remote model’s audio will play back inside the browser."
)

# Serve the HTML + JS right from Streamlit
components.html(
  """
<!DOCTYPE html>
<html>
<head>
  <style>
    button {font-size:1rem;padding:0.6rem 1.2rem;margin-top:1rem}
    #log {white-space:pre-line;font-family:monospace;margin-top:1rem}
  </style>
</head>
<body>
  <button id="connect">Connect & Talk</button>
  <div id="log"></div>

<script>
const $log = txt => document.getElementById("log").textContent += txt + "\\n";

async function init() {
  try {
    $log("🔑  Fetching EPHEMERAL_KEY …");
    const res = await fetch("http://localhost:8000/session");
    const token = await res.json();
    const EPHEMERAL_KEY = token.client_secret.value;
    $log("✔  Key received");

    // --- 1. PeerConnection ---
    const pc = new RTCPeerConnection();
    pc.onconnectionstatechange = () => $log("PC → " + pc.connectionState);

    // --- 2. Remote audio sink ---
    const audio = document.createElement("audio");
    audio.autoplay = true;
    pc.ontrack = e => (audio.srcObject = e.streams[0]);

    // --- 3. Local microphone track ---
    const ms = await navigator.mediaDevices.getUserMedia({ audio: true });
    pc.addTrack(ms.getTracks()[0]);

    // --- 4. Data-channel logs ---
    const dc = pc.createDataChannel("oai-events");
    dc.onmessage = e => $log("📨 " + e.data);

    // --- 5. SDP offer/answer dance ---
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    const url = "https://api.openai.com/v1/realtime";
    const model = "gpt-4o-realtime-preview";
    const resp = await fetch(`${url}?model=${model}`, {
      method: "POST",
      body: offer.sdp,
      headers: {
        Authorization: `Bearer ${EPHEMERAL_KEY}`,
        "Content-Type": "application/sdp",
      },
    });

    const answer = { type: "answer", sdp: await resp.text() };
    await pc.setRemoteDescription(answer);
    $log("🗣  All set – start talking!");

  } catch (err) {
    console.error(err);
    $log("❌ " + err);
  }
}

document.getElementById("connect").onclick = () => init();
</script>
</body>
</html>
    """,
    height=480,
)
