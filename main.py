import flet as ft
import math

def main(page: ft.Page):
    page.title = "Steel1 - Smart Lift Planner"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT

    # Kobelco RK250 Load Chart Data
    crane_database = {
        6.3: {
            "360": {
                9.32:  {3.0: 25.0, 4.0: 23.0, 5.0: 19.4, 6.0: 16.3},
                16.42: {5.0: 16.7, 8.0: 10.9, 10.0: 7.4, 12.0: 5.45},
                23.52: {6.0: 11.2, 10.0: 7.05, 14.0: 4.15, 16.0: 3.45},
                30.62: {8.0: 7.0, 12.0: 4.95, 16.0: 3.15, 20.0: 1.9, 24.0: 1.15}
            }
        },
        5.1: {
            "front": {
                9.32:  {3.0: 25.0, 4.0: 23.0, 5.0: 19.4, 6.0: 16.3},
                16.42: {5.0: 16.7, 8.0: 10.9, 10.0: 7.4, 12.0: 5.45},
                23.52: {6.0: 11.2, 10.0: 7.05, 14.0: 4.15, 16.0: 3.45},
                30.62: {8.0: 7.0, 12.0: 4.95, 16.0: 3.15, 20.0: 1.9, 24.0: 1.15}
            },
            "side": {
                9.32:  {3.0: 25.0, 4.0: 23.0, 5.0: 18.1, 6.0: 12.9},
                16.42: {5.0: 15.6, 8.0: 9.65, 10.0: 6.20, 12.0: 4.30},
                23.52: {6.0: 11.2, 10.0: 6.90, 14.0: 3.75, 16.0: 2.80},
                30.62: {8.0: 7.0, 12.0: 4.90, 16.0: 3.00, 20.0: 1.65, 24.0: 0.90}
            }
        }
    }

    single_line_pull = 3.5

    # Common Inputs
    outrigger_dd = ft.Dropdown(
        label="Outrigger အကျယ် (m)",
        options=[
            ft.dropdown.Option("6.3"),
            ft.dropdown.Option("5.1")
        ],
        value="6.3"
    )

    area_dd = ft.Dropdown(
        label="မချီမည့် ဧရိယာ",
        options=[
            ft.dropdown.Option("360"),
            ft.dropdown.Option("front"),
            ft.dropdown.Option("side")
        ],
        value="360"
    )

    parts_in = ft.TextField(
        label="ကြိုးအရေအတွက် (Parts of line)",
        value="4",
        keyboard_type=ft.KeyboardType.NUMBER
    )

    # Auto Planner Controls
    t1_rad = ft.TextField(
        label="လိုအပ်သော Radius (m)",
        keyboard_type=ft.KeyboardType.NUMBER
    )

    t1_load = ft.TextField(
        label="မချီမည့် ဝန် (တန်)",
        keyboard_type=ft.KeyboardType.NUMBER
    )

    t1_res = ft.Text(
        "",
        size=15,
        weight=ft.FontWeight.BOLD
    )

    # Manual Planner Controls
    t2_boom = ft.Dropdown(
        label="ထုတ်မည့် Boom အရှည် (m)",
        options=[
            ft.dropdown.Option("9.32"),
            ft.dropdown.Option("16.42"),
            ft.dropdown.Option("23.52"),
            ft.dropdown.Option("30.62")
        ],
        value="16.42"
    )

    t2_rad = ft.TextField(
        label="အကွာအဝေး Radius (m)",
        keyboard_type=ft.KeyboardType.NUMBER
    )

    t2_res = ft.Text(
        "",
        size=15,
        weight=ft.FontWeight.BOLD
    )

    # Radius interpolation
    def get_safe_rad_and_cap(capacities, rad):
        keys = sorted(capacities.keys())

        if rad in keys:
            return rad, capacities[rad]

        if rad < keys[0]:
            return keys[0], capacities[keys[0]]

        if rad > keys[-1]:
            return None, None

        for i in range(len(keys) - 1):
            r1, r2 = keys[i], keys[i + 1]

            if r1 < rad < r2:
                c1, c2 = capacities[r1], capacities[r2]

                interpolated_cap = c1 + (
                    (rad - r1) * (c2 - c1) / (r2 - r1)
                )

                return rad, round(interpolated_cap, 2)

        return None, None

    def check_errors():
        area_val = area_dd.value.lower()

        if outrigger_dd.value == "6.3" and area_val != "360":
            return "⚠️ Outrigger 6.3m တွင် '360' သာ ရွေးပါ။"

        if outrigger_dd.value == "5.1" and area_val == "360":
            return "⚠️ Outrigger 5.1m တွင် 'front' သို့မဟုတ် 'side' သာ ရွေးပါ။"

        return None

    def safe_angle(radius, boom):
        ratio = min(max(radius / boom, -1), 1)
        return math.degrees(math.acos(ratio))

    # Auto Planner
    def run_tab1(e):
        err = check_errors()

        if err:
            t1_res.value = err
            t1_res.color = "orange"
            page.update()
            return

        try:
            rad_val = float(t1_rad.value)
            load_val = float(t1_load.value)

            rope_cap = int(parts_in.value) * single_line_pull

            booms = crane_database[
                float(outrigger_dd.value)
            ][area_dd.value.lower()]

            found = False

            res_str = "📊 အလိုအလျောက် တွက်ချက်မှု:\n"
            res_str += "-" * 30 + "\n"

            for b_len, caps in booms.items():

                if rad_val < b_len:

                    calc_r, chart_c = get_safe_rad_and_cap(
                        caps,
                        rad_val
                    )

                    if calc_r is not None:

                        max_load = min(chart_c, rope_cap)

                        if max_load >= load_val:

                            found = True

                            ang = safe_angle(rad_val, b_len)

                            res_str += (
                                f"✅ Boom {b_len}m | {ang:.1f}°\n"
                                f"   မနိုင်ဝန်: {max_load} တန်\n\n"
                            )

            if not found:
                t1_res.value = "❌ ဤဝန်အတွက် ချီနိုင်သော Boom မရှိပါ။"
                t1_res.color = "red"

            else:
                t1_res.value = res_str
                t1_res.color = "green"

        except Exception:
            t1_res.value = "ဂဏန်းများကို မှန်ကန်စွာ ထည့်ပါ။"
            t1_res.color = "red"

        page.update()

    # Manual Planner
    def run_tab2(e):
        err = check_errors()

        if err:
            t2_res.value = err
            t2_res.color = "orange"
            page.update()
            return

        try:
            b_val = float(t2_boom.value)
            r_val = float(t2_rad.value)

            rope_cap = int(parts_in.value) * single_line_pull

            caps = crane_database[
                float(outrigger_dd.value)
            ][area_dd.value.lower()][b_val]

            if r_val >= b_val:
                t2_res.value = "❌ Radius သည် Boom ထက် မကြီးရပါ။"
                t2_res.color = "red"
                page.update()
                return

            calc_r, chart_c = get_safe_rad_and_cap(caps, r_val)

            if calc_r is None:
                t2_res.value = "❌ Radius လွန်နေပါသည်။"
                t2_res.color = "red"

            else:
                max_load = min(chart_c, rope_cap)

                ang = safe_angle(r_val, b_val)

                t2_res.value = (
                    f"📊 Boom {b_val}m တွက်ချက်မှု:\n"
                    + "-" * 30
                    + f"\n   ထောင့်: {ang:.1f}°"
                    + f"\n   မနိုင်ဝန်: {max_load} တန်"
                )

                t2_res.color = "green"

        except Exception:
            t2_res.value = "ဂဏန်းများကို မှန်ကန်စွာ ထည့်ပါ။"
            t2_res.color = "red"

        page.update()

    # Auto Layout
    auto_col = ft.Column(
        [
            ft.Text(
                "လိုချင်သော Radius နှင့် ဝန်ကို ထည့်ပါ-",
                italic=True
            ),

            t1_rad,
            t1_load,

            ft.ElevatedButton(
                "Boom ရှာမည်",
                on_click=run_tab1,
                bgcolor="blue",
                color="white"
            ),

            t1_res
        ],
        visible=True,
        spacing=15
    )

    # Manual Layout
    manual_col = ft.Column(
        [
            ft.Text(
                "ကိုယ်တိုင် Boom ရွေးပြီး တွက်ချက်ပါ-",
                italic=True
            ),

            t2_boom,
            t2_rad,

            ft.ElevatedButton(
                "တန်ချိန်တွက်မည်",
                on_click=run_tab2,
                bgcolor="green",
                color="white"
            ),

            t2_res
        ],
        visible=False,
        spacing=15
    )

    # Switch Auto
    def show_auto(e):
        auto_btn.bgcolor = "blue"
        auto_btn.color = "white"

        manual_btn.bgcolor = None
        manual_btn.color = "green"

        auto_col.visible = True
        manual_col.visible = False

        page.update()

    # Switch Manual
    def show_manual(e):
        auto_btn.bgcolor = None
        auto_btn.color = "blue"

        manual_btn.bgcolor = "green"
        manual_btn.color = "white"

        auto_col.visible = False
        manual_col.visible = True

        page.update()

    # Tab Buttons
    auto_btn = ft.ElevatedButton(
        "Auto Planner",
        on_click=show_auto,
        bgcolor="blue",
        color="white"
    )

    manual_btn = ft.OutlinedButton(
        "Manual Check",
        on_click=show_manual,
        color="green"
    )

    tab_row = ft.Row(
        [auto_btn, manual_btn],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    # Page Layout
    page.add(
        ft.Text(
            "Steel1 - Smart Planner",
            size=24,
            weight=ft.FontWeight.BOLD,
            color="blue"
        ),

        outrigger_dd,
        area_dd,
        parts_in,

        ft.Divider(),

        tab_row,

        ft.Divider(),

        auto_col,
        manual_col
    )

ft.app(target=main)
