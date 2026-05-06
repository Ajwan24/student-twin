from flask import Flask, request, jsonify, render_template, redirect, session
import numpy as np
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = "secret123"

users = {}

def analyze_student(data):
    try:
        study = float(data.get("study", 0))
        sleep = float(data.get("sleep", 0))
        stress = int(data.get("stress", 0))
        focus = int(data.get("focus", 0))
        feeling = str(data.get("feeling", "")).lower()
    except:
        study, sleep, stress, focus, feeling = 0,0,0,0,""

    stress = max(1, min(10, stress))
    focus = max(1, min(10, focus))

    score = (study*10) + (sleep*5) + (focus*6) - (stress*5)

    if feeling == "good":
        score += 15
    elif feeling == "okay":
        score += 10
    elif feeling == "tired":
        score -= 10
    elif feeling == "stressed":
        score -= 15

    score = max(0, min(100, score))

    avg_pandas = (study + sleep + stress + focus) / 4

    arr = np.array([study, sleep, focus])
    avg_numpy = np.mean(arr)
    std_dev = np.std(arr)

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
        pass

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


def analyze_result(base, data):
    score = base["score"]
    study = base["study"]
    sleep = base["sleep"]
    stress = base["stress"]
    focus = base["focus"]

    if score >= 70:
        profile = "🟢 Organized Student"
        prediction = "High improvement chance"
    elif score >= 40:
        profile = "🟡 Irregular Student"
        prediction = "Needs improvement"
    else:
        profile = "🔴 At Risk"
        prediction = "Risk of decline"

    health = "Good" if sleep >= 7 else "Low"
    consistency = "High" if study >= 4 else "Low"
    balance = "Balanced" if study >= 4 and sleep >= 7 else "Unbalanced"

    if score >= 80:
        level = "🟢 Excellent"
    elif score >= 50:
        level = "🟡 Average"
    else:
        level = "🔴 Weak"

    tips = []

    if sleep < 5:
        tips.append("⚠️ Your sleep is too low. Try to get at least 7 hours.")

    if stress > 7 and study < 3:
        tips.append("⚠️ High stress with low study time.")

    if focus < 4:
        tips.append("🎯 Improve your focus.")

    if score < 40:
        tips.append("🚨 You need improvement plan.")

    if not tips:
        tips.append("👍 You're doing well.")

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

    if data[-1]["score"] > data[-2]["score"]:
        return "📈 Improving"
    elif data[-1]["score"] < data[-2]["score"]:
        return "📉 Declining"
    else:
        return "➖ Stable"


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
            error = "Wrong username"
    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u in users:
            error = "User exists"
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
    return jsonify({**base, **extra})


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


if name == "__main__":
    app.run(host="0.0.0.0", port=10000)
