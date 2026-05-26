import flet as ft
import math

def main(page: ft.Page):
    page.title = "Steel1 - Kobelco RK250-5 Crane Calculator"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 550
    page.window_height = 850

    # Crane Database
    crane_database = {
        6.3: {"360": {9.32: {3:25,4:23,5:19.4,6:16.3}, 16.42: {5:16.7,8:10.9,10:7.4,12:5.45}, 23.52: {6:11.2,10:7.05,14:4.15,16:3.45}, 30.62: {8:7,12:4.95,16:3.15,20:1.9,24:1.15}}},
        5.1: {"side": {9.32: {3:25,4:23,5:18.1,6:12.9}, 16.42: {5:15.6,8:9.65,10:6.2,12:4.3}, 23.52: {6:11.2,10:6.9,14:3.75,16:2.8}, 30.62: {8:7,12:4.9,16:3,20:1.65,24:0.9}}, "front": {9.32: {3:25,4:23,5:19.4,6:16.3}, 16.42: {5:16.7,8:10.9,10:7.4,12:5.45}, 23.52: {6:11.2,10:7.05,14:4.15,16:3.45}, 30.62: {8:7,12:4.95,16:3.15,20:1.9,24:1.15}}},
        3.8: {"side": {9.32: {3:25,4:23,5:16.3,6:12}, 16.42: {5:12.5,8:8.5,10:5.8,12:4.2}, 23.52: {6:9.5,10:6,14:3.2,16:2.5}, 30.62: {8:6,12:4,16:2.4,20:1.5}}}
    }

    single_line_pull = 3.5
    boom_pivot_height = 1.5

    # ========== NEW: Radius Error Analysis ==========
    def calculate_capacity_at_radius(out_val, direction, boom_len, radius, rope_cap):
        """Return capacity at given radius"""
        if out_val not in crane_database or direction not in crane_database[out_val]:
            return None
        if boom_len not in crane_database[out_val][direction]:
            return None
        
        caps = crane_database[out_val][direction][boom_len]
        radii = sorted(caps.keys())
        
        # Find capacity at or just beyond radius
        for i, r in enumerate(radii):
            if r >= radius:
                return caps[r]
            # Interpolate between radii
            if i < len(radii) - 1 and radii[i] < radius < radii[i+1]:
                r1, r2 = radii[i], radii[i+1]
                c1, c2 = caps[r1], caps[r2]
                interp = c1 + (c2 - c1) * (radius - r1) / (r2 - r1)
                return interp
        return None

    def analyze_radius_change(e):
        try:
            out_val = float(radius_analysis_out.value.split()[0])
            direction = radius_analysis_dir.value
            
            if out_val == 6.3:
                direction = "360"
            elif direction == "360":
                direction = "side"
            
            boom_len = float(radius_analysis_boom.value)
            base_radius = float(radius_analysis_base.value)
            rope_cap = int(radius_analysis_parts.value) * single_line_pull
            
            # Get capacity at base radius
            base_cap = calculate_capacity_at_radius(out_val, direction, boom_len, base_radius, rope_cap)
            
            if base_cap is None:
                analysis_result.value = f"❌ Radius {base_radius}m အတွက် ဒေတာမရှိပါ"
                analysis_result.color = "red"
                page.update()
                return
            
            # Calculate capacities at +1m, +2m, +3m
            results = []
            loss_per_meter = []
            
            for i in range(1, 4):
                new_radius = base_radius + i
                new_cap = calculate_capacity_at_radius(out_val, direction, boom_len, new_radius, rope_cap)
                
                if new_cap is not None:
                    loss = base_cap - new_cap
                    loss_pct = (loss / base_cap) * 100
                    loss_per_meter.append(loss_pct / i)
                    results.append({
                        "radius": new_radius,
                        "capacity": new_cap,
                        "loss": loss,
                        "loss_pct": loss_pct
                    })
            
            # Build result message
            res_text = f"📊 Boom {boom_len}m | {out_val}m Outrigger | {direction}\n"
            res_text += "=" * 40 + "\n"
            res_text += f"✅ Base Radius: {base_radius}m → {base_cap:.2f} တန်\n\n"
            
            res_text += "📉 Radius တိုးလာတိုင်း ကျဆင်းမှု:\n"
            for r in results:
                res_text += f"   • {r['radius']}m → {r['capacity']:.2f} တန် (လျော့ {r['loss']:.2f}တန် / {r['loss_pct']:.1f}%)\n"
            
            # Average loss per meter
            if loss_per_meter:
                avg_loss_pct = sum(loss_per_meter) / len(loss_per_meter)
                res_text += f"\n⚠️ ပျမ်းမျှအားဖြင့် Radius 1m တိုးတိုင်း {avg_loss_pct:.1f}% ကျဆင်းသည်။\n"
            
            # Warning for high radius
            if base_radius > 15:
                res_text += "\n🔴 သတိပေးချက်: Radius ကြီးလွန်းပါက ကရိန် မှောက်ကျနိုင်သည်။"
            elif base_radius > 12:
                res_text += "\n🟡 သတိပေးချက်: Radius အတော်ကြီးနေပြီ။ ဂရုစိုက်ပါ။"
            
            analysis_result.value = res_text
            analysis_result.color = "blue"
            
        except ValueError:
            analysis_result.value = "ဂဏန်းများကို မှန်ကန်စွာ ထည့်ပါ"
            analysis_result.color = "red"
        except Exception as ex:
            analysis_result.value = f"Error: {str(ex)}"
            analysis_result.color = "red"
        
        page.update()

    # Radius Analysis Inputs
    radius_analysis_out = ft.Dropdown(
        label="Outrigger အကျယ်",
        options=[ft.dropdown.Option("6.3m (360°)"), ft.dropdown.Option("5.1m (side)"), ft.dropdown.Option("3.8m (side)")],
        value="6.3m (360°)",
        width=400
    )
    
    radius_analysis_dir = ft.Dropdown(
        label="ဦးတည်ရာ",
        options=[ft.dropdown.Option("side"), ft.dropdown.Option("front"), ft.dropdown.Option("360")],
        value="360",
        width=400
    )
    
    radius_analysis_boom = ft.Dropdown(
        label="Boom အရှည် (m)",
        options=[ft.dropdown.Option("9.32"), ft.dropdown.Option("16.42"), ft.dropdown.Option("23.52"), ft.dropdown.Option("30.62")],
        value="16.42",
        width=400
    )
    
    radius_analysis_base = ft.TextField(
        label="စတင် Radius (m)",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=400
    )
    
    radius_analysis_parts = ft.TextField(
        label="Parts of line",
        value="4",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=400
    )
    
    analyze_btn = ft.ElevatedButton(
        "Radius 1m တိုးတိုင်း တွက်မည်",
        on_click=analyze_radius_change,
        bgcolor="red",
        color="white",
        width=400
    )
    
    analysis_result = ft.Text("", size=14, selectable=True)

    # Update direction options based on outrigger
    def update_dir_options(e):
        if "6.3" in radius_analysis_out.value:
            radius_analysis_dir.options = [ft.dropdown.Option("360")]
            radius_analysis_dir.value = "360"
            radius_analysis_dir.disabled = True
        else:
            radius_analysis_dir.options = [ft.dropdown.Option("side"), ft.dropdown.Option("front")]
            radius_analysis_dir.value = "side"
            radius_analysis_dir.disabled = False
        page.update()
    
    radius_analysis_out.on_change = update_dir_options
    update_dir_options(None)

    # ========== TAB 2: Safe Radius Finder (Prevents Error) ==========
    safe_radius_out = ft.Dropdown(
        label="Outrigger အကျယ်",
        options=[ft.dropdown.Option("6.3m (360°)"), ft.dropdown.Option("5.1m (side)"), ft.dropdown.Option("5.1m (front)"), ft.dropdown.Option("3.8m (side)")],
        value="6.3m (360°)",
        width=400
    )
    
    safe_radius_boom = ft.Dropdown(
        label="Boom အရှည် (m)",
        options=[ft.dropdown.Option("9.32"), ft.dropdown.Option("16.42"), ft.dropdown.Option("23.52"), ft.dropdown.Option("30.62")],
        value="16.42",
        width=400
    )
    
    safe_radius_load = ft.TextField(
        label="မချီမည့် ဝန် (တန်)",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=400
    )
    
    safe_radius_parts = ft.TextField(label="Parts of line", value="4", keyboard_type=ft.KeyboardType.NUMBER, width=400)
    safe_result = ft.Text("", size=14)
    
    def find_safe_radius(e):
        try:
            load = float(safe_radius_load.value)
            out_str = safe_radius_out.value
            boom_len = float(safe_radius_boom.value)
            rope_cap = int(safe_radius_parts.value) * single_line_pull
            
            if "6.3" in out_str:
                out_val, direction = 6.3, "360"
            elif "5.1" in out_str:
                out_val = 5.1
                direction = "side" if "side" in out_str else "front"
            else:
                out_val, direction = 3.8, "side"
            
            if out_val not in crane_database or direction not in crane_database[out_val]:
                safe_result.value = "ဒေတာမရှိပါ"
                safe_result.color = "red"
                page.update()
                return
            
            if boom_len not in crane_database[out_val][direction]:
                safe_result.value = f"Boom {boom_len}m အတွက် ဒေတာမရှိပါ"
                safe_result.color = "red"
                page.update()
                return
            
            caps = crane_database[out_val][direction][boom_len]
            radii = sorted(caps.keys())
            
            # Find maximum safe radius
            safe_radius = None
            max_cap = None
            
            for i, r in enumerate(radii):
                cap = min(caps[r], rope_cap)
                if cap >= load:
                    safe_radius = r
                    max_cap = cap
                else:
                    break
            
            if safe_radius:
                # Calculate next radius loss
                next_radius = radii[radii.index(safe_radius) + 1] if radii.index(safe_radius) + 1 < len(radii) else safe_radius + 1
                next_cap = caps.get(next_radius, 0)
                loss = max_cap - next_cap if next_cap else 0
                
                safe_result.value = f"✅ {load} တန် ချီရန် အများဆုံး Radius: {safe_radius}m\n"
                safe_result.value += f"   Boom {boom_len}m တွင် မနိုင်ဝန်: {max_cap:.2f} တန်\n"
                safe_result.value += f"   ⚠️ {safe_radius+1}m သွားလျှင် {loss:.2f} တန် ကျမည်"
                safe_result.color = "green"
            else:
                safe_result.value = f"❌ Boom {boom_len}m ဖြင့် {load} တန် မချီနိုင်ပါ။\n   ပိုရှည်သော Boom သုံးပါ သို့မဟုတ် ဝန်လျှော့ပါ။"
                safe_result.color = "red"
                
        except ValueError:
            safe_result.value = "ဝန်အား ထည့်ပါ"
            safe_result.color = "red"
        page.update()
    
    safe_btn = ft.ElevatedButton("အများဆုံး Radius ရှာမည်", on_click=find_safe_radius, bgcolor="green", color="white", width=400)

    # Tabs
    tab1 = ft.Container(
        content=ft.Column([
            ft.Text("📐 Radius တိုးလာတိုင်း တန်ချိန်ကျဆင်းနှုန်း", size=16, weight=ft.FontWeight.BOLD),
            radius_analysis_out, radius_analysis_dir, radius_analysis_boom, 
            radius_analysis_base, radius_analysis_parts, analyze_btn, 
            ft.Divider(), analysis_result
        ], spacing=15),
        padding=15
    )
    
    tab2 = ft.Container(
        content=ft.Column([
            ft.Text("🛡️ ဝန်အတွက် အများဆုံး အန္တရာယ်ကင်း Radius", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("သတ်မှတ်ဝန်အတွက် ဘယ်Radiusအထိ အန္တရာယ်ကင်းစွာ ချီနိုင်လဲ", italic=True, size=12),
            safe_radius_out, safe_radius_boom, safe_radius_load, safe_radius_parts, safe_btn, safe_result
        ], spacing=15),
        padding=15
    )
    
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="📉 Radius vs Capacity", content=tab1),
            ft.Tab(text="🛡️ Safe Radius Finder", content=tab2),
        ],
        expand=True
    )
    
    page.add(
        ft.Text("Steel1 - Kobelco RK250-5", size=22, weight=ft.FontWeight.BOLD, color="blue"),
        ft.Text("Radius Error Analysis & Safe Zone Calculator", size=14, italic=True),
        ft.Divider(),
        tabs
    )

ft.app(target=main)
