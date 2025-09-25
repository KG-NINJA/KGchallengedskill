# KGchallengedskill

### Kyoto voxel experiment
- Converted **PLATEAU CityGML data of Kyoto (Gion / Higashiyama area)** into voxel blocks.  
- Initial approach: **Minecraft-style cityscape**.  
- Adjustments: applied height exaggeration, reduced block size, expanded radius.  
- Final result: a **wireframe "megademo"-style visualization** built directly from **real Kyoto urban data**, lightweight enough to run in WebGL.  
- https://x.com/FuwaCocoOwnerKG/status/1970435527989141817

### Osaka subway simulation
- Built a prototype to simulate passenger flow on the **Osaka Metro Midosuji Line**.  
- Parameters included station order, inflow per station, boarding/alighting counts, and capacity per train.  
- Ran scenarios such as **one trainset running 4 round trips**, then compared the output with **official Osaka Metro ridership data (~1.2M daily passengers)**.  
- Outcome:  
  - The model reproduced relative station load (Umeda, Namba, Tennoji as top stations).  
  - Absolute numbers were ~1/3 of real peak capacity (sim ~570 vs. real ~1,800 per train).  
  - Demonstrated how **real ridership statistics can be used to scale crowd simulations toward realistic congestion levels**.  
  - https://x.com/FuwaCocoOwnerKG/status/1970366303123972212


##AutoKaggler — Titanic Pipeline (CI + Kaggle API Automated Submission) 

https://github.com/KG-NINJA/autokaggler

Role: Developer / Demonstrator
Date: 2025
Format: Kaggle Competition Automation Demo

📜 Overview

Using the Kaggle Titanic competition as a model, we built an automated submission pipeline using CI/CD and the Kaggle API. We automated the submission process in a stable and reproducible manner, demonstrating the practicality of AI-operated technology.

Technical Features

Workflow design using GitHub Actions

Automatic submission using the Kaggle API

Consistency through JSON input/output and structured logging

Ensuring reproducibility through random seeding and stratified CV

Supporting model interpretation through feature importance output

Results

Automatically generates submission.csv files that perfectly match the official Kaggle format

Adding commit hashes to submission comments ensures traceability

Consistently outputs a score of 0.75598 (above average)

Significance

Implemented a system that enables beginners to complete the submission process, which would normally take several hours, in just a few seconds

Reinterpreting Kaggle Titanic from an "introductory exercise in accuracy competition" to an "exercise for automation and reproducibility"


## Nano Banana Hackathon
Nano Banana 48 Hour Hackathon (Kaggle × Google DeepMind, 2025)


https://www.kaggle.com/competitions/banana


Participated in a 48-hour hackathon-style Kaggle competition hosted by Google DeepMind.

Format uniqueness:

Only one submission allowed per participant.


Participation
2,723 Entrants

816 Submissions

Application + demo video required, not just a model score.

Focused on building with Gemini 2.5 Flash Image (Nano Banana) in novel ways.

Scale and selectivity:



Result: Delivered SceneMixer, a live web app that transforms an uploaded character image into cinematic clips with consistent identity, heart-rate-driven narration, and immersive presentation.
https://www.kaggle.com/competitions/banana/writeups/scenemixer

## OpenAI to Z Challenge — Jungle Anomaly Finder (NDVI Satellite Explorer)

**Role:** Independent Researcher / Builder  
https://www.kaggle.com/kgninja


**Timeline:** 2025  
**Format:** Selective, hackathon-style write-up track

# 📜 Resume Entry — Kaggle x OpenAI Hackathon

## OpenAI to Z Challenge (Kaggle × OpenAI, 2025)

- Participated in a **rare hackathon-style Kaggle competition** hosted by OpenAI.  
- **Format uniqueness**:  
  - Only **one submission per team allowed** (no retries).  
  - **English write-up required** with reproducibility and multi-source validation.  
  - Unlike typical Kaggle challenges, no official dataset was provided; participants had to gather and analyze open data independently.  
- **Scale and selectivity**:  
  - **8,156 entrants**, but only **229 final submissions** (<3%).  
  - Reached final submission despite being a first-time entrant — successfully completing a challenge with one of the **lowest completion rates in Kaggle history**.  
- **Skills demonstrated**:  
  - Research and integration of open satellite/LiDAR datasets.  
  - Analytical rigor under strict one-shot submission constraints.  
  - Clear communication and documentation in English for global reproducibility.  

🔗 Kaggle Write-up: [Jungle Anomaly Finder – NDVI Satellite Explorer](https://www.kaggle.com/competitions/openai-to-z-challenge/writeups/jungle-anomaly-finder-ndvi-satellite-explorer)  
🔗 GitHub Repository: [openai-to-z-fuwa](https://github.com/KG-NINJA/openai-to-z-fuwa/blob/main/README.md)  

---


Built an end-to-end, open-source geospatial pipeline (NDVI anomaly detection + contextual layers) and completed a **final write-up submission** — one of the comparatively few participants who finished end-to-end within the time window.

<!-- Proof of completion -->
![Kaggle “Your Work — Submitted” (proof of completion)](openai-to-z-final-submission.png)

<!-- Challenge stats snapshot -->
![Kaggle challenge stats (host/prize/entrants/submissions)](openai-to-z-stats.png)

**Links**  
- Final write-up (Kaggle): *Jungle Anomaly Finder — NDVI Satellite Explorer*  
  https://www.kaggle.com/competitions/openai-to-z-challenge/writeups/jungle-anomaly-finder-ndvi-satellite-explorer  
- Source code (GitHub):  
  https://github.com/KG-NINJA/openai-to-z-fuwa/blob/main/README.md

  **Skills Demonstrated**  
- Sustained delivery across multiple checkpoints with strict deadlines  
- End-to-end geospatial pipeline design (data → analysis → visualization → reporting)  
- Reproducible research documentation in English  
- Project management and perseverance in a selective global competition

**Methods & Stack:** Python · NDVI/remote sensing · GIS (raster/vector) · Reproducible research workflows

*Advanced through all stages of the two-month, checkpoint-based hackathon (OpenAI to Z Challenge). 
The competition imposed strict one-submission rules, multiple deadlines, and rigorous compliance checks. 
At each checkpoint, many entrants dropped out due to documentation, reproducibility, and eligibility requirements. 
Successfully delivered a final write-up by the June 29th deadline, avoiding common disqualification pitfalls 
that eliminated a large share of participants.*

---

## Soham Interviewing Simulator — Challenge Log

https://github.com/KG-NINJA/soham.penrose/blob/main/readme.md

**Role:** Participant / Strategist  
**Timeline:** 2025  
**Format:** AI-based interview & negotiation simulator

**Overview**  
Completed an AI-powered interview simulation game modeled on real-world negotiation challenges.  
The simulator demanded **adaptability, negotiation skills, emotional intelligence, and strategic AI use**.  
Advanced to **Global Rank #34**, received multiple virtual offers, and successfully secured a top-tier "shramp" offer, which is known for its difficulty.

**Key Achievements**
- 🎯 Reached Overall Rank #34 globally  
- 💰 Negotiated a $110,000 finalized offer (missed a $140,000 offer by seconds)  
- 🦐 Achieved an offer from “shramp,” regarded as harder than Ramp (final-boss equivalent)  
- 📊 Sent 7 applications, received 2 confirmed offers (29% success rate)  
- ⚡ Demonstrated integrity-based playstyle in a system designed for deception — turning honesty into a winning strategy  

**Skills Demonstrated**
- Real-time adaptability in negotiation scenarios  
- Strategic use of AI tools combined with human intuition  
- Resilience under strict timeouts and high-pressure decision making  
- Cross-cultural communication and emotional intelligence
---
## LLM ##
ChatGPT , Google Gemini , Claude , Grok


Most of my PC skills are the result of converting my life experiences into Ninjutsu through the LLM.

## Programming & Scripting
Python, JavaScript, HTML5, PowerShell

## Data Science & AI
Notebook LM, OpenAI API（GPT-3/4/4o）Realtime API, Gemini, Gemini API, Claude, GPTs（カスタムGPT）, Prompt Engineering, Few-shot, Chain of Thought, Transformers,Ollama, Whisper API, Suno, Sora, Veo

## AI Agents & Automation
Windsurf, Devin, OpenHands, OpenInterpreter, n8n, API連携,Codex CLI,Jules 

## Data & Visualization
Google Earth Engine, NDVI解析, 衛星画像解析, GeoJSON, Markdown自動生成, PDFレポート自動生成, 画像生成AI（DALL-E, Stable Diffusion, Midjourney）

## Web & Cloud
GitHub, GitHub Actions, CI/CD, GitHub Pages, Notion API, Chrome拡張開発, Telegra.ph API, Firebase Studio, Firebase Auth, Cloud Functions, Google Colab

## OS & Devices
Windows, Linux, Ubuntu, Raspberry Pi（Zero）, IoT（Raspberry Pi＋AI＋センサー）(arduino＋shield) , free VMware

## NLP & Knowledge
NLP（自然言語処理）, OSM（OpenStreetMap）API, 地名解析（トポニム分析）

##OSS Models via Japanese Cloud Servers

Experimented with running open-source LLMs on Japanese cloud servers to handle Japanese text files without mojibake issues.

Focused on ensuring compatibility with Windows environments where encoding defaults often cause problems.

Tested end-to-end pipeline: PowerShell → OSS model API → BOM-safe text/PDF output.

Demonstrated how cloud-hosted OSS models can bridge enterprise adoption of AI in Japan by eliminating encoding friction.

##Others

YouTube video editing & channel operation, Lyrics writing, Simple composition, Keyboard instruments, Guitar, Singing




