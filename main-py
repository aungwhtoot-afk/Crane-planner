Import flet as ft
import math

def main(page: ft.Page):
    page.title = "Steel1 - Crane Planner"
    page.scroll = "auto" 
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # ဇယား အချက်အလက်များ
    crane_database = {
        6.3: {
            "360": {
                9.5:  {3.0: 25.0, 4.0: 23.0, 5.0: 19.4, 6.0: 16.3},
                16.6: {5.0: 16.7, 8.0: 10.9, 10.0: 7.4, 12.0: 5.45},
                23.52: {6.0: 11.2, 10.0: 7.05, 14.0: 4.15, 16.0: 3.45},
                30.62: {8.0: 7.0, 12.0: 4.95, 16.0: 3.15, 20.0: 1.9, 24.0: 1.15}
            }
        },
        5.1: {
            "front": {
                9.5:  {3.0: 25.0, 4.0: 23.0, 5.0: 19.4, 6.0: 16.3},
                16.6: {5.0: 16.7, 8.0: 10.9, 10.0: 7.4, 12.0: 5.45},
                23.52: {6.0: 11.2, 10.0: 7.05, 14.0: 4.15, 16.0: 3.45},
                30.62: {8.0: 7.0, 12.0: 4.95, 16.0: 3.15, 20.0: 1.9, 24.0: 1.15}
            },
            "side": {
                9.5:  {3.0: 25.0, 4.0: 23.0, 5.0: 18.1, 6.0: 12.9},
                16.6: {5.0: 15.6, 8.0: 9.65, 10.0: 6.20, 12.0: 4.30},
                23.52: {6.0: 11.2, 10.0: 6.90, 14.0: 3.75, 16.0: 2.80},
                30.62: {8.0: 7.0, 12.0: 4.90, 16.0: 3.00, 20.0: 1.65, 24.0: 0.90}
            }
        }
    }
    single_line_pull = 3.5
    
    # အခြေခံ ထည့်သွင်းရန် အကွက်များ
    outrigger_dd = ft.Dropdown(label="Outrigger (m)", options=[ft.dropdown.Option("6.3"), ft.dropdown.Option("5.1")], value="6.3")
    area_dd = ft.Dropdown(label="အလုပ်လုပ်မည့် ဧရိယာ", options=[ft.dropdown.Option("360"), ft.dropdown.Option("front"), ft.dropdown.Option("side")], value="360")
    parts_in = ft.TextField(label="ကြိုးအရေအတွက် (Parts)", value="4", keyboard_type="number")
    
    # Auto အတွက် အကွက်များ
    t1_rad = ft.TextField(label="လိုအပ်သော Radius (m)", keyboard_type="number")
    t1_load = ft.TextField(label="မချီမည့် ဝန် (တန်)", keyboard_type="number")
    t1_res = ft.Text("", size=15, weight="bold")
    
    # Manual အတွက် အကွက်များ
    t2_boom = ft.Dropdown(label="Boom အရှည် (m)", options=[ft.dropdown.Option("9.5"), ft.dropdown.Option("16.6"), ft.dropdown.Option("23.52"), ft.dropdown.Option("30.62")], value="16.6")
    t2_rad = ft.TextField(label="အကွာအဝေး Radius (m)", keyboard_type="number")
    t2_res = ft.Text("", size=15, weight="bold")

    def check_errors():
        out_val = float(outrigger_dd.value)
        area_val = area_dd.value.lower()
        if out_val == 6.3 and area_val != "360":
            return "⚠️ Outrigger 6.3m တွင် '360' သာ ရွေးပါ။"
        if out_val == 5.1 and area_val == "360":
            return "⚠️ Outrigger 5.1m တွင် 'front' သို့မဟုတ် 'side' သာ ရွေးပါ။"
        return None

    def get_safe_rad_and_cap(capacities, rad):
        for r in sorted(capacities.keys()):
            if r >= rad:
                return r, capacities[r]
        return None, None

    def run_tab1(e):
        err = check_errors()
        if err:
            t1_res.value, t1_res.color = err, "orange"
            page.update()
            return
        try:
            rad_val = float(t1_rad.value)
            load_val = float(t1_load.value)
            rope_cap = int(parts_in.value) * single_line_pull
            booms = crane_database[float(outrigger_dd.value)][area_dd.value.lower()]
            found = False
            res_str = "📊 အကောင်းဆုံး Boom ရလဒ်:\n" + "-"*30 + "\n"
            
            for boom_len, caps in booms.items():
                if rad_val < boom_len:
                    safe_r, chart_c = get_safe_rad_and_cap(caps, rad_val)
                    if safe_r is not None:
                        max_load = min(chart_c, rope_cap)
                        if max_load >= load_val:
                            found = True
                            ang = math.degrees(math.acos(rad_val / boom_len))
                            res_str += f"✅ Boom {boom_len}m ဖြင့် ချီနိုင်ပါသည်။\n"
                            res_str += f"   ထောင့် {ang:.1f}° | အများဆုံးဝန် {max_load} တန်\n\n"
            
            if not found:
                t1_res.value, t1_res.color = "❌ ဤဝန်အတွက် ဘေးကင်းသော Boom မရှိပါ။", "red"
            else:
                t1_res.value, t1_res.color = res_str, "green"
        except Exception:
            t1_res.value, t1_res.color = "ဂဏန်းများကို ပြည့်စုံမှန်ကန်စွာ ထည့်ပါ။", "red"
        page.update()

    def run_tab2(e):
        err = check_errors()
        if err:
            t2_res.value, t2_res.color = err, "orange"
            page.update()
            return
        try:
            boom_val = float(t2_boom.value)
            rad_val = float(t2_rad.value)
            rope_cap = int(parts_in.value) * single_line_pull
            caps = crane_database[float(outrigger_dd.value)][area_dd.value.lower()][boom_val]
            if rad_val >= boom_val:
                t2_res.value, t2_res.color = "❌ Radius သည် Boom အရှည်ထက် မကြီးရပါ။", "red"
                page.update()
                return
            safe_r, chart_c = get_safe_rad_and_cap(caps, rad_val)
            if safe_r is None:
                t2_res.value, t2_res.color = "❌ Radius လွန်နေပါသည်။", "red"
            else:
                max_load = min(chart_c, rope_cap)
                ang = math.degrees(math.acos(rad_val / boom_val))
                res_str = f"📊 Boom {boom_val}m တွင် တွက်ချက်မှု:\n" + "-"*30 + "\n"
                res_str += f"   - မြှင့်ရမည့်ထောင့်: {ang:.1f}°\n"
                res_str += f"   - အများဆုံး ဝန်: {max_load} တန်\n"
                t2_res.value, t2_res.color = res_str, "green"
        except Exception:
            t2_res.value, t2_res.color = "ဂဏန်းများကို ပြည့်စုံမှန်ကန်စွာ ထည့်ပါ။", "red"
        page.update()

    # --- Mode အရ ပေါ်မည့် အကွက်များ ---
    auto_col = ft.Column([t1_rad, t1_load, ft.ElevatedButton("အကောင်းဆုံး Boom ရှာရန်", on_click=run_tab1, bgcolor="blue", color="white"), t1_res], visible=True)
    manual_col = ft.Column([t2_boom, t2_rad, ft.ElevatedButton("တွက်ချက်မည်", on_click=run_tab2, bgcolor="green", color="white"), t2_res], visible=False)

    def mode_changed(e):
        if mode_dd.value == "Auto (အလိုအလျောက် ရှာရန်)":
            auto_col.visible = True
            manual_col.visible = False
        else:
            auto_col.visible = False
            manual_col.visible = True
        page.update()

    # Tab အစားထိုး Dropdown
    mode_dd = ft.Dropdown(
        label="တွက်ချက်မည့်ပုံစံ ရွေးချယ်ပါ",
        options=[
            ft.dropdown.Option("Auto (အလိုအလျောက် ရှာရန်)"),
            ft.dropdown.Option("Manual (ကိုယ်တိုင် Boom ရွေးရန်)")
        ],
        value="Auto (အလိုအလျောက် ရှာရန်)",
        on_change=mode_changed,
        border_color="blue"
    )

    page.add(
        ft.Text("Steel1 - Crane Planner", size=24, weight="bold", color="blue"),
        outrigger_dd, 
        area_dd, 
        parts_in, 
        ft.Divider(),
        mode_dd, # ဒီနေရာကနေ Auto/Manual ရွေးရပါမယ်
        ft.Divider(),
        auto_col,
        manual_col
    )

ft.app(target=main)

