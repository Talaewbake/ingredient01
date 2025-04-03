
import streamlit as st
import pandas as pd
import datetime
import os

# กำหนดธีมสีแบบพาสเทล
st.markdown("""
    <style>
        .main {
            background-color: #f9f9f9;
        }
        .stButton>button {
            background-color: #A3D2CA;
            color: black;
            border-radius: 8px;
            height: 3em;
            width: 100%;
        }
        .stTextInput>div>div>input {
            background-color: #ffffff;
        }
        .stDataFrame {
            background-color: #ffffff;
        }
        .css-1d391kg, .css-ffhzg2 {  /* headers */
            color: #5EAAA8;
        }
    </style>
""", unsafe_allow_html=True)

# ชื่อไฟล์ CSV สำหรับเก็บข้อมูล
CSV_FILE = "stock_data.csv"

# โหลดข้อมูลจากไฟล์ CSV ถ้ามี
if os.path.exists(CSV_FILE):
    stock_df = pd.read_csv(CSV_FILE)
else:
    stock_df = pd.DataFrame(columns=["ชื่อวัตถุดิบ", "จำนวน", "หน่วย", "วันหมดอายุ"])

# แปลงค่าวันหมดอายุให้เป็นวันที่
if not stock_df.empty:
    stock_df["วันหมดอายุ"] = pd.to_datetime(stock_df["วันหมดอายุ"], errors='coerce')

# หัวข้อของเว็บ
st.title("📦 ระบบจัดการสต็อกวัตถุดิบ")

# ฟอร์มเพิ่มวัตถุดิบใหม่
with st.form("add_form"):
    st.subheader("➕ เพิ่มวัตถุดิบ")
    name = st.text_input("ชื่อวัตถุดิบ")
    qty = st.number_input("จำนวน", min_value=0.0, step=0.1)
    unit = st.selectbox("หน่วย", ["กิโลกรัม", "ลิตร", "ชิ้น", "ฟอง", "แพ็ค"])
    exp_date = st.date_input("วันหมดอายุ", min_value=datetime.date.today())
    submitted = st.form_submit_button("เพิ่มวัตถุดิบ")

    if submitted and name:
        new_data = pd.DataFrame([[name, qty, unit, exp_date]], columns=stock_df.columns)
        stock_df = pd.concat([stock_df, new_data], ignore_index=True)
        stock_df.to_csv(CSV_FILE, index=False)
        st.success(f"เพิ่มวัตถุดิบ '{name}' เรียบร้อยแล้ว")

# แสดงตารางวัตถุดิบทั้งหมด
st.subheader("📋 รายการวัตถุดิบในสต็อก")
if stock_df.empty:
    st.info("ยังไม่มีวัตถุดิบในระบบ")
else:
    today = pd.to_datetime(datetime.date.today())
    warning_df = stock_df[stock_df["วันหมดอายุ"] <= today + pd.Timedelta(days=3)]
    warning_df = warning_df.sort_values(by="วันหมดอายุ")

    if not warning_df.empty:
        st.warning("❤️⏰🚨 วัตถุดิบเหล่านี้ใกล้หมดอายุใน 3 วัน")
        st.dataframe(warning_df)

    # รวมจำนวนคงเหลือของแต่ละวัตถุดิบ
    summary_df = stock_df.groupby(["ชื่อวัตถุดิบ", "หน่วย"]).agg({"จำนวน": "sum"}).reset_index()
    summary_df = summary_df.rename(columns={"จำนวน": "จำนวนคงเหลือ"})

    st.markdown("### 📊 จำนวนคงเหลือของวัตถุดิบ")
    st.dataframe(summary_df)

    st.markdown("### 🗂️ รายการทั้งหมด")
    sorted_df = stock_df.sort_values(by="วันหมดอายุ")
    st.dataframe(sorted_df)

# ตัวเลือกสำหรับลบรายการ
st.subheader("🗑️ ลบวัตถุดิบ")
item_to_delete = st.selectbox("เลือกวัตถุดิบที่ต้องการลบ", ["-"] + list(stock_df["ชื่อวัตถุดิบ"]))
if st.button("ลบรายการ"):
    if item_to_delete != "-":
        stock_df = stock_df[stock_df["ชื่อวัตถุดิบ"] != item_to_delete]
        stock_df.to_csv(CSV_FILE, index=False)
        st.success(f"ลบ '{item_to_delete}' เรียบร้อยแล้ว")
    else:
        st.warning("กรุณาเลือกรายการที่จะลบก่อน")
