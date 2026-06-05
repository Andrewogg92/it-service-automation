import sys
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

def extract_and_normalize_row(raw_row):
    if isinstance(raw_row, dict) and "record_date" not in raw_row and "date" not in raw_row and len(raw_row.keys()) == 1:
        row = list(raw_row.values())[0]
    else:
        row = raw_row
    if not isinstance(row, dict): return {}
    return {str(k).strip().lower(): v for k, v in row.items()}

# NEW HELPER: Wraps Make.com's flat strings back into proper JSON arrays
def parse_make_string_to_list(val):
    if not val or val == "null" or val == "None": return []
    if isinstance(val, list): return val
    if isinstance(val, str):
        val = val.strip()
        if not val.startswith('['): val = f"[{val}]"
        try: return json.loads(val)
        except Exception as e:
            print(f"Error parsing list: {e}", file=sys.stderr)
            return []
    return []

@app.route('/generate-forecast', methods=['POST'])
def generate_forecast():
    try:
        data = request.json or {}

        # Extract using our new wrapper helper!
        multiplier = float(data.get("multiplier", 1.0))
        demand_history = parse_make_string_to_list(data.get("demand"))
        task_weights_array = parse_make_string_to_list(data.get("weights"))
        employees = parse_make_string_to_list(data.get("staff"))
        employee_availability = parse_make_string_to_list(data.get("pto"))

        # --- PROCESS WEIGHTS ---
        weights = {}
        for w in task_weights_array:
            w_clean = extract_and_normalize_row(w)
            name_val = next((v for k, v in w_clean.items() if "task_name" in k or "metric" in k), None)
            minutes_val = next((v for k, v in w_clean.items() if "minute" in k), None)
            if name_val and minutes_val is not None:
                weights[str(name_val).strip().lower()] = float(minutes_val)

        if not weights:
            weights = {"tickets_closed": 10.0, "inbound_calls": 12.0, "tech_bar_visits": 10.0, "new_hires": 60.0, "terminations": 25.0, "hardware_upgrades": 60.0}

        # --- PROCESS DEMAND HOURS ---
        daily_demand = {}
        for raw_row in demand_history:
            row = extract_and_normalize_row(raw_row)
            date_str = next((str(v).strip() for k, v in row.items() if "date" in k), None)
            if not date_str or date_str == 'None': continue

            tickets = sum(int(float(v or 0)) for k, v in row.items() if "ticket" in k)
            calls = sum(int(float(v or 0)) for k, v in row.items() if "call" in k)
            tech_bar = sum(int(float(v or 0)) for k, v in row.items() if "tech_bar" in k or "visit" in k)
            new_hires = sum(int(float(v or 0)) for k, v in row.items() if "hire" in k)
            terminations = sum(int(float(v or 0)) for k, v in row.items() if "termination" in k)
            upgrades = sum(int(float(v or 0)) for k, v in row.items() if "upgrade" in k)

            t_hrs = (tickets * weights.get("tickets_closed", 10.0) / 60.0) * multiplier
            c_hrs = (calls * weights.get("inbound_calls", 12.0) / 60.0) * multiplier
            tb_hrs = (tech_bar * weights.get("tech_bar_visits", 10.0) / 60.0) * multiplier
            nh_hrs = (new_hires * weights.get("new_hires", 60.0) / 60.0) * multiplier
            term_hrs = (terminations * weights.get("terminations", 25.0) / 60.0) * multiplier
            upg_hrs = (upgrades * weights.get("hardware_upgrades", 60.0) / 60.0) * multiplier

            total_hrs = t_hrs + c_hrs + tb_hrs + nh_hrs + term_hrs + upg_hrs
            daily_demand[date_str] = {"total_demand_hours": total_hrs, "drivers": {"Tickets": t_hrs, "Calls": c_hrs, "Tech Bar": tb_hrs, "Provisioning": nh_hrs + term_hrs + upg_hrs}}

        # --- PROCESS CAPACITY HOURS ---
        daily_capacity = {d: {"total_capacity_hours": (len(employees) * 8.0) if employees else 128.0, "lost_hours": 0.0} for d in daily_demand}

        for raw_avail in employee_availability:
            avail = extract_and_normalize_row(raw_avail)
            date_str = next((str(v).strip() for k, v in avail.items() if "date" in k), None)
            if date_str in daily_capacity:
                lost = next((float(v or 8.0) for k, v in avail.items() if "removed" in k or "hour" in k), 0.0)
                daily_capacity[date_str]["total_capacity_hours"] -= lost
                daily_capacity[date_str]["lost_hours"] += lost

        # --- FORMAT OUTPUT ---
        forecast_results = []
        for date_str, demand_data in daily_demand.items():
            c_hrs = daily_capacity.get(date_str, {"total_capacity_hours": 0.0})["total_capacity_hours"]
            d_hrs = demand_data["total_demand_hours"]
            gap = c_hrs - d_hrs
            utilization = (d_hrs / c_hrs * 100) if c_hrs > 0 else 999.0
            risk = "Critical" if utilization > 115 else "High" if utilization > 100 else "Medium" if utilization > 85 else "Low"

            forecast_results.append({
                "date": date_str, "demand_hours": round(d_hrs, 1), "capacity_hours": round(c_hrs, 1),
                "gap_hours": round(gap, 1), "utilization_percent": round(utilization, 1), "risk_level": risk,
                "drivers": {k: round(v, 1) for k, v in demand_data["drivers"].items()}
            })

        forecast_results = sorted(forecast_results, key=lambda x: x["date"])
        weekly_summary = {"total_demand": round(sum(r["demand_hours"] for r in forecast_results), 1), "total_capacity": round(sum(r["capacity_hours"] for r in forecast_results), 1), "net_gap": round(sum(r["gap_hours"] for r in forecast_results), 1)}

        return jsonify({"forecast_results": forecast_results, "weekly_summary": weekly_summary})
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)