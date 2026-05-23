# NASA ETF & SpaceX SPV Daily Tracker (GitHub Actions)

This repository automatically tracks the daily top 10 holdings of the **Tema Space Innovators ETF (NASA)** along with the daily shares of **SpaceX SPV**, updating your personal Google Sheet every day after market close.

The tracker runs completely on **GitHub Actions** and requires no local computing resource or paid servers. It communicates with your Google Sheet using a **Google Apps Script Web App** (zero complex Google Cloud credential setups required!).

---

## 🛠️ Step-by-Step Setup Guide

Follow these simple steps to set up and activate your daily tracker:

### Step 1: Set up the Google Sheet

1. Create a **new Google Sheet** (or open an existing one).
2. Open the script editor by clicking **Extensions > Apps Script** from the top menu.
3. Delete any default code in `Code.gs` and paste the exact contents of the [apps_script.js](apps_script.js) file from this repository.
4. Save the project (click the disk icon 💾 or press `Ctrl + S`).

---

### Step 2: Deploy as a Web App

1. In the Apps Script editor, click the **Deploy** button (top-right corner) and select **New deployment**.
2. Click the gear icon ⚙️ next to "Select type" and select **Web app**.
3. Configure the following settings:
   - **Description**: `NASA Tracker Receiver`
   - **Execute as**: `Me (your_email@gmail.com)`
   - **Who has access**: `Anyone` *(Note: This is required so GitHub Actions can send updates to it. Your sheet remains private, and only those who know this long private URL can trigger updates).*
4. Click **Deploy**.
5. Google will ask you to authorize permissions. Click **Authorize Access**, log into your Google account, click **Advanced** (at the bottom of the security warning), and click **Go to Untitled project (unsafe)** to approve permissions.
6. Copy the **Web App URL** shown in the "New deployment" window. (It will look like `https://script.google.com/macros/s/AKfycb.../exec`).

---

### Step 3: Configure GitHub Repository Secret

1. Push this folder to a **new private (or public) GitHub repository**.
2. On your GitHub repository page, click **Settings** (tab at the top).
3. On the left sidebar, click **Secrets and variables > Actions**.
4. Click the green **New repository secret** button.
5. Configure the secret:
   - **Name**: `GOOGLE_SHEET_WEBAPP_URL`
   - **Value**: *Paste the Web App URL you copied in Step 2.*
6. Click **Add secret**.

---

## 🚀 How to Run and Test

Your tracker is now fully configured! It is scheduled to run automatically every day at **23:00 UTC** (6:00 PM EST / 7:00 PM EDT). 

To run and test it **immediately**:
1. On your GitHub repository page, click the **Actions** tab at the top.
2. Select **Daily NASA ETF & SpaceX Tracker** from the left sidebar.
3. Click the **Run workflow** dropdown on the right side and click the green **Run workflow** button.
4. Refresh the page in 30 seconds. You will see the job running.
5. Check your Google Sheet! Two new tabs will be created automatically:
   - `SpaceX_SPV_Shares`: Stores dates, direct SPV shares, and SpaceX common share equivalents.
   - `NASA_Top_10_Holdings`: Stores historical daily top 10 holdings with ranks, tickers, names, and percentage weights.

---

## 📊 Sheet Structure and Design

The script automatically applies premium, readable styles directly to your Google Sheet:
- **No extra text**: Only the raw, structured data.
- **Top 10 Holdings tab**: Logs historical data day-by-day.
- **SpaceX SPV Shares tab**: Appends daily share numbers with automatic formatting.
- **Formattings applied**: Automatically styles weight columns as percentage (`0.00%`), formats shares with commas (`#,##0.00`), bolds table headers, and resizes columns automatically for a polished desktop-dashboard look.
