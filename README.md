## 📬 Gmail Job Application Tracker → Google Sheets

A Python script that automatically extracts job application details from your Gmail "Sent" folder and logs them into a CSV file and Google Sheets.

---

### 🔍 Features

- Authenticates with Gmail and Google Sheets using OAuth 2.0
- Searches sent emails for job application threads (e.g., _"Re: Data Engineering at XYZ"_)
- Extracts:

  - Email **Subject**
  - **Company name** (from subject)
  - **Date sent**

- Appends the details to:

  - `job_applications.csv`
  - A linked **Google Sheet**

- Skips duplicates (based on company name)
- Adds a default status (`"in progress"`) for tracking

---

### 📦 Requirements

- Python 3.7+
- Gmail and Sheets APIs enabled on your Google Cloud project
- `credentials.json` (OAuth client secret)
- Libraries:

  - `google-api-python-client`
  - `google-auth-httplib2`
  - `google-auth-oauthlib`
  - `pandas`

---

### 🔐 Setup

1. Enable Gmail and Sheets APIs in [Google Cloud Console](https://console.cloud.google.com/).
2. Download `credentials.json` and place it in the root folder.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the script:

```bash
python main.py
```

---

### 🗃️ File Overview

| File                   | Purpose                                          |
| ---------------------- | ------------------------------------------------ |
| `main.py`              | Extracts email data and appends to CSV           |
| `sheets_upload.py`     | Handles upload of CSV data to Google Sheets      |
| `credentials.json`     | OAuth2 credentials (must be downloaded manually) |
| `token.pickle`         | Stores the auth token after first login          |
| `job_applications.csv` | Local log of applications                        |

---

### 📌 Use Case

Perfect for job seekers who want to **track applications** automatically without manually logging each one. Ideal if you use Gmail and apply to many roles via email.

