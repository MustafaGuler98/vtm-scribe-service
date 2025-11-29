# Elysium Scribe Service

A lightweight Python microservice designed to handle PDF operations for the **Elysium V:tM Character Generator**. 

This service receives character data in JSON format and populates a fillable PDF sheet using `pypdf`. It is built with **FastAPI** to ensure low latency and is deployed on **Vercel**.

## 🚀 API Endpoints

### `POST /generate-pdf`

Accepts a character object and streams back a filled PDF file.

*   **Input:** JSON (Character Data)
*   **Output:** `application/pdf` (Streamed)

## 🛠 Extensibility & Usage

While this service is tailored for Project Elysium, the core logic in `pdf_service.py` is generic. Developers can fork this repository to build their own auto-fillers for Mr.Gone's character sheets. 

## 🤝 Special Thanks & Credits

A huge thank you to **Mr. Gone** for his legendary work in creating the definitive character sheets for the community. 

*   **Mr. Gone's Character Sheets:** [https://mrgone.rocksolidshells.com](https://mrgone.rocksolidshells.com)
*   *Permission was kindly granted by Mr. Gone to use his sheets in this project.*

## 🛠 Tech Stack

*   **Language:** Python 3.9+
*   **Framework:** FastAPI
*   **Libraries:** pypdf
*   **Infrastructure:** Vercel (Serverless Functions)

## 🔗 Related Project

This is the backend service for the main application: [Elysium](https://elysium.mustafaguler.me)