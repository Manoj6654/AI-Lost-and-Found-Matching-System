# AI-Based Lost & Found Matching System

> **Final-Year B.E. Artificial Intelligence & Machine Learning Project**

A complete full-stack web application that intelligent matches reported lost and found items using Natural Language Processing (NLP) text similarity, computer vision image histogram correlation, and multi-attribute weighted scoring algorithms.

---

## 🌟 Key Features

1. **User Authentication & Role Management**:
   - Secure registration, session-based login/logout.
   - Werkzeug salted password hashing.
   - Role-based separation: Standard Users vs System Administrators.

2. **Lost & Found Reporting**:
   - Submit item details: Name, Category, Description, Color, Brand, Location, Date, Time, Image upload, and secret identifying marks.
   - Secure file upload processing and image format validation.

3. **Multi-Attribute AI Matching Engine**:
   - **NLP Text Matching**: Preprocessing + `TfidfVectorizer` (unigrams & bigrams) + Cosine Similarity.
   - **Computer Vision Matching**: OpenCV HSV color histogram correlation for uploaded photos.
   - **Attribute Similarity**: Taxonomy matching for categories, sequence matching for locations, and date proximity exponential decay function.
   - **Configurable Weights** (defined in `config.py`):
     - Text/Description: **35%**
     - Category: **20%**
     - Color & Brand: **15%**
     - Location Proximity: **15%**
     - Date Distance: **10%**
     - Image Features: **5%**

4. **Dynamic Match Results & Badging**:
   - **90% – 100%**: `Very High Match` (Green Badge)
   - **75% – 89%**: `High Match` (Teal Badge)
   - **50% – 74%**: `Possible Match` (Yellow Badge)
   - **Below 50%**: `Low Match` (Secondary Badge)
   - Human-readable reason checklist generation explaining why items matched.

5. **Notification & Claim System**:
   - Automated real-time alerts for scores $\ge 75\%$.
   - Submit ownership claim requests with verification proof message.
   - Admin approval releases secure contact details (Email, Phone) to facilitate item recovery.

6. **Professional Admin Dashboard**:
   - Analytics overview (Total Users, Lost Items, Found Items, Matches, Pending Claims, Resolved Cases).
   - User account moderation.
   - Item status management (Active, Claimed, Resolved, Delete).
   - Review, approve, or reject item claims.

---

## 📁 Project Structure

```
lost_found_ai/
│
├── app.py                     # Flask application factory and server entrypoint
├── config.py                  # AI weights, database, and system settings
├── seed_data.py               # Seed database script (10 Lost, 10 Found, Demo Case)
├── requirements.txt           # Python dependency specifications
├── README.md                  # Project documentation & execution guide
│
├── models/
│   └── models.py              # SQLAlchemy ORM models (User, Item, Match, Claim, Notification)
│
├── routes/
│   ├── auth.py                # Registration, Login, Logout, Session handling
│   ├── user.py                # Dashboard, Notifications, My Reports
│   ├── items.py               # Report Lost/Found, Item Details, Search/Filter
│   ├── matches.py             # Match Results, Dynamic AI Matching Trigger, How AI Works
│   ├── claims.py              # Submit Claims, Claim status viewing
│   └── admin.py               # Admin Dashboard, Users/Items/Matches/Claims Management
│
├── ai/
│   ├── text_matching.py       # TF-IDF & Cosine Similarity processor
│   ├── image_matching.py      # OpenCV HSV histogram matcher
│   └── matching_engine.py    # Weighted scoring engine & reason generator
│
├── templates/                 # Jinja2 HTML5 Templates
│   ├── base.html              # Bootstrap 5 layout & navbar
│   ├── index.html             # Landing page
│   ├── login.html             # Login form
│   ├── register.html          # Registration form
│   ├── dashboard.html         # User dashboard
│   ├── report_lost.html       # Report lost item form
│   ├── report_found.html      # Report found item form
│   ├── item_detail.html       # Item details view
│   ├── my_reports.html        # User submitted items
│   ├── matches.html           # Match results list
│   ├── match_detail.html      # Side-by-side match breakdown
│   ├── notifications.html     # Real-time notification list
│   ├── claims.html            # User claims tracker
│   ├── how_it_works.html      # Educational AI explanation page
│   └── admin/
│       ├── dashboard.html     # Admin statistics overview
│       ├── users.html         # User management
│       ├── items.html         # Item management
│       ├── matches.html       # Match management
│       └── claims.html        # Claim review & approval
│
├── static/
│   ├── css/
│   │   └── style.css          # Custom styling & match badges
│   ├── js/
│   │   └── main.js            # Image preview & alert handler
│   └── uploads/               # Uploaded item images
│
└── instance/
    └── database.db            # SQLite database file
```

---

## 🛠️ Technology Stack

- **Backend**: Python 3.x, Flask, Flask-SQLAlchemy, Werkzeug
- **AI / ML**: `scikit-learn` (`TfidfVectorizer`, `cosine_similarity`), `OpenCV` (`cv2`), `Pillow` (`PIL`), `NumPy`
- **Frontend**: HTML5, CSS3, JavaScript (ES6), Bootstrap 5.3, Bootstrap Icons, Jinja2 Templates
- **Database**: SQLite3

---

## 🚀 How to Run the Project in VS Code (Windows)

### Step 1: Open Terminal in Project Directory
Navigate to the project root:
```bash
cd C:\Users\Dell\.gemini\antigravity\scratch\lost_found_ai
```

### Step 2: Create & Activate Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Populate Seed Data & Initialize Database
Run the seeding script to create the SQLite database, populate 10 lost and 10 found items, and execute the AI engine:
```bash
python seed_data.py
```

### Step 5: Start the Flask Application
```bash
python app.py
```

### Step 6: Open Web Application in Browser
Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Pre-Configured Test Accounts

| Role | Email | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@lostfound.ai` | `adminpassword` | Full admin control, approve/reject claims, delete items/users |
| **User 1** | `john@gmail.com` | `password123` | Report items, view matches, submit claims |
| **User 2 (Sarah)** | `sarah@gmail.com` | `password123` | Demo case lost item owner |
| **User 3 (Alex)** | `alex@gmail.com` | `password123` | Demo case found item reporter |

---

## 🧪 Demonstrating the Requirement #20 Demo Test Scenario

To present the project during a BE AI/ML evaluation, use this pre-configured scenario:

1. **Lost Item Report** (Owner: `sarah@gmail.com`):
   - *"Black Samsung Galaxy smartphone with cracked screen, lost near college library on 5 August."*
2. **Found Item Report** (Reporter: `alex@gmail.com`):
   - *"Black Samsung mobile phone, cracked display, found near college library on 5 August."*

### Demo Verification Steps:
1. Log in as `sarah@gmail.com` (password: `password123`).
2. Go to **AI Matches** or **Dashboard**.
3. Observe the top match candidate showing a **High / Very High Match Score (~87% - 94%)**.
4. Click **View Match** to inspect the side-by-side comparison.
5. Review the AI Recommendation Factors list:
   - `✓ Exact Category Match: Electronics`
   - `✓ High Description Similarity (88%)`
   - `✓ Matching Color: Black`
   - `✓ Matching Brand: Samsung`
   - `✓ Nearby Location Match: 'College Library'`
   - `✓ Exact Same Date Reported`
6. Click **Submit Ownership Claim**.
7. Log out and log in as System Admin (`admin@lostfound.ai` / `adminpassword`).
8. Go to **Pending Claims**, click **Approve**.
9. Log back in as `sarah@gmail.com` under **My Claims** to see the approved status and the released contact details for `alex@gmail.com` (`+1-555-0789`).

Author Manoj Kumar KR
---

## 🔮 Future Enhancements

- Integration of Deep Learning convolutional neural networks (e.g. MobileNet / ResNet) for semantic image feature embeddings.
- Automated geolocation map distance radius calculation using Leaflet.js or Google Maps API.
- Automated SMS/WhatsApp notifications via Twilio integration.
