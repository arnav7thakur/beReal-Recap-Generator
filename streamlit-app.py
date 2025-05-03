import streamlit as st
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from moviepy.editor import ImageSequenceClip, concatenate_videoclips
import os
import tempfile
from pathlib import Path
import shutil

st.set_page_config(page_title="Beat Synced Video Generator", layout="centered")

st.title("🎶 Beat-Synced Image Video Generator")
st.markdown("Upload an **audio file** and **images**, and generate a video where image transitions sync with the music beats.")

# Upload inputs
audio_file = st.file_uploader("Upload MP3 audio", type=["mp3"])
images = st.file_uploader("Upload image files", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if audio_file and images:
    with st.spinner("Processing audio and images..."):
        # Create temp directory (persistent during session)
        temp_dir = tempfile.mkdtemp()
        tmp_path = Path(temp_dir)

        # Save audio
        audio_path = tmp_path / audio_file.name
        with open(audio_path, "wb") as f:
            f.write(audio_file.read())

        # Load and process audio
        y, sr = librosa.load(audio_path)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, aggregate=np.median)
        onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, backtrack=True)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, units="frames")
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        all_times = sorted(set(np.concatenate((onset_times, beat_times))))
        num_beats = len(all_times)

        st.success(f"✅ Detected {num_beats} beat moments.")

        # Show waveform
        fig, ax = plt.subplots(figsize=(10, 4))
        librosa.display.waveshow(y, sr=sr, ax=ax)
        ax.vlines(all_times, ymin=-1, ymax=1, color="r", linestyle="dashed", label="Beats")
        ax.set_title("Waveform with Beat Markers")
        ax.set_xlabel("Time (s)")
        ax.legend()
        st.pyplot(fig)

        # Save uploaded images
        image_paths = []
        for img_file in images:
            img_path = tmp_path / img_file.name
            with open(img_path, "wb") as f:
                f.write(img_file.read())
            image_paths.append(str(img_path))

        image_paths.sort()

        # --- Progress Bar ---
        progress_bar = st.progress(0)
        status_text = st.empty()

        image_clips = []
        total_steps = num_beats + 2
        step = 0

        status_text.text("🔄 Syncing images with beats...")

        for i in range(num_beats):
            img_index = i % len(image_paths)
            img_path = image_paths[img_index]
            duration = all_times[i + 1] - all_times[i] if i < num_beats - 1 else 0.2

            clip = ImageSequenceClip([img_path], durations=[duration])
            image_clips.append(clip)

            step += 1
            progress_bar.progress(step / total_steps)

        status_text.text("📽️ Compiling video...")

        # --- Final Video ---
        final_clip = concatenate_videoclips(image_clips, method="compose")
        output_path = tmp_path / "final_output.mp4"
        final_clip.write_videofile(str(output_path), codec="libx264", fps=12, audio=str(audio_path), audio_fps=sr, verbose=False, logger=None)

        step += 1
        progress_bar.progress(step / total_steps)

        # Show results
        status_text.text("✅ Video ready! Watch or download below.")
        st.video(str(output_path))
        st.download_button("⬇️ Download Video", data=open(output_path, "rb"), file_name="beat_synced_video.mp4")

        # Cleanup button
        if st.button("🧹 Clear Temporary Files"):
            shutil.rmtree(temp_dir)
            st.success("Temporary files cleared.")
