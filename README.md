<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=190&color=0:0f2027,50:203a43,100:2c5364&section=header&text=Jaydeep%20Solanki&fontSize=60&fontColor=ffffff&fontAlignY=38&desc=AI%20Engineering%20%C2%B7%20Backend%20%C2%B7%20Robotics&descSize=30&descAlignY=66" alt="Jaydeep Solanki, AI engineering, backend, robotics and flight software" width="100%">

<img src="https://img.shields.io/badge/Open%20to%20Work-Full--Time-2EA043?style=flat-square" alt="Open to full-time work">
<img src="https://img.shields.io/badge/Bengaluru-India-0B3D91?style=flat-square" alt="Based in Bengaluru, India">
<img src="https://img.shields.io/badge/ECE-Graduate-5C3EE8?style=flat-square" alt="Electronics and communication engineering graduate">
<a href="https://whoisjayd.github.io/resume/resume.pdf" title="Resume, view the PDF"><img src="https://img.shields.io/badge/Resume-View%20PDF-E11D48?style=flat-square&logo=adobeacrobatreader&logoColor=white" alt="Resume, view the PDF"></a>

<div><b>Backend and AI engineer</b>, recent ECE graduate, building reliable services and robotics software. Interested in AI, backend and flight software roles.</div>

&nbsp;

<a href="https://linkedin.com/in/solanki-jaydeep/" title="LinkedIn"><img height="22" width="22" src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/linkedin/linkedin-original.svg" alt="LinkedIn profile"></a> &nbsp; <a href="https://x.com/jaydeepsolankee" title="X"><img height="22" width="22" src="https://cdn.simpleicons.org/x/111111/f0f6fc?viewbox=auto" alt="X profile"></a> &nbsp; <a href="https://peerlist.io/jaydeepsolanki" title="Peerlist"><img height="22" width="22" src="https://cdn.simpleicons.org/peerlist/00AA45?viewbox=auto" alt="Peerlist profile"></a> &nbsp; <a href="https://jaydeepsolanki.vercel.app/" title="Portfolio"><img height="22" width="22" src="https://cdn.simpleicons.org/googlechrome/0969DA?viewbox=auto" alt="Portfolio website"></a> &nbsp; <a href="mailto:contactjaydeepsolanki@gmail.com" title="Email"><img height="22" width="22" src="https://cdn.simpleicons.org/gmail/EA4335?viewbox=auto" alt="Email Jaydeep"></a>

</div>

## About

I studied electronics and have written software alongside it since first year, so I'm comfortable on both sides of the hardware boundary. My competition work covers a robotic arm, a model satellite's flight computer and the ground stations that read its telemetry. Outside competitions I build backend services and command-line tools, two of them on PyPI. I also mentored the juniors who took over our systems, and they ranked higher than we did.

## Experience

- **Engineering Intern, Deloitte** · Current
- **Intern, Ellipsis Infotech** · May to June 2025 · built an [IoT air conditioning control system](https://github.com/whoisjayd/internship-project-ac-control-iot) with ESP8266 firmware, a FastAPI backend and a Next.js dashboard

## Tech Stack

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="https://skillicons.dev/icons?i=py%2Cts%2Cjs%2Ccpp%2Crust%2Cpytorch&theme=light">
    <img src="https://skillicons.dev/icons?i=py,ts,js,cpp,rust,pytorch&theme=dark" alt="Tech stack: Python, TypeScript, JavaScript, C++, Rust, PyTorch">
  </picture>
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="https://skillicons.dev/icons?i=opencv%2Carduino%2Craspberrypi%2Cfastapi%2Cflask%2Cnodejs&theme=light">
    <img src="https://skillicons.dev/icons?i=opencv,arduino,raspberrypi,fastapi,flask,nodejs&theme=dark" alt="Tech stack: OpenCV, Arduino, Raspberry Pi, FastAPI, Flask, Node.js">
  </picture>
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="https://skillicons.dev/icons?i=express%2Cnextjs%2Creact%2Ctailwind%2Cpostgres%2Cmongodb&theme=light">
    <img src="https://skillicons.dev/icons?i=express,nextjs,react,tailwind,postgres,mongodb&theme=dark" alt="Tech stack: Express, Next.js, React, Tailwind, PostgreSQL, MongoDB">
  </picture>
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="https://skillicons.dev/icons?i=redis%2Cdocker%2Ckubernetes%2Cprometheus%2Cgithubactions%2Cvercel&theme=light">
    <img src="https://skillicons.dev/icons?i=redis,docker,kubernetes,prometheus,githubactions,vercel&theme=dark" alt="Tech stack: Redis, Docker, Kubernetes, Prometheus, GitHub Actions, Vercel">
  </picture>
</div>

## Embedded and Robotics

<table>
  <tr>
    <th align="left" width="30%">Project</th>
    <th align="left">What It Does</th>
  </tr>
  <tr>
    <td valign="top"><div><b><a href="https://github.com/whoisjayd/flipkart-grid-5.0">Flipkart GRID Robotic Arm</a></b></div><div><sub>Finalist, Flipkart GRID 5.0, IIT Madras</sub></div></td>
    <td valign="top"><div>Finds a box, picks it up and drops it in the right zone. YOLOv5 on an Intel RealSense camera locates the box in 3D, inverse kinematics gives the joint angles, and a Python app sends them to an Arduino Mega over serial. Two ESP32 cameras read the QR code on separate threads. I built the software and embedded side.</div><div><code>Python</code> <code>YOLOv5</code> <code>OpenCV</code> <code>RealSense</code> <code>Arduino</code> <code>ESP32</code></div></td>
  </tr>
  <tr>
    <td valign="top"><div><b>Model Satellite</b></div><div><sub>Rank 9, Teknofest 2024, Our First International Competition</sub></div><div><a href="https://github.com/whoisjayd/teknofest-model-satellite-telemetry">Flight Software</a> · <a href="https://github.com/whoisjayd/teknofest-model-satellite-gui-telemetry">Ground Station</a></div></td>
    <td valign="top"><div>Flight computer on a Raspberry Pi Zero 2W that reads a BMP390, BNO055 and TMP117, tracks the flight from ascent to recovery, logs to CSV and streams telemetry and camera video to the ground. The desktop ground station shows it live and can replay a CSV as a flight, so we tested the whole chain without flying.</div><div><code>Python</code> <code>asyncio</code> <code>WebSockets</code> <code>Flask</code> <code>PySide6</code> <code>Raspberry Pi</code></div></td>
  </tr>
  <tr>
    <td valign="top"><div><b><a href="https://github.com/whoisjayd/cansat-india-data-visualization-and-control-system">CanSat Ground Station</a></b></div><div><sub>Runner-Up, CanSat India</sub></div></td>
    <td valign="top"><div>PyQt5 app for Team Dyaus that reads live serial telemetry from the CanSat and plots it during flight.</div><div><code>Python</code> <code>PyQt5</code> <code>pyserial</code></div></td>
  </tr>
  <tr>
    <td valign="top"><div><b><a href="https://github.com/whoisjayd/internship-project-ac-control-iot">AC Control IoT</a></b></div><div><sub>Ellipsis Infotech Internship</sub></div></td>
    <td valign="top"><div>Controls an office's air conditioners from one dashboard. ESP8266 boards send IR commands and accept OTA updates, a FastAPI backend stores state in PostgreSQL, and a Next.js dashboard manages devices and zones.</div><div><code>ESP8266</code> <code>MQTT</code> <code>FastAPI</code> <code>PostgreSQL</code> <code>Next.js</code></div></td>
  </tr>
</table>

## Software and Open Source

<table>
  <tr>
    <th align="left" width="30%">Project</th>
    <th align="left">What It Does</th>
  </tr>
  <tr>
    <td valign="top"><div><b><a href="https://github.com/whoisjayd/notewise">NoteWise</a></b></div><div><a href="https://pypi.org/project/notewise/" title="NoteWise latest version on PyPI"><img src="https://img.shields.io/pypi/v/notewise?style=flat-square&logo=pypi&logoColor=white&label=PyPI" alt="NoteWise latest version on PyPI"></a> <a href="https://github.com/whoisjayd/notewise/stargazers" title="NoteWise GitHub stars"><img src="https://img.shields.io/github/stars/whoisjayd/notewise?style=flat-square&logo=github" alt="NoteWise GitHub stars"></a></div></td>
    <td valign="top"><div>CLI that turns a YouTube video or playlist into local Markdown study notes. Splits long videos by chapter, adds optional quizzes, caches transcripts in SQLite, and works with Gemini, OpenAI, Anthropic, Groq and more through LiteLLM. Tested on Linux, Windows and macOS with a 90% coverage gate. Ships on PyPI, as standalone binaries and as a Docker image.</div><div><code>Python</code> <code>Typer</code> <code>LiteLLM</code> <code>SQLAlchemy</code> <code>PyInstaller</code> <code>Docker</code></div></td>
  </tr>
  <tr>
    <td valign="top"><div><b><a href="https://github.com/whoisjayd/blazeserve">BlazeServe</a></b></div><div><a href="https://pypi.org/project/blazeserve/" title="BlazeServe latest version on PyPI"><img src="https://img.shields.io/pypi/v/blazeserve?style=flat-square&logo=pypi&logoColor=white&label=PyPI" alt="BlazeServe latest version on PyPI"></a> <a href="https://pypi.org/project/blazeserve/" title="BlazeServe monthly downloads on PyPI"><img src="https://img.shields.io/pypi/dm/blazeserve?style=flat-square&label=downloads" alt="BlazeServe monthly downloads on PyPI"></a></div></td>
    <td valign="top"><div>HTTP file server for when <code>python -m http.server</code> is too basic. Supports range requests, ETag caching, per-IP rate limiting, TLS, uploads and ZIP streaming, and exposes Prometheus metrics and Kubernetes health endpoints.</div><div><code>Python</code> <code>Prometheus</code> <code>Docker</code> <code>Kubernetes</code></div></td>
  </tr>
  <tr>
    <td valign="top"><div><b><a href="https://github.com/whoisjayd/gitresume">GitResume</a></b></div><div><img src="https://img.shields.io/badge/Status-Archived-6B7280?style=flat-square" alt="GitResume status: archived"> <a href="https://github.com/whoisjayd/gitresume/stargazers" title="GitResume GitHub stars"><img src="https://img.shields.io/github/stars/whoisjayd/gitresume?style=flat-square&logo=github" alt="GitResume GitHub stars"></a></div></td>
    <td valign="top"><div>Reads your GitHub repositories and drafts ATS-friendly resume bullets from them with an LLM. Includes GitHub OAuth and Redis caching.</div><div><code>Python</code> <code>FastAPI</code> <code>Redis</code> <code>Docker</code> <code>OAuth</code></div></td>
  </tr>
</table>

## More Projects

- [Smart Bulb Dashboard](https://github.com/whoisjayd/control-my-home-bulb): self-hosted web app that controls a Tasmota bulb over MQTT
- [Finance Manager](https://github.com/whoisjayd/finance-manager): budgeting and reports web app on Flask and MongoDB
- [Remote Screenshot Server](https://github.com/whoisjayd/remote-screenshot-server): desktop screenshots and a live MJPEG stream over HTTPS
- [LAN File Transfer](https://github.com/whoisjayd/file-transfer): Tkinter app that sends files between computers on a network
- [IMDb TMDb Movie Scraper](https://github.com/whoisjayd/imdb-tmdb-movie-scraper): Scrapy and Selenium scraper with TMDb enrichment
- [Flask MongoDB CRUD API](https://github.com/whoisjayd/flask-mongodb-crud-api): user management REST API with bcrypt hashing
- [Resume Template](https://github.com/whoisjayd/resume): YAML resume rendered with RenderCV and published on GitHub Pages
- [Bank Management System](https://github.com/whoisjayd/bank-management-system): my first project, written in Class 12 with Python and MySQL

<div align="right">
<img src="https://img.shields.io/github/last-commit/whoisjayd/whoisjayd?style=flat-square&label=last%20updated&color=2EA043" alt="Date this profile README was last updated">
<img src="https://komarev.com/ghpvc/?username=whoisjayd&color=00d9ff&style=flat-square&label=profile%20views" alt="Profile view count">
</div>
