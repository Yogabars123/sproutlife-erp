# 🎨 Sproutlife ERP — Professional Styling Guide

## What's Included

| File | Purpose |
|------|---------|
| `style.py` | **Core styling module** — all CSS + helper functions |
| `1_RM_Inventory.py` | Updated RM Inventory page (example integration) |
| `2_GRN_Data.py` | Updated GRN Data page (example integration) |

---

## Step 1 — Add `style.py` to your project root

Place `style.py` in the **same folder as your other `.py` pages** (or one level above and adjust the import path).

---

## Step 2 — Add these 3 lines to the TOP of EVERY page

```python
from style import apply_global_styles, stat_card, page_header, section_label

apply_global_styles()   # ← call this right after st.set_page_config()
```

---

## Step 3 — Replace your existing headers

Instead of:
```python
st.markdown("## 📦 RM Inventory")
st.markdown("Live raw material stock")
```

Use:
```python
page_header("📦", "RM Inventory", "Live raw material stock")
```

---

## Step 4 — Replace your stat/metric blocks

Instead of custom HTML stat cards, use:
```python
st.markdown(
    stat_card("Total QTY Available", "16,300,788", "2,414 records", "#1A56DB", "📦"),
    unsafe_allow_html=True
)
```

**Color guide:**
| Color | Use for |
|-------|---------|
| `#1A56DB` | Primary / neutral totals |
| `#16A34A` | Positive / received / in-stock |
| `#B45309` | Warning / pending / low stock |
| `#DC2626` | Danger / rejected / out of stock |

---

## Step 5 — Add section labels above filter rows

```python
section_label("Search & Filter")
```

---

## What the Styling Improves

- ✅ **Background** — Clean `#F8FAFC` slate-50 instead of Streamlit default grey
- ✅ **Sidebar** — White with subtle shadow, active page highlighted in blue
- ✅ **Typography** — DM Sans font (professional, modern, used by Notion/Linear)
- ✅ **Buttons** — Solid blue with hover lift effect
- ✅ **Inputs & Selects** — Soft border, focus ring on click
- ✅ **Tables** — Clean header, alternating row highlight on hover
- ✅ **KPI Cards** — Gradient with glow shadow, 4-column layout
- ✅ **Spacing** — Consistent padding and breathing room throughout
- ✅ **No Streamlit branding** — Footer and hamburger menu hidden

---

## Apply to All 7 Pages

Add these two lines to each of your pages:
```
1_RM_Inventory.py      ← done (example provided)
2_GRN_Data.py          ← done (example provided)
3_FG_Inventory.py      ← add the 3 lines
4_Consumption.py       ← add the 3 lines
5_Forecast.py          ← add the 3 lines
6_Replenishment.py     ← add the 3 lines
7_Consumption_vs_Forecast.py ← add the 3 lines
```
