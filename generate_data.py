import numpy as np, pandas as pd, datetime as dt
from openpyxl.styles import Font

rng = np.random.default_rng(42)
START = dt.date(2025, 1, 1)
END = dt.date(2026, 10, 31)          # last complete month (change to extend)

months = pd.period_range("2025-01", "2026-10", freq="M")
N_M = len(months)

# ---------------- Products ----------------
catalog = {
 "Home Decor": {"Candles & Holders": ["CANDLE HOLDER","LANTERN","TEA LIGHT SET","SCENTED CANDLE"],
                "Wall Art": ["WALL CLOCK","PICTURE FRAME","METAL SIGN","MIRROR"],
                "Cushions & Textiles": ["CUSHION COVER","THROW BLANKET","TABLE RUNNER"]},
 "Kitchen & Dining": {"Tableware": ["CERAMIC BOWL","DINNER PLATE","MUG","TEA CUP SET"],
                "Storage": ["BISCUIT TIN","STORAGE JAR","BREAD BIN"],
                "Cookware": ["COOKIE CUTTERS SET","BAKING TRAY","MIXING BOWL"]},
 "Garden & Outdoor": {"Planters": ["GARDEN POT","HANGING PLANTER","HERB PLANTER"],
                "Garden Tools": ["GARDEN TROWEL","SEED TRAY","WATERING CAN"]},
 "Stationery & Gifts": {"Stationery": ["NOTEBOOK","GREETING CARD SET","PENCIL CASE","WRAPPING PAPER"],
                "Gifts": ["TRINKET BOX","KEY RING","GIFT TAG SET","PHOTO ALBUM"]},
 "Bags & Accessories": {"Bags": ["SHOPPER BAG","LUNCH BAG","WASH BAG"],
                "Accessories": ["UMBRELLA","HOT WATER BOTTLE COVER","PURSE"]},
 "Seasonal": {"Christmas": ["CHRISTMAS TREE DECORATION","ADVENT CALENDAR","STOCKING","WREATH"],
              "Easter & Summer": ["EASTER EGG SET","PICNIC BASKET","BUNTING"]},
}
adjs = ["VINTAGE","RED SPOTTY","BLUE FLORAL","RETRO","PINK HEART","WOODLAND","SPACE","GREEN LEAF",
        "GOLD STAR","SCANDI","LONDON","BIRD","LAVENDER","STRIPED","CHERRY BLOSSOM","SKULLS"]
brands = ["HomeNest","Craftly","Bloomora","Urbanware","PaperTrail","Nordic Hue","Greenleaf Co","Giftopia"]
materials = ["Ceramic","Glass","Wood","Metal","Cotton","Paper","Plastic","Fabric"]
price_band = {"Home Decor":(3,30),"Kitchen & Dining":(2,22),"Garden & Outdoor":(3,35),
              "Stationery & Gifts":(0.8,12),"Bags & Accessories":(2.5,25),"Seasonal":(1.2,18)}
rows, seen = [], set()
code = 20000
for cat, subs in catalog.items():
    for sub, items in subs.items():
        for it in items:
            for _ in range(rng.integers(3, 6)):
                name = f"{rng.choice(adjs)} {it}"
                if name in seen: continue
                seen.add(name)
                code += int(rng.integers(1, 40))
                pc = str(code) + (rng.choice(["", "", "A", "B"]))
                lo, hi = price_band[cat]
                price = round(float(rng.uniform(lo, hi)) * 4) / 4 or 0.85
                rows.append([pc, name, round(max(price, 0.85), 2), cat, sub,
                             rng.choice(brands), rng.choice(materials)])
products = pd.DataFrame(rows, columns=["Product Code","Product","Price","Category","Subcategory","Brand","Material"])
products["pop"] = rng.pareto(1.6, len(products)) + 0.3
seasonal_cats = products["Subcategory"].eq("Christmas").values

# ---------------- Customers ----------------
countries = {"United Kingdom":("Europe",.52),"Germany":("Europe",.08),"France":("Europe",.07),
             "Netherlands":("Europe",.04),"Spain":("Europe",.03),"United States":("North America",.10),
             "Canada":("North America",.03),"Australia":("Oceania",.04),"India":("Asia",.04),
             "United Arab Emirates":("Asia",.03),"Singapore":("Asia",.02)}
first = ["Aarav","Olivia","Liam","Emma","Noah","Sophia","Mohammed","Isabella","Lucas","Mia","Arjun","Charlotte",
         "Ethan","Amelia","Priya","Oliver","Hannah","Jack","Zara","Leo","Chloe","Daniel","Anika","Sam","Grace"]
last = ["Smith","Patel","Jones","Brown","Taylor","Khan","Müller","Dubois","Garcia","Wilson","Reddy","Evans",
        "Clark","Singh","Walker","Hughes","Rossi","Nguyen","Lee","Thompson","Martin","Kumar","Davies","Wright"]
segments = ["Consumer","Corporate","Small Business"]
pay = ["Credit Card","Debit Card","PayPal","Apple Pay","Google Pay","Bank Transfer"]

# monthly new-customer volumes: growth trend + seasonality (Q4 peak) + noise
season = np.array([.9,.85,.95,.95,1.0,.95,.9,.95,1.05,1.2,1.4,1.3] * 2)[:N_M]
trend = np.linspace(190, 300, N_M)
acq = (trend * season * rng.normal(1, .05, N_M)).astype(int)
cust_rows = []
cid = 10001
acq_month = []
cnames, cprobs = list(countries), np.array([v[1] for v in countries.values()])
cprobs = cprobs / cprobs.sum()
for mi, n in enumerate(acq):
    for _ in range(n):
        c = rng.choice(cnames, p=cprobs)
        cust_rows.append([cid, c, f"{rng.choice(first)} {rng.choice(last)}", countries[c][0],
                          rng.choice(segments, p=[.68,.12,.20]), rng.choice(pay, p=[.28,.2,.2,.14,.1,.08])])
        acq_month.append(mi); cid += 1
customers = pd.DataFrame(cust_rows, columns=["Customer ID","Country","Customer Name","Region",
                                             "Customer Segment","Preferred Payment Method"])
customers["_acq"] = acq_month
# per-customer loyalty (heavy-tailed -> realistic retention curve)
seg_boost = customers["Customer Segment"].map({"Consumer":1.0,"Corporate":1.5,"Small Business":1.25}).values
loyalty = np.clip(rng.beta(1.1, 3.0, len(customers)) * 2.2 * seg_boost, 0, 1)

# ---------------- Sales ----------------
sales = []
inv = 600000
month_season = {1:.85,2:.85,3:.95,4:.95,5:1,6:.95,7:.9,8:.9,9:1.05,10:1.2,11:1.5,12:1.4}
pops = products["pop"].values
for i, row in customers.iterrows():
    a = row["_acq"]
    for k in range(0, N_M - a):
        m = months[a + k]
        if k == 0:
            active = True
        else:
            p = loyalty[i] * (0.15 + 0.85 * np.exp(-k / 3.0)) * month_season[m.month] * 0.5
            active = rng.random() < min(p, .95)
        if not active: continue
        n_inv = 1 + (rng.random() < .22) + (rng.random() < .06)
        for _ in range(n_inv):
            day = int(rng.integers(1, m.days_in_month + 1))
            d = dt.date(m.year, m.month, day)
            if d > END: continue
            inv += int(rng.integers(1, 4))
            n_lines = int(np.clip(rng.poisson(4.5) + 1, 1, 14))
            w = pops.copy()
            if m.month in (10, 11, 12): w = np.where(seasonal_cats, w * 6, w)
            else: w = np.where(seasonal_cats, w * .08, w)
            w = w / w.sum()
            idx = rng.choice(len(products), size=min(n_lines, len(products)), replace=False, p=w)
            mult = 4 if row["Customer Segment"] == "Corporate" else 1
            for j in idx:
                q = int(np.clip(rng.geometric(.45), 1, 12) * (rng.integers(1, 4) if mult > 1 else 1))
                sales.append((row["Customer ID"], q, str(inv), d, products.iloc[j]["Product Code"]))
sales = pd.DataFrame(sales, columns=["Customer ID","Quantity","Invoice","Date","Product Code"])
sales = sales.sort_values(["Date","Invoice"]).reset_index(drop=True)

customers = customers.drop(columns="_acq")
products = products.drop(columns="pop")
# drop customers with no sales (none expected) and report
print("customers", len(customers), "products", len(products), "sales rows", len(sales),
      "invoices", sales.Invoice.nunique(), sales.Date.min(), sales.Date.max())
rev = sales.merge(products[["Product Code","Price"]], on="Product Code")
rev["amt"] = rev.Quantity * rev.Price
print("total sales", round(rev.amt.sum()))
sales["Date"] = pd.to_datetime(sales["Date"])
first_m = sales.groupby("Customer ID").Date.min().dt.to_period("M")
sales["ci"] = (sales.Date.dt.to_period("M") - sales["Customer ID"].map(first_m)).apply(lambda x: x.n)
ret = sales.groupby("ci")["Customer ID"].nunique()
print("retention by month idx (avg active / m0 size approx):")
print((ret / ret.iloc[0]).round(3).head(10).to_dict())

import os
pass
sales["Date"] = sales["Date"].dt.date
sales = sales.drop(columns="ci")
out = "Cohort_Sales_Data_2025_2026.xlsx"
with pd.ExcelWriter(out, engine="openpyxl", datetime_format="yyyy-mm-dd", date_format="yyyy-mm-dd") as xw:
    customers.to_excel(xw, sheet_name="Customers", index=False)
    products.to_excel(xw, sheet_name="Products", index=False)
    sales.to_excel(xw, sheet_name="Sales", index=False)
    for ws in xw.book.worksheets:
        for c in ws[1]:
            c.font = Font(bold=True, name="Arial")
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = max(12, min(34, len(str(col[0].value)) + 6))
        ws.freeze_panes = "A2"
print("saved")
