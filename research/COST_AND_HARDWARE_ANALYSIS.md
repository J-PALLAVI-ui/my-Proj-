# FUJINOVA — Cost, Hardware Constraints & Capacity Analysis

**Document Version:** 1.0.0  
**Status:** COMPLETE (Stage 0 Discovery)  
**Host Environment:** Windows 11 Home/Pro (Build 22631+)  
**Processor:** AMD Ryzen 7 5800H (8 Cores / 16 Threads @ 3.2 GHz base, up to 4.4 GHz boost)  
**System Memory:** 16.0 GB DDR4-3200 MHz  
**Dedicated Graphics:** NVIDIA GeForce RTX 3050 Laptop GPU (4.0 GB GDDR6 VRAM, 75W TGP)  
**Available Disk Storage:** Approximately 63 GB free on SSD  
**Author:** FujiNova Infrastructure & Capacity Planner  

---

## 1. Development Hardware Feasibility Assessment

The developer laptop presents a capable development environment provided we respect its two principal physical bottlenecks: **16 GB System RAM** and **4 GB GPU VRAM**.

### Memory (RAM) Budget Analysis

To prevent Windows pagefile thrashing and thermal throttling, we analyze active memory allocation during peak development:

```
Total System RAM: 16,384 MB (16.0 GB)
----------------------------------------------------------------------
Baseline Windows 11 OS + Background Services:           ~ 4,800 MB
IDE (VS Code / Antigravity with extensions):            ~ 1,500 MB
Web Browser (Chrome / Edge with 8-10 tabs + DevTools):  ~ 2,600 MB
FastAPI Backend + Uvicorn + Python Runtime:             ~   250 MB
In-Memory GTFS Schedules + RAPTOR Routing Arrays:       ~    20 MB
SQLite Database Cache & Working Memory:                 ~    30 MB
Frontend Dev Server (Vite / Node.js):                   ~   220 MB
----------------------------------------------------------------------
Total Allocated Memory under Recommended Stack:         ~ 9,420 MB (~57.5%)
Available Safety Headroom:                              ~ 6,964 MB (~42.5%)
```

#### Why We Must Avoid Java OpenTripPlanner (OTP) or Docker PostGIS:
- If we were to run **OpenTripPlanner 2 (Java JVM)**, it would consume an additional 3,500 MB to 4,500 MB of RAM.
- If we were to run **Docker Desktop (WSL2 with PostgreSQL/PostGIS)**, the `vmmem` process would claim an additional 3,000 MB to 4,000 MB of RAM.
- Adding both would push memory consumption to **16.5 GB**, forcing Windows into aggressive disk paging, freezing the UI, and causing sudden IDE crashes.
- **Verdict:** Our choice of **Python RAPTOR + SQLite WAL** keeps backend memory at a featherweight **~300 MB**, leaving over 6.9 GB of free breathing room.

---

### GPU (VRAM) Budget Analysis: The 4 GB Ceiling

The laptop's NVIDIA RTX 3050 Laptop GPU has exactly **4,096 MB VRAM**.

```
Dedicated GPU VRAM: 4,096 MB
Windows Desktop Window Manager (DWM) & Display:        ~   600 MB
Browser WebGL (MapLibre 3D Vector Map rendering):      ~   450 MB
Available Remaining VRAM for Local AI:                 ~ 3,046 MB
```

#### Local LLM Quantization Reality Check:
* A 7B parameter model in 16-bit float requires **14 GB VRAM** (Cannot run).
* A 7B model quantized to 4-bit (Q4_K_M, e.g., Qwen 2.5 7B or Llama 3.1 8B) requires **~4.4 GB to 4.8 GB VRAM** for weights alone, plus **500 MB to 1 GB** for the KV cache at 4,096 context tokens.
* When loaded in Ollama, approximately 20 of 28 layers can be offloaded to the RTX 3050, while the remaining 8 layers spill into system RAM across the PCIe Gen3 bus.
* **Inference Result:** Generation speeds drop from ~35 tokens/sec to **16–22 tokens/sec**. If context expands to 8k tokens, speeds drop to **8–12 tokens/sec**.
* **Verdict:** Cloud AI inference (Gemini 2.5 Flash / GPT-4o-mini) is **vastly superior** for interactive conversational responsiveness, preserving 100% of GPU resources for fluid 60 FPS WebGL 3D map rendering in the browser.

---

### Disk Storage Budget (63 GB Free Space)

The project storage footprint is remarkably compact:

| Component | Estimated Disk Space | Description / Notes |
| :--- | :---: | :--- |
| **Python Virtual Environment (`.venv`)** | ~ 450 MB | FastAPI, Uvicorn, LangGraph, Pydantic, NumPy, Requests |
| **Node.js (`node_modules`)** | ~ 380 MB | React, Vite, TypeScript, Tailwind, MapLibre GL, Radix UI |
| **Raw GTFS Feeds (Zipped + Extracted)** | ~ 45 MB | Fujikyu Bus GTFS-JP (12 MB) + JR East GTFS (28 MB) |
| **Yamanashi PMTiles Vector Map** | ~ 85 MB | Pre-clipped OpenStreetMap vector tiles for Yamanashi/Fuji |
| **SQLite Application Database** | ~ 60 MB | Places, attractions, stops, and conversation checkpoints |
| **Git Repository & Documentation** | ~ 30 MB | Source code, research docs, markdown assets |
| **Total Estimated Disk Consumption** | **~ 1,050 MB (1.05 GB)** | **Consumes only 1.6% of available 63 GB SSD storage!** |

---

## 3. Financial Cost Analysis: Free Options vs. Unavoidable Expenses

FujiNova is engineered to be **100% cost-free during Stage 0, Stage 1, and core development**.

### Zero-Cost Services & Datasets (Verified Free)

1. **Google AI Studio (Gemini 2.5 Flash / 1.5 Flash):**
   - **Cost:** **$0.00**
   - **Terms:** 15 Requests Per Minute (RPM), 1,500 Requests Per Day (RPD), 1,000,000 Tokens Per Minute (TPM).
   - **Coverage:** Completely covers all manual testing, automated unit tests, and interactive demos.
2. **OpenFreeMap / Protomaps Vector Basemaps:**
   - **Cost:** **$0.00**
   - **Terms:** Completely free, open-source tile hosting without API keys or usage fees.
3. **Fujikyu Bus GTFS-JP Open Data:**
   - **Cost:** **$0.00** (CC BY 4.0 public open data).
4. **ODPT Public Transportation API:**
   - **Cost:** **$0.00** (Free developer registration key).
5. **JARTIC National Highway Traffic Volume API:**
   - **Cost:** **$0.00** (Free MLIT xROAD developer agreement).
6. **OpenStreetMap Overpass API:**
   - **Cost:** **$0.00** (Free community infrastructure with reasonable rate limiting).

---

### Unavoidable or Optional Production Costs

If and when the project transitions from local development to public internet deployment:

| Item | Development Cost | Production Cost (Monthly / Annual) | Necessity Level |
| :--- | :---: | :---: | :--- |
| **OpenAI API Backup Balance** | $0.00 (Optional) | $5.00 one-time prepaid deposit | **Recommended** (Emergency fallback for GPT-4o-mini) |
| **Google Cloud Billing (Gemini Paid Tier)** | $0.00 | $0.50 – $2.00 / month (Pay-per-token at scale) | **Optional** (Only needed if exceeding 1,500 RPD) |
| **Frontend Cloud Hosting (Vercel / Cloudflare)** | $0.00 | $0.00 (Generous free tier for static SPAs) | **Free** |
| **Backend Cloud Hosting (Render / Fly.io / VPS)** | $0.00 | $0.00 (Free tier) to $5.00 / month (512MB RAM instance) | **Free during dev; $5/mo for 24/7 public API** |
| **Custom Domain (`fujinova.travel` or `.jp`)** | $0.00 | ~$12.00 – $25.00 / year | **Optional for deployment** |

---

## 4. Hardware Optimization Guidelines for Implementation

1. **Virtual Environment Discipline:** Use a single local Python virtual environment (`.venv`) inside `d:\FujiNova` created with Python 3.11/3.12.
2. **Preventing Memory Leaks:** Avoid holding full GTFS dataframe objects in LangGraph session memory; compile GTFS routes into immutable lookup dictionaries upon server boot.
3. **Vite Build Hygiene:** Run Vite in development mode (`npm run dev`) which leverages native ES modules and consumes under 250 MB of memory.
4. **Local GPU Hygiene:** Leave local GPU acceleration reserved for MapLibre WebGL map rendering. Do not run heavy local Ollama models simultaneously with cloud agent testing.
