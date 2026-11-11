# 📊 Cohort Sales Analysis Dashboard (Power BI)

> **Are the customers we acquired still buying?**
> An end-to-end Power BI project that turns raw transactions into a cohort retention dashboard: data model, DAX, and interactive visuals.

<p align="center">
  <a href="https://app.powerbi.com/links/xmq-_qndGL?ctid=d8951f7f-6451-4c56-9e5f-2ad53476f070&pbi_source=linkShare">
    <img src="images/dashboard-overview.png" alt="Cohort Analysis Dashboard" width="900">
  </a>
</p>

<p align="center">
  <a href="https://app.powerbi.com/links/xmq-_qndGL?ctid=d8951f7f-6451-4c56-9e5f-2ad53476f070&pbi_source=linkShare"><b>🔗 View the Live Dashboard</b></a>
  &nbsp;|&nbsp;
</p>

---

## 📌 Table of Contents

1. [Project Overview](#-project-overview)
2. [What Is a Cohort Analysis?](#-what-is-a-cohort-analysis)
3. [Dashboard Features](#-dashboard-features)
4. [Key Insights](#-key-insights)
5. [Tech Stack](#-tech-stack)
6. [Dataset](#-dataset)
7. [Data Model](#-data-model)
8. [How It Was Built (Step by Step)](#-how-it-was-built-step-by-step)
9. [DAX Measures Explained](#-dax-measures-explained)
10. [Visual Design Notes](#-visual-design-notes)
11. [Validation Checks](#-validation-checks)
12. [Repository Structure](#-repository-structure)
13. [How to Run It Locally](#-how-to-run-it-locally)
14. [What I Learned](#-what-i-learned)
15. [Credits and Disclaimer](#-credits-and-disclaimer)
16. [Contact](#-contact)

---

## 🎯 Project Overview

A normal sales dashboard says *how many* customers you have. A cohort dashboard says *whether they stay*.

This project analyses **customer retention and revenue by acquisition month** for **January 2025 to October 2026**. It answers questions such as:

- How many new customers do we acquire each month, and how does that compare with last year?
- Of the customers who joined in a given month, how many are still buying 1, 2, 3 … 21 months later?
- Which cohorts are the most valuable over their lifetime?
- Where does retention drop off, and when?

| Item | Detail |
|---|---|
| **Period** | Jan 2025 – Oct 2026 (22 months) |
| **Customers** | ~5,500 |
| **Products** | 162 across 6 categories and 8 brands |
| **Sales lines** | ~75,000 across ~13,600 invoices |
| **Total sales** | ≈ $2.5M |
| **Tool** | Power BI (DAX, Power Query, HTML/SVG-in-DAX) |

---

## 🧠 What Is a Cohort Analysis?

A **cohort** is a group of customers who made their **first purchase in the same month**. The Jan-2025 cohort is everyone who bought for the first time in January 2025.

The cohort matrix then follows each group over time:

```
Cohort      Month 0   Month 1   Month 2   Month 3  ...
Jan-2025      171        30        19        22
Feb-2025      173        41        35        20
```

- **Month 0** = the month of first purchase. It is always the full size of the cohort.
- **Month 1** = the number of those customers who bought again the next month, and so on.
- Dividing each cell by the Month 0 value gives **retention %**.

This view separates *new* customers from *returning* ones, which an ordinary total hides.

---

## ✨ Dashboard Features

| Feature | Description |
|---|---|
| **Cohort matrix heatmap** | Rows are acquisition months, columns are months since first purchase (0–21). Month 0 is shaded grey and later months in a purple heat scale. The selected month's row is highlighted in blue. |
| **Dynamic "Cohort for" switch** | One matrix, five metrics: Cohort Customers, Customer Retention %, Customer Churn %, Customer Revenue, Customer Lifetime Revenue. |
| **Unit switch** | Shows revenue as None, K or M. |
| **KPI cards** | Active Customers, Acquired Customers, Avg. Customers Retained and Total Sales, each with absolute and % change vs last year. Built in DAX and rendered as HTML. |
| **Customers Acquired chart** | Monthly new-customer area chart with a **dynamic title** that calculates the yearly average, the prior-year average and the variance. |
| **CY vs PY cohort trend** | Compares the selected month's cohort with the same month a year earlier, across months since first purchase. |
| **Slicers** | Month, Customer Country, Customer Segment, Brand, Product Category. |

---

## 🔍 Key Insights

> These come from synthetic data, so they illustrate how to read the dashboard, not real business findings.

- **Acquisition is growing:** average new customers per month rose from **235 (2025) to 272 (2026), about +16%**.
- **Retention drops fast:** only about **one in five customers buys again in month 1**, so the first 30 days are where retention is won or lost.
- **Seasonality matters:** the **Nov-2025 cohort was the largest (369 customers)** and retained best in month 1 (~35%), in line with a Q4 gift-buying effect.
- **Lifetime value builds slowly:** cumulative revenue per cohort keeps rising after month 6 even as the active count falls, because a small loyal group keeps buying.

---

## 🛠 Tech Stack

| Layer | Tool |
|---|---|
| Visualisation and modelling | **Power BI Desktop** |
| Calculations | **DAX** |
| Data loading | **Power Query** |
| Synthetic data | **Python** (pandas, numpy, openpyxl) |
| Custom visual | **HTML Content** (KPI cards) |
| Version control | **Git / GitHub** |

---

## 🗂 Dataset

The dataset is **synthetic**. It was generated by `generate_data.py` to mimic real retail behaviour, so no real customer or company data is involved.

### Tables

| Table | Rows | Columns |
|---|---|---|
| **Customers** | ~5,500 | Customer ID, Country, Customer Name, Region, Customer Segment, Preferred Payment Method |
| **Products** | 162 | Product Code, Product, Price, Category, Subcategory, Brand, Material |
| **Sales** | ~75,000 | Customer ID, Quantity, Invoice, Date, Product Code |

### Realism built into the generator

- **Growing acquisition:** new customers per month trend upward from ~190 to ~300.
- **Seasonality:** Q4 has more new customers and more orders, and Christmas products sell mostly in Oct–Dec.
- **Realistic retention curve:** about 22% of a cohort returns in month 1, falling to about 5% by month 6, with a long tail of loyal buyers. Corporate and Small Business customers retain better than Consumers.
- **Mixed baskets:** invoices contain 1–14 product lines, and Corporate customers buy larger quantities.
- **Price lives in the Products table only**, as in many real systems, so sales value is calculated as `Quantity × Price`.

To regenerate or extend the data (for example through Dec 2026), edit `END` in `generate_data.py` and run it.

---

## 🧩 Data Model

A **star schema**: one fact table (`Sales`) and three dimensions, plus helper tables.

```
Customers (1) ───► (*) Sales (*) ◄─── (1) Products
                          ▲
                          │ (*:1)
                        Date  (marked as date table)

Disconnected helper tables (no relationships):
  Month Index  → matrix columns 0–23
  Cohort For   → "Cohort for" dropdown
  Unit         → K / M dropdown
  Date Axis    → month axis for the acquisition chart
```

### Why disconnected tables?

- **Month Index** supplies the matrix columns 0, 1, 2 … without filtering Sales by itself. Measures apply the number deliberately.
- **Cohort For** and **Unit** are *selectors*. They hold labels that a `SWITCH` measure reads.
- **Date Axis** gives the acquisition chart a month axis that the month slicer does **not** filter, so the chart always shows the full timeline.

---

## 🧱 How It Was Built (Step by Step)

### Step 1: Generate the data
Run `generate_data.py` to create `Cohort_Sales_Data_2025_2026.xlsx` with the `Customers`, `Products` and `Sales` sheets.

### Step 2: Load into Power BI
1. **Get Data → Excel** and select all three sheets.
2. In **Power Query**, set types: `Date` = Date, `Quantity` = Whole number, `Price` = Fixed decimal, `Customer ID` and `Product Code` = **Text** (some product codes contain letters).
3. **Close & Apply**.

### Step 3: Build the Date table and relationships
```DAX
Date =
ADDCOLUMNS(
    CALENDAR(DATE(2025,1,1), DATE(2026,12,31)),
    "Year", YEAR([Date]),
    "Month Start", DATE(YEAR([Date]), MONTH([Date]), 1),
    "Month Label", FORMAT([Date], "MMM-yyyy"),
    "Month Sort", YEAR([Date]) * 100 + MONTH([Date])
)
```
- Mark it as the **date table**, and sort `Month Label` by `Month Sort`.
- Create one-to-many, single-direction relationships: `Customers[Customer ID] → Sales`, `Products[Product Code] → Sales`, `Date[Date] → Sales[Date]`.

### Step 4: Add the cohort columns

**Customers table**
```DAX
First Purchase Date = CALCULATE(MIN(Sales[Date]))
Cohort Month = DATE(YEAR(Customers[First Purchase Date]), MONTH(Customers[First Purchase Date]), 1)
Cohort Label = FORMAT(Customers[Cohort Month], "MMM-yyyy")   -- sort by Cohort Month
```

**Sales table**
```DAX
Sales Amount = Sales[Quantity] * RELATED(Products[Price])
Cohort Month = RELATED(Customers[Cohort Month])
Months Since First Purchase =
(YEAR(Sales[Date]) - YEAR(Sales[Cohort Month])) * 12
    + MONTH(Sales[Date]) - MONTH(Sales[Cohort Month])
```

These two ideas power the whole project: **every customer has a cohort month**, and **every sale knows how many months after the first purchase it happened**.

### Step 5: Create the helper tables
```DAX
Month Index = SELECTCOLUMNS(GENERATESERIES(0, 23, 1), "Index", [Value])

Cohort For =
DATATABLE("Metric", STRING, "Sort", INTEGER,
    {{"Cohort Customers",1},{"Customer Retention %",2},{"Customer Churn %",3},
     {"Customer Revenue",4},{"Customer Life Time Revenue",5}})

Unit =
DATATABLE("Unit", STRING, "Divisor", INTEGER, {{"None",1},{"K",1000},{"M",1000000}})

Date Axis =
VAR _last = MAX(Sales[Date])
RETURN
ADDCOLUMNS(
    FILTER(SUMMARIZE('Date', 'Date'[Year], 'Date'[Month Start]), 'Date'[Month Start] <= _last),
    "Month", FORMAT('Date'[Month Start], "MMM"),
    "Month No", MONTH('Date'[Month Start])
)
```
Sort `Cohort For[Metric]` by `Sort`, and `Date Axis[Month]` by `Month No`.

### Step 6: Write the measures
See [DAX Measures Explained](#-dax-measures-explained).

### Step 7: Build the visuals
Matrix, area charts, slicers and HTML KPI cards. See [Visual Design Notes](#-visual-design-notes).

### Step 8: Test, then publish
Run the [validation checks](#-validation-checks), publish to the Power BI Service, and share the live link.

---

## 📐 DAX Measures Explained

### 1. Core measures

| Measure | What it does |
|---|---|
| `Total Sales` | `SUM(Sales[Sales Amount])` |
| `Active Customers` | Distinct customers with a sale in the current filter context |
| `Acquired Customers` | Customers whose **first** purchase falls in the period (`Months Since First Purchase = 0`) |
| `Orders` | `DISTINCTCOUNT(Sales[Invoice])` |
| `Quantity` | `SUM(Sales[Quantity])` |

```DAX
Total Sales = SUM(Sales[Sales Amount])
Active Customers = DISTINCTCOUNT(Sales[Customer ID])
Acquired Customers = CALCULATE([Active Customers], Sales[Months Since First Purchase] = 0)
```

> **Why does `Acquired Customers` work?** In any period, sales with month number 0 belong to customers buying for the first time, which means they were acquired that month.

### 2. Prior-year comparison (repeated for each KPI)

```DAX
Active Customers PY = CALCULATE([Active Customers], SAMEPERIODLASTYEAR('Date'[Date]))
Active Customers Var = [Active Customers] - [Active Customers PY]
Active Customers Var % = DIVIDE([Active Customers Var], [Active Customers PY])
```
The same pattern is used for `Acquired Customers` and `Total Sales`. Because the data starts in Jan 2025, prior-year values are blank for all 2025 months, and the cards show "No prior-year data".

### 3. Selected month

```DAX
Selected Month =
VAR _lastDate  = CALCULATE(MAX(Sales[Date]), REMOVEFILTERS())
VAR _lastMonth = DATE(YEAR(_lastDate), MONTH(_lastDate), 1)
RETURN
IF(HASONEVALUE('Date'[Month Start]), MAX('Date'[Month Start]), _lastMonth)
```
Returns the month chosen in the slicer, or falls back to the latest month with data if nothing is selected, so the visuals never go blank.

### 4. Cohort building blocks

**Is Observable** returns 1 when the month has already happened for a cohort, and 0 when it is still in the future. It keeps the lower-right of the matrix blank instead of showing fake zeros.

```DAX
Is Observable =
VAR _i = SELECTEDVALUE('Month Index'[Index])
VAR _lastDate = CALCULATE(MAX(Sales[Date]), REMOVEFILTERS())
VAR _lastMonth = DATE(YEAR(_lastDate), MONTH(_lastDate), 1)
VAR _cohortMonth = MIN(Customers[Cohort Month])
RETURN IF(EDATE(_cohortMonth, _i) <= _lastMonth, 1, 0)
```

**Cohort Size** is the number of customers in the cohort at month 0, which is the denominator for retention.

```DAX
Cohort Size =
CALCULATE(
    DISTINCTCOUNT(Sales[Customer ID]),
    Sales[Months Since First Purchase] = 0,
    REMOVEFILTERS('Month Index')
)
```

**Cohort Customers** is the number of customers from the row's cohort who bought in month *N* (the column).

```DAX
Cohort Customers =
VAR _i = SELECTEDVALUE('Month Index'[Index])
VAR _v = CALCULATE(DISTINCTCOUNT(Sales[Customer ID]), Sales[Months Since First Purchase] = _i)
RETURN IF([Is Observable] = 1, _v)
```

> **How one matrix cell is calculated (row Jun-2025, column 3):**
> 1. The row filters customers to the **Jun-2025 cohort**.
> 2. The column provides `_i = 3`.
> 3. The measure keeps only sales where `Months Since First Purchase = 3` (their September purchases).
> 4. It counts the distinct customers on those sales.

### 5. The five cohort metrics

| Metric | Formula idea |
|---|---|
| **Customer Retention %** | `Cohort Customers ÷ Cohort Size` |
| **Customer Churn %** | `1 − Retention %` |
| **Customer Revenue** | Cohort revenue in month *N* only (`Months Since First Purchase = N`) |
| **Customer Life Time Revenue** | Cumulative cohort revenue from month 0 to *N* (`<= N`) |

```DAX
Customer Retention % = DIVIDE([Cohort Customers], [Cohort Size])

Customer Churn % =
VAR _r = [Customer Retention %]
RETURN IF(NOT ISBLANK(_r), 1 - _r)

Customer Revenue =
VAR _i = SELECTEDVALUE('Month Index'[Index])
VAR _v = CALCULATE(SUMX(Sales, Sales[Quantity] * RELATED(Products[Price])),
                   Sales[Months Since First Purchase] = _i)
RETURN IF([Is Observable] = 1, _v)

Customer Life Time Revenue =
VAR _i = SELECTEDVALUE('Month Index'[Index])
VAR _v = CALCULATE(SUMX(Sales, Sales[Quantity] * RELATED(Products[Price])),
                   Sales[Months Since First Purchase] <= _i)
RETURN IF([Is Observable] = 1, _v)
```

### 6. The dynamic matrix value

`Cohort Value` reads the **Cohort for** dropdown and returns the matching metric. Month 0 always shows the raw customer count, and later months show the % of that count for retention.

```DAX
Cohort Value =
VAR _metric = SELECTEDVALUE('Cohort For'[Metric], "Cohort Customers")
VAR _i      = SELECTEDVALUE('Month Index'[Index])
VAR _div    = SELECTEDVALUE(Unit[Divisor], 1)
VAR _start  = [Cohort Size]
VAR _cust   = [Cohort Customers]
VAR _rev    = [Customer Revenue]
VAR _ltr    = [Customer Life Time Revenue]
VAR _revFmt = IF(_div = 1, "#,0", "#,0.0")
RETURN
IF(ISBLANK(_i), BLANK(),
    SWITCH(_metric,
        "Cohort Customers",           IF(NOT ISBLANK(_cust), FORMAT(_cust, "#,0")),
        "Customer Retention %",       IF(_i = 0, FORMAT(_cust, "#,0"),
                                          IF(NOT ISBLANK(_cust), FORMAT(DIVIDE(_cust, _start), "0%"))),
        "Customer Churn %",           IF(NOT ISBLANK(_cust), FORMAT(1 - DIVIDE(_cust, _start), "0%")),
        "Customer Revenue",           IF(NOT ISBLANK(_rev), FORMAT(DIVIDE(_rev, _div), _revFmt)),
        "Customer Life Time Revenue", IF(NOT ISBLANK(_ltr), FORMAT(DIVIDE(_ltr, _div), _revFmt))
    ))
```

> **Note:** the label text inside `SWITCH` must match the `Cohort For[Metric]` labels exactly.
> **Design trade-off:** `FORMAT()` returns text, so a numeric companion measure (below) drives the colours and charts.

### 7. Matrix colours

**Cohort Heat** is a numeric 0–1 value used to shade each cell, scaled by metric.

```DAX
Cohort Heat =
VAR _metric = SELECTEDVALUE('Cohort For'[Metric], "Cohort Customers")
VAR _i      = SELECTEDVALUE('Month Index'[Index])
VAR _start  = [Cohort Size]
VAR _cust   = [Cohort Customers]
VAR _rev0 =
    CALCULATE([Total Sales], Sales[Months Since First Purchase] = 0, REMOVEFILTERS('Month Index'))
RETURN
IF(ISBLANK(_i) || _i = 0, BLANK(),
    SWITCH(_metric,
        "Cohort Customers",           DIVIDE(_cust, _start),
        "Customer Retention %",       DIVIDE(_cust, _start),
        "Customer Churn %",           IF(NOT ISBLANK(_cust), 1 - DIVIDE(_cust, _start)),
        "Customer Revenue",           DIVIDE([Customer Revenue], _rev0),
        "Customer Life Time Revenue", DIVIDE([Customer Life Time Revenue], _rev0)
    ))
```

**Cohort BG Color** returns a hex colour per cell: grey for month 0 (darker for bigger cohorts) and a soft purple scale for the rest. It is applied through *Cell elements → Background color → Field value*.

**Cohort Font Color** highlights the selected month's row:

```DAX
Cohort Font Color =
IF(MIN(Customers[Cohort Month]) = [Selected Month], "#2B3A9F", "#333333")
```

### 8. Trend chart (CY vs PY)

```DAX
Cohort Number =
VAR _metric = SELECTEDVALUE('Cohort For'[Metric], "Cohort Customers")
VAR _div    = SELECTEDVALUE(Unit[Divisor], 1)
RETURN
SWITCH(_metric,
    "Cohort Customers",           [Cohort Customers],
    "Customer Retention %",       [Customer Retention %],
    "Customer Churn %",           [Customer Churn %],
    "Customer Revenue",           DIVIDE([Customer Revenue], _div),
    "Customer Life Time Revenue", DIVIDE([Customer Life Time Revenue], _div))

Cohort Value CY =
CALCULATE([Cohort Number], REMOVEFILTERS('Date'), Customers[Cohort Month] = [Selected Month])

Cohort Value PY =
CALCULATE([Cohort Number], REMOVEFILTERS('Date'), Customers[Cohort Month] = EDATE([Selected Month], -12))

Trend Title = "Trend: " & SELECTEDVALUE('Cohort For'[Metric], "Cohort Customers")
```
`CY` is the selected month's cohort and `PY` is the same cohort 12 months earlier. `REMOVEFILTERS('Date')` lets the chart show all later months for that cohort.

### 9. Average customers retained (KPI card)

The average of retained customers for months 1 and later, for the selected cohort (month 0 excluded):

```DAX
Avg Customers Retained =
VAR _m = [Selected Month]
RETURN
AVERAGEX(
    FILTER(ALL('Month Index'[Index]), 'Month Index'[Index] > 0),
    CALCULATE([Cohort Customers], REMOVEFILTERS('Date'), Customers[Cohort Month] = _m)
)
```
`Avg Customers Retained PY` is identical, using `EDATE([Selected Month], -12)`.

### 10. Acquisition chart and dynamic title

```DAX
Acquired Customers Axis =
CALCULATE([Acquired Customers], REMOVEFILTERS('Date'),
          TREATAS(VALUES('Date Axis'[Month Start]), 'Date'[Month Start]))

Acq Avg CY =
VAR _y = YEAR(MAX('Date'[Month Start]))
RETURN AVERAGEX(FILTER(ALL('Date Axis'[Month Start]), YEAR('Date Axis'[Month Start]) = _y),
                [Acquired Customers Axis])

Acq Avg PY =
VAR _y = YEAR(MAX('Date'[Month Start])) - 1
RETURN AVERAGEX(FILTER(ALL('Date Axis'[Month Start]), YEAR('Date Axis'[Month Start]) = _y),
                [Acquired Customers Axis])

Acquired Title =
VAR _y = YEAR(MAX('Date'[Month Start]))
VAR _cy = [Acq Avg CY]
VAR _py = [Acq Avg PY]
VAR _var = _cy - _py
RETURN
"Customers Acquired -> " & _y & " Avg. " & FORMAT(_cy, "#,0") &
IF(ISBLANK(_py), " | No prior-year data",
   " | " & (_y - 1) & " Avg. " & FORMAT(_py, "#,0") &
   " | Variance " & FORMAT(_var, "+#,0;-#,0") &
   " | Variance% " & FORMAT(DIVIDE(_var, _py), "+0%;-0%"))
```
The title is bound to the chart through *Title → fx → Field value*, so it updates with the selected year.

### 11. KPI cards (DAX + HTML)

Each KPI card is a DAX measure that returns **HTML**, rendered by the *HTML Content* visual. One scale variable (`_s`) controls every size, and each card calculates its own value, prior-year value, variance pills (green for up, red for down) and "vs last year" line.

```DAX
KPI HTML Active Customers =
VAR _s = 1.15                                  -- one number scales the whole card
VAR _val = [Active Customers]
VAR _py  = [Active Customers PY]
VAR _var = _val - _py
VAR _pct = DIVIDE(_var, _py)
VAR _has = NOT ISBLANK(_py)
VAR _up  = _var >= 0
VAR _fill = IF(_up, "#E3F6EA", "#FDE3E6")
VAR _ink  = IF(_up, "#1E8E3E", "#D93025")
-- ... font sizes, padding and pill styles derived from _s ...
RETURN
"<div style='font-family:Segoe UI,Arial,sans-serif;background:#fff;border-radius:40px; ...'>"
    & "<!-- icon, label, value, two variance pills, 'vs last year' line -->"
& "</div>"
```
The same pattern is used for Acquired Customers, Avg. Customers Retained and Total Sales (which adds `K`/`M` formatting). See `dax/kpi_cards.dax` in the repo for the full code.

---

## 🎨 Visual Design Notes

| Visual | Fields | Key formatting |
|---|---|---|
| **Cohort matrix** | Rows `Cohort Label`, Columns `Month Index[Index]`, Values `Cohort Value` | Style = None; totals off; centred values; background and font colours from `Cohort BG Color` / `Cohort Font Color`; visual filter `Index ≤ 21` |
| **Customers Acquired** (area) | X `Date Axis[Year]` + `Month`, Y `Acquired Customers Axis` | Smoothed line; data labels on; title from `Acquired Title` |
| **Trend: Cohort** (area) | X `Month Index[Index]`, Y `Cohort Value PY`, `Cohort Value CY` | Categorical axis; CY in blue over PY in grey; title from `Trend Title` |
| **KPI cards** | HTML Content with the `KPI HTML …` measures | Visual background, border and shadow off; rounded corners set on the visual |
| **Slicers** | Month (single select), Country, Segment, Brand, Category | Month slicer set to **None** on the matrix and acquisition chart via *Edit interactions* |

**Interaction rules that make the page work**
- The **month slicer must not filter the matrix**. Otherwise each row would show only one month.
- **Cohort for** and **Unit** are single-select with "Select all" off.
- A visual filter (`Index ≤ 21`) removes empty columns beyond the data range.

---

## ✅ Validation Checks

| Check | Expected result |
|---|---|
| Matrix Month 0 | Equals the cohort's `Acquired Customers` |
| Retention % at month 0 | 100% for every cohort |
| Churn % at month 0 | 0% |
| Retention % + Churn % in any cell | Exactly 100% |
| Lifetime Revenue across a row | Never decreases |
| Lower-right of the matrix | Blank, not zero |
| Avg. Customers Retained | Equals a hand-calculated average of months 1+ in that cohort's row |
| CY at month 0 in the trend chart | Equals the Acquired Customers KPI for the same month |
| Prior-year values for 2025 | Blank (no 2024 data), shown as "No prior-year data" |

---

## 📁 Repository Structure

```
cohort-sales-dashboard/
├── README.md
├── cohort_dashboard.pbix            # Power BI report
├── data/
│   ├── Cohort_Sales_Data_2025_2026.xlsx
│   └── generate_data.py             # synthetic data generator
├── dax/
│   ├── columns.dax
│   ├── measures.dax
│   └── kpi_cards.dax
└── images/
    ├── dashboard-overview.png
    ├── cohort-matrix.png
    ├── kpi-cards.png
    └── data-model.png
```

---

## ▶️ How to Run It Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/cohort-sales-dashboard.git
   ```
2. **Open** `cohort_dashboard.pbix` in **Power BI Desktop**.
3. If prompted, **update the data source path** (*Transform data → Data source settings*) to point to `data/Cohort_Sales_Data_2025_2026.xlsx`.
4. To **regenerate data**:
   ```bash
   cd data
   pip install pandas numpy openpyxl
   python generate_data.py
   ```
5. The **HTML Content** custom visual must be installed from AppSource for the KPI cards to render.

---

## 💡 What I Learned

- **Cohort logic comes down to two fields:** a cohort month per customer and a months-since-first-purchase number per sale.
- **Disconnected tables are powerful:** they enable matrix columns, dropdown-driven `SWITCH` measures and a slicer-proof time axis.
- **Blank beats zero:** using an observability flag keeps future cells empty, so the matrix tells the truth.
- **Text and numbers need separate measures:** a formatted text measure cannot drive colour scales or chart axes.
- **Interactions need design:** deciding which slicers should *not* filter a visual (via *Edit interactions*) mattered as much as the DAX.
- **DAX can drive presentation too:** HTML in measures gives full control of KPI card design.

---

## 🙏 Credits and Disclaimer

- Dashboard layout and concept inspired by **Goodly Insights**' cohort analysis tutorial. The data model, synthetic dataset, DAX measures and extended features here were built independently for 2025–2026.
- All data is **synthetic**. Numbers are illustrative and do not represent any real company or customers.

---

## 📬 Contact

**Azar Shaik**
Data / BI Analyst · 3+ years of experience · **open to new opportunities**

- 💼 LinkedIn: [your-linkedin-url](https://www.linkedin.com/in/azarshaik/)
- 📧 Email: Azarshaik963@gmail.com
- 🔗 Live dashboard: [View here]([https://app.powerbi.com/links/xmq-_qndGL?ctid=d8951f7f-6451-4c56-9e5f-2ad53476f070&pbi_source=linkShare])

If this project helped you, a ⭐ on the repo is appreciated.
