# =========================================================
# 📚 Digital Student Twin Project
# =========================================================

# =========================================================
# 🤝 SHARED PART (ALL STUDENTS)
# Flask + Routes + Connection
# =========================================================

from flask import Flask, request, jsonify, render_template, redirect, session
import numpy as np
import pandas as pd
import json

# 🔹 Create Flask App
app = Flask(__name__)   # ✅ FIXED
app.secret_key = "secret123"

# 🔹 Users Storage
users = {}

# =========================================================
# 👩‍💻 STUDENT 1: Analysis & Input
# (Input Handling + Score Calculation)
# =========================================================

def analyze_student(data):
    try:
        study = float(data.get("study", 0))
        sleep = float(data.get("sleep", 0))
        stress = int(data.get("stress", 0))
        focus = int(data.get("focus", 0))
        feeling = str(data.get("feeling", "")).lower()
    except:
        study, sleep, stress, focus, feeling = 0,0,0,0,""

    # Validation
    stress = max(1, min(10, stress))
    focus = max(1, min(10, focus))

    # Score Calculation
    score = (study*10) + (sleep*5) + (focus*6) - (stress*5)

    # Feeling Impact
    if feeling == "good":
        score += 15
    elif feeling == "okay":
        score += 10
    elif feeling == "tired":
        score -= 10
    elif feeling == "stressed":
        score -= 15

    score = max(0, min(100, score))

# =========================================================
# 👩‍💻 STUDENT 2: Data & Intelligence
# (NumPy + Pandas + File Storage)
# =========================================================

    df = pd.DataFrame([{
        "study": study,
        "sleep": sleep,
        "stress": stress,
        "focus": focus
    }])

    avg_pandas = df.mean().mean()

    arr = np.array([study, sleep, focus])
    avg_numpy = np.mean(arr)
    std_dev = np.std(arr)

    # Save History
    try:
        with open("students.json", "a") as f:
            json.dump({
                "study": study,
                "sleep": sleep,
                "stress": stress,
                "focus": focus,
                "score": score
            }, f)
            f.write("\n")
    except:
        print("Error saving file")

    return {
        "score": int(score),
        "avg_numpy": float(avg_numpy),
        "avg_pandas": float(avg_pandas),
        "std_dev": float(std_dev),
        "study": study,
        "sleep": sleep,
        "stress": stress,
        "focus": focus
    }

# =========================================================
# 👩‍💻 STUDENT 3: Prediction & Output
# (Classification + Tips + Trend)
# =========================================================

def analyze_result(base, data):

    score = base["score"]
    study = base["study"]
    sleep = base["sleep"]
    stress = base["stress"]
    focus = base["focus"]

    # Profile
    if score >= 70:
        profile = "🟢 Organized Student"
    elif score >= 40:
        profile = "🟡 Irregular Student"
    else:
        profile = "🔴 At Risk"

    # Prediction
    if score >= 70:
        prediction = "High improvement chance"
    elif score >= 40:
        prediction = "Needs improvement"
    else:
        prediction = "Risk of decline"

    # Status
    health = "Good" if sleep >= 7 else "Low"
    consistency = "High" if study >= 4 else "Low"
    balance = "Balanced" if study >= 4 and sleep >= 7 else "Unbalanced"

    # Level System
    if score >= 80:
        level = "🟢 Excellent"
    elif score >= 50:
        level = "🟡 Average"
    else:
        level = "🔴 Weak"

    # Smart Tips
    tips = []

    if sleep < 5:
        tips.append("⚠️ Your sleep is too low. Try to get at least 7 hours.")

    if stress > 7 and study < 3:
        tips.append("⚠️ High stress with low study time. Try to balance your schedule.")

    if score < 40:
        tips.append("🚨 Your performance is low. You need a serious improvement plan.")

    if focus < 4:
        tips.append("🎯 Improve your focus during study sessions.")

    if study >= 5 and sleep >= 7 and stress < 5:
        tips.append("🔥 Excellent routine! Keep maintaining your performance.")

    if not tips:
        tips.append("👍 You're doing well, but there's still room for improvement.")

    return {
        "profile": profile,
        "prediction": prediction,
        "health": health,
        "consistency": consistency,
        "balance": balance,
        "tips": tips,
        "level": level,
        "trend": get_trend()
    }

# =========================================================
# 📈 TREND FUNCTION (Student 3 Extension)
# =========================================================

def get_trend():
    data = []

    try:
        with open("students.json", "r") as f:
            for line in f:
                data.append(json.loads(line))
    except:
        return "No data"

    if len(data) < 2:
        return "No trend yet"

    last = data[-1]["score"]
    prev = data[-2]["score"]

    if last > prev:
        return "📈 Improving"
    elif last < prev:
        return "📉 Declining"
    else:
        return "➖ Stable"

# =========================================================
# 🔐 ROUTES
# =========================================================

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in users and users[u] == p:
            session["user"] = u
            return redirect("/")
        else:
            error = "❌ Wrong username or password"

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""

    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in users:
            error = "⚠️ User already exists"
        else:
            users[u] = p
            return redirect("/login")

    return render_template("register.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    base = analyze_student(data)
    extra = analyze_result(base, data)
    final = {**base, **extra}
    return jsonify(final)


@app.route("/history")
def history():
    data = []

    try:
        with open("students.json", "r") as f:
            for line in f:
                data.append(json.loads(line))
    except:
        pass

    return render_template("history.html", data=data)

# =========================================================
# 🚀 RUN
# =========================================================

if __name__ == "__main__":   # ✅ FIXED
    app.run(debug=True)