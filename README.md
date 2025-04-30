# Instagram Automation

## 📌 Project Description
This project automates **liking posts on Instagram** using **Python and Requests**. It allows users to:

- **Like a specific post** using its URL.
- **Like the latest post** from a public Instagram profile.
- Manage **cookies** and **authentication** for seamless interactions with Instagram.

🚀 This tool is designed for developers who want to automate Instagram interactions using Python.

---

## 🔧 Installation & Setup

### **Prerequisites**

- **Python 3.8+**
- **Poetry** (for package management)
- **A valid Instagram session cookie** (exported from your browser)

### **1️⃣ Clone the Repository**

```sh
 git clone https://github.com/yourusername/instagram-auto-liker.git
 cd instagram-auto-liker
```

### **2️⃣ Install Dependencies with Poetry**

```sh
 poetry install
```

### **3️⃣ Set Up Your Cookies**

Save your **Instagram session cookies** in `cookies.json` in the root directory.

Example `cookies.json`:

```json
[
    {"name": "csrftoken", "value": "your_csrf_token"},
    {"name": "sessionid", "value": "your_session_id"}
]
```

---

## 🚀 Usage

Run the script and choose an option:

```sh
 poetry run python send-like.py
```

---

## 📂 Project Structure

```
instagram-auto-liker/
├── README.md              # Project documentation
├── cookies.json           # Instagram session cookies
├── poetry.lock            # Poetry lock file
├── pyproject.toml         # Poetry configuration
├── send-like.py           # Main script for interaction
```

---

