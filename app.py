from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Demo data stored in memory
student = {
    "name": "Student",
    "goal": "Muscle Building",
    "diet": "veg",
    "budget": 100
}

food_logs = []
water_glasses = 0

FOODS = [
    {"name": "Poha", "meal": "Breakfast", "price": 20,
     "calories": 250, "protein": 6, "veg": True},
    {"name": "Oats with milk", "meal": "Breakfast", "price": 25,
     "calories": 300, "protein": 12, "veg": True},
    {"name": "Dal rice", "meal": "Lunch", "price": 35,
     "calories": 400, "protein": 14, "veg": True},
    {"name": "Egg bhurji with roti", "meal": "Lunch", "price": 40,
     "calories": 380, "protein": 22, "veg": False},
    {"name": "Roasted chana", "meal": "Snack", "price": 10,
     "calories": 120, "protein": 6, "veg": True},
    {"name": "Paneer roti", "meal": "Dinner", "price": 35,
     "calories": 400, "protein": 20, "veg": True},
    {"name": "Chicken with roti", "meal": "Dinner", "price": 50,
     "calories": 450, "protein": 30, "veg": False}
]

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SmartBite | Smart Campus Nutrition</title>
<style>
:root {
  --green:#167653;
  --light:#eaf6ef;
  --dark:#17372a;
  --muted:#6d8276;
}
* {box-sizing:border-box}
body {
  margin:0;background:#f4f8f5;color:var(--dark);
  font-family:Arial,sans-serif;
}
header {
  padding:24px 6%;background:var(--green);color:white;
  display:flex;justify-content:space-between;align-items:center;
  flex-wrap:wrap;gap:12px;
}
header h1 {margin:0;font-size:28px}
header p {margin:6px 0 0}
.pill {background:#ffffff25;padding:9px 14px;border-radius:20px}
main {max-width:1100px;margin:25px auto;padding:0 16px}
h2 {margin-top:0}
.hero {
  padding:26px;border-radius:20px;background:#dff2e5;
  margin-bottom:20px;
}
.hero h2 {font-size:28px;margin-bottom:8px}
.grid {
  display:grid;grid-template-columns:repeat(3,minmax(0,1fr));
  gap:16px;margin-bottom:20px;
}
.card {
  background:white;padding:20px;border-radius:16px;
  box-shadow:0 4px 16px #153b2410;min-width:0;
}
.metric {font-size:28px;font-weight:bold;margin:12px 0}
.muted {color:var(--muted);font-size:14px}
label {display:block;font-size:14px;font-weight:bold;margin-top:12px}
input,select {
  width:100%;padding:12px;margin-top:6px;
  border:1px solid #d4e1d8;border-radius:9px;background:white;
}
button {
  padding:12px 15px;border:0;border-radius:9px;
  background:var(--green);color:white;font-weight:bold;
  cursor:pointer;margin-top:12px;
}
button:hover {opacity:.88}
button.secondary {background:var(--light);color:var(--green)}
button.full {width:100%}
.meal {
  border:1px solid #e3ece5;border-radius:12px;
  padding:14px;margin-top:10px;
}
.meal strong {display:block;margin-bottom:5px}
.row {display:flex;justify-content:space-between;gap:10px;align-items:center}
.result {white-space:pre-line;line-height:1.8}
.notice {font-size:12px;color:var(--muted);line-height:1.5}
@media(max-width:750px) {
  .grid {grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media(max-width:480px) {
  .grid {grid-template-columns:1fr}
  header h1 {font-size:23px}
  .hero h2 {font-size:23px}
}
</style>
</head>
<body>
<header>
  <div>
    <h1>🥗 SmartBite</h1>
    <p>Smart food choices for campus life</p>
  </div>
  <span class="pill">Student Edition</span>
</header>

<main>
  <section class="hero">
    <h2 id="welcome">Eat smart. Spend smart.</h2>
    <p>Plan meals around your preferences and budget, then track what you eat.</p>
    <button onclick="generatePlan()">✨ Build my daily plan</button>
  </section>

  <div class="grid">
    <section class="card">
      <div class="muted">Calories logged</div>
      <div class="metric" id="calories">0</div>
      <div class="muted">kcal · estimated</div>
    </section>
    <section class="card">
      <div class="muted">Protein logged</div>
      <div class="metric" id="protein">0 g</div>
      <div class="muted">From your food log</div>
    </section>
    <section class="card">
      <div class="muted">Food spending</div>
      <div class="metric" id="spending">₹0</div>
      <div class="muted" id="budgetLabel">Daily budget: ₹100</div>
    </section>
  </div>

  <div class="grid">
    <section class="card">
      <h2>Your profile</h2>
      <label>Name</label>
      <input id="name" placeholder="Your name">
      <label>Goal</label>
      <select id="goal">
        <option>Muscle Building</option>
        <option>Healthy Lifestyle</option>
        <option>Weight Management</option>
      </select>
      <label>Food preference</label>
      <select id="diet">
        <option value="veg">Vegetarian</option>
        <option value="nonveg">Non-vegetarian</option>
      </select>
      <label>Daily budget (₹)</label>
      <input id="budget" type="number" min="1" value="100">
      <button class="full" onclick="saveProfile()">Save profile</button>
    </section>

    <section class="card">
      <h2>🍽️ Your meal plan</h2>
      <div id="meals" class="result muted">Build your plan to see suggestions.</div>
      <p class="notice">Food prices and nutrition figures are estimates and may vary.</p>
    </section>

    <section class="card">
      <h2>💧 Water tracker</h2>
      <div class="metric"><span id="water">0</span> glasses</div>
      <p class="muted">Track your water intake today.</p>
      <button onclick="addWater()">+ Add a glass</button>
      <button class="secondary" onclick="resetWater()">Reset</button>
      <hr style="border:0;border-top:1px solid #e5eee7;margin:20px 0">
      <h2>✨ SmartBite tip</h2>
      <p id="tip">Choose a balanced meal and keep your budget in mind.</p>
    </section>
  </div>

  <section class="card" style="margin-bottom:20px">
    <h2>📝 Log your food</h2>
    <div class="grid" style="margin-bottom:0">
      <div>
        <label>Food name</label>
        <input id="foodName" placeholder="e.g. 2 eggs">
      </div>
      <div>
        <label>Calories (kcal)</label>
        <input id="foodCalories" type="number" min="0" placeholder="e.g. 150">
      </div>
      <div>
        <label>Protein (g)</label>
        <input id="foodProtein" type="number" min="0" placeholder="e.g. 12">
      </div>
      <div>
        <label>Cost (₹)</label>
        <input id="foodCost" type="number" min="0" placeholder="e.g. 20">
      </div>
    </div>
    <button onclick="logFood()">+ Add food</button>
    <div id="foodHistory" class="result" style="margin-top:15px"></div>
  </section>
</main>

<footer style="text-align:center;padding:22px" class="muted">
  SmartBite · Student food planner · Prototype
</footer>

<script>
let profile = {name:"Student", goal:"Muscle Building", diet:"veg", budget:100};
let foods = [];
let waterCount = 0;
let currentPlan = [];

async function api(url, options={}) {
  const response = await fetch(url, {
    headers: {"Content-Type":"application/json"},
    ...options
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

async function saveProfile() {
  const budget = Number(document.getElementById("budget").value);
  if (!Number.isFinite(budget) || budget < 1) {
    alert("Enter a valid daily budget.");
    return;
  }
  profile = {
    name: document.getElementById("name").value.trim() || "Student",
    goal: document.getElementById("goal").value,
    diet: document.getElementById("diet").value,
    budget
  };
  try {
    await api("/api/profile", {method:"POST", body:JSON.stringify(profile)});
    document.getElementById("welcome").textContent =
      "Welcome, " + profile.name + "!";
    document.getElementById("budgetLabel").textContent =
      "Daily budget: ₹" + profile.budget;
    await generatePlan();
    await refreshDashboard();
  } catch(e) { alert(e.message); }
}

async function generatePlan() {
  try {
    const data = await api("/api/plan");
    currentPlan = data.meals;
    const container = document.getElementById("meals");
    container.innerHTML = "";
    currentPlan.forEach(food => {
      const div = document.createElement("div");
      div.className = "meal";
      const title = document.createElement("strong");
      title.textContent = food.meal;
      const description = document.createElement("div");
      description.textContent = food.name;
      const info = document.createElement("div");
      info.className = "muted";
      info.textContent = "₹" + food.price + " · " + food.calories +
        " kcal · " + food.protein + " g protein";
      const button = document.createElement("button");
      button.className = "secondary";
      button.textContent = "Log this meal";
      button.onclick = () => logSuggestedFood(food);
      div.append(title, description, info, button);
      container.appendChild(div);
    });
    document.getElementById("tip").textContent = data.tip;
  } catch(e) { alert(e.message); }
}

async function logSuggestedFood(food) {
  await addLog(food.name, food.calories, food.protein, food.price);
}

async function logFood() {
  const name = document.getElementById("foodName").value.trim();
  const calValue = document.getElementById("foodCalories").value;
  const proteinValue = document.getElementById("foodProtein").value;
  const costValue = document.getElementById("foodCost").value;

  if (!name || calValue === "" || proteinValue === "" || costValue === "") {
    alert("Fill in all food fields.");
    return;
  }
  const values = [Number(calValue), Number(proteinValue), Number(costValue)];
  if (values.some(v => !Number.isFinite(v) || v < 0)) {
    alert("Nutrition and cost values must be non-negative numbers.");
    return;
  }
  await addLog(name, ...values);
  document.getElementById("foodName").value = "";
  document.getElementById("foodCalories").value = "";
  document.getElementById("foodProtein").value = "";
  document.getElementById("foodCost").value = "";
}

async function addLog(name, calories, protein, cost) {
  try {
    await api("/api/log", {
      method:"POST",
      body:JSON.stringify({name, calories, protein, cost})
    });
    await refreshDashboard();
  } catch(e) { alert(e.message); }
}

async function addWater() {
  try {
    const data = await api("/api/water", {method:"POST", body:"{}"});
    waterCount = data.water;
    document.getElementById("water").textContent = waterCount;
  } catch(e) { alert(e.message); }
}

async function resetWater() {
  try {
    const data = await api("/api/water/reset", {method:"POST", body:"{}"});
    waterCount = data.water;
    document.getElementById("water").textContent = waterCount;
  } catch(e) { alert(e.message); }
}

async function refreshDashboard() {
  const data = await api("/api/dashboard");
  document.getElementById("calories").textContent = data.calories;
  document.getElementById("protein").textContent = data.protein + " g";
  document.getElementById("spending").textContent = "₹" + data.spending;
  document.getElementById("water").textContent = data.water;
  document.getElementById("budgetLabel").textContent =
    "Daily budget: ₹" + data.budget;
  document.getElementById("foodHistory").textContent =
    data.logs.length
      ? data.logs.map(x => x.name + " — " + x.calories +
        " kcal, " + x.protein + " g protein, ₹" + x.cost).join("\\n")
      : "No food logged yet.";
}

async function loadProfile() {
  try {
    profile = await api("/api/profile");
    document.getElementById("name").value = profile.name;
    document.getElementById("goal").value = profile.goal;
    document.getElementById("diet").value = profile.diet;
    document.getElementById("budget").value = profile.budget;
    document.getElementById("welcome").textContent = "Welcome, " + profile.name + "!";
    await generatePlan();
    await refreshDashboard();
  } catch(e) { console.error(e); }
}

loadProfile();
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/api/profile", methods=["GET", "POST"])
def profile_api():
    global student
    if request.method == "GET":
        return jsonify(student)

    data = request.get_json(silent=True) or {}
    try:
        budget = float(data.get("budget", 100))
        if budget < 1 or budget > 100000:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify(error="Budget must be between 1 and 100000."), 400

    diet = data.get("diet", "veg")
    if diet not in ("veg", "nonveg"):
        return jsonify(error="Invalid food preference."), 400

    goal = data.get("goal", "Healthy Lifestyle")
    if goal not in ("Muscle Building", "Healthy Lifestyle", "Weight Management"):
        return jsonify(error="Invalid goal."), 400

    student = {
        "name": str(data.get("name", "Student"))[:60],
        "goal": goal,
        "diet": diet,
        "budget": budget
    }
    return jsonify(student)

@app.route("/api/plan")
def meal_plan():
    allowed = [f for f in FOODS if student["diet"] == "nonveg" or f["veg"]]
    meals = []
    for meal_name in ("Breakfast", "Lunch", "Snack", "Dinner"):
        options = [f for f in allowed if f["meal"] == meal_name]
        if options:
            meals.append(options[0])

    tips = {
        "Muscle Building": "Include protein-rich foods and regular balanced meals.",
        "Healthy Lifestyle": "Choose a variety of foods, including vegetables and protein sources.",
        "Weight Management": "Focus on balanced meals and consistent habits, not extreme restriction."
    }
    return jsonify(meals=meals, tip=tips[student["goal"]])

@app.route("/api/log", methods=["POST"])
def log_food():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    if not name or len(name) > 100:
        return jsonify(error="Enter a food name under 100 characters."), 400

    try:
        calories = float(data["calories"])
        protein = float(data["protein"])
        cost = float(data["cost"])
        if any(not 0 <= x <= 100000 for x in (calories, protein, cost)):
            raise ValueError()
    except (KeyError, ValueError, TypeError):
        return jsonify(error="Enter valid non-negative nutrition and cost values."), 400

    food_logs.append({
        "name": name,
        "calories": calories,
        "protein": protein,
        "cost": cost
    })
    return jsonify(ok=True)

@app.route("/api/dashboard")
def dashboard():
    return jsonify(
        calories=round(sum(f["calories"] for f in food_logs), 1),
        protein=round(sum(f["protein"] for f in food_logs), 1),
        spending=round(sum(f["cost"] for f in food_logs), 2),
        logs=food_logs,
        water=water_glasses,
        budget=student["budget"]
    )

@app.route("/api/water", methods=["POST"])
def add_water():
    global water_glasses
    water_glasses += 1
    return jsonify(water=water_glasses)

@app.route("/api/water/reset", methods=["POST"])
def reset_water():
    global water_glasses
    water_glasses = 0
    return jsonify(water=water_glasses)

@app.route("/api/health")
def health():
    return jsonify(status="SmartBite is running")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)