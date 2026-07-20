# RecapGen (formerly beReal Recap Generator)

> [!NOTE]  
> **🚀 We are LIVE!**  
> This repository contains the **initial Proof-of-Concept (PoC) and experimental playground** (Jupyter Notebooks) for the beat-synced video synthesis engine.  
> The project has since evolved into a full-fledged, production-ready web platform.  
> **Check out the live application here:** [recap-gen.vercel.app](https://recap-gen.vercel.app)

---

## 🏗️ Production Architecture (RecapGen)

**Tech Stack:** React (Vite SPA), FastAPI (Python), Librosa, FFmpeg, Modal (Serverless Containers), Supabase (PostgreSQL + Storage + Auth), Vercel

### The Underlying Pattern & Problem
Turning photo rolls into music videos usually requires hours of manual timeline editing or relying on automated generators that cut mechanically on a rigid BPM clock. Furthermore, heavy digital signal processing (FFT analysis) and multi-frame 1080p FFmpeg transcoding instantly OOM crash standard 512MB–2GB web servers and violate 10–30s edge gateway timeouts (`Vercel/Cloudflare`).

### What We Built & Solved
We decoupled the architecture into an edge-routed presentation layer (Vercel) and an ephemeral serverless compute engine (Modal), introducing a custom acoustic onset algorithm coupled with an asynchronous job-worker protocol and JIT pre-compilation warmups.

#### 1. Decoupled Serverless Engine & Async Job Protocol
- **Non-Blocking Ingestion (`POST /api/process`):** Validates client JWTs, saves raw audio/images to a persistent volume (`modal.Volume`), initializes state (`{"status": "queued"}`) in a distributed memory dictionary (`modal.Dict`), and dispatches background container work via `run_video_job.spawn()`, returning `200 OK` (`{ job_id: "uuid" }`) in `<100ms`.
- **Distributed Memory Polling (`GET /api/status/{job_id}`):** The React frontend polls phase transitions (`detecting beats` -> `generating video` -> `uploading to Supabase` -> `done`) directly from `modal.Dict` across container instances. Enforced immutable dictionary merging (`jobs_dict[job_id] = { **jobs_dict[job_id], "status": new_status, "user_id": user_id }`) to prevent concurrent updates from stripping ownership metadata (`403 Forbidden` bugs).
- **Dual-Key Security:** The client uses `VITE_SUPABASE_ANON_KEY` bound to `auth.uid()` for reading archives (`/my-studio`). Background Modal containers use `SUPABASE_SERVICE_ROLE_KEY` to write rendered `.mp4` artifacts to storage and commit metadata directly to PostgreSQL without client-side network dependency.

#### 2. DSP Warmup Optimization & Parallel Transcoding
- **Librosa Warmup Pre-Compilation (`_warmup_librosa`):** Python's numerical libraries (Librosa, NumPy, Numba) suffer an 8–10s JIT compilation penalty on their first run. We engineered a pre-warm routine during container provisioning that executes dummy FFT and beat-tracking operations against synthetic noise arrays during build time, slashing cold-start DSP latency by **91%** (`~9.0s` -> `<800ms`).
- **Acoustic Onset Beat Tracking:** Computes Short-Time Fourier Transforms (STFT), measures positive spectral energy flux across frequency bins, locks dominant tempo (BPM), and algorithmically downsamples transitions to match the exact number of supplied images at high-impact acoustic moments.
- **Parallel Multi-Core FFmpeg Transcoding:** Sharded image cropping, scaling, and segment encoding across CPU cores using Python `concurrent.futures`. Once segments complete, an FFmpeg `concat` demuxer joins the streams with the source audio in a single high-speed pass without re-encoding video frames.
- **PostgREST Schema Cache Invalidation:** Resolved a critical issue where backend RLS/policy changes committed directly to PostgreSQL left Supabase's PostgREST API layer serving stale permissions (`403 Forbidden` / `"The reel is empty"`). Built explicit database notification hooks (`NOTIFY pgrst, 'reload schema'`) executed via raw `psycopg2` immediately following schema updates, coupled with deterministic public read policies on `public.videos`.

---

## 🧪 Legacy PoC (This Repository)

This repository (`beReal-Recap-Generator`) consists of the original experimentation code.
The [main notebook](https://github.com/arnav7thakur/beReal-Recap-Generator/blob/main/BeReal-Recap-Generator-Generalized%20.ipynb) consists of the working baseline algorithm. 

**Background on the PoC:**
The "BeReal Recap Enhancement Project" was initiated following dissatisfaction with the 2023 recap feature of the social media application BeReal. This project aimed to improve the user experience by creating a more immersive and personalized recap video.

The journey began with obtaining images from BeReal using a third-party website to overcome limitations in the platform's provided recap. A suitable song was then selected to accompany the images. Using a Jupyter notebook, the synchronization process commenced using `librosa`, `numpy`, `pydub`, `moviepy`, and `PIL`.

After iterative experimentation and refinement, a novel approach based on amplitude thresholding and segment-based peak analysis was devised. This method optimized the synchronization process by distributing images based on peak counts within music segments.
