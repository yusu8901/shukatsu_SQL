#単純なルールベースの絞り込みを、クエリ作成
#streamlitで実装


import sqlite3
import streamlit as st

#----------------------------------------
# サンプル用ダミーデータの作成
#----------------------------------------
# ※実際にはより実際的なデータを使うべきだが、ここではサンプルとして簡易的なものを用意する。
#   50件のサンプルデータを、ある程度バラつきをつけて用意する。

# employment_type: ["正社員", "契約社員", "アルバイト/インターン"]
# work_location: ["首都圏", "関西圏", "地方"]
# salary_range: ["~300", "300~500", "500~700", "700~"]
# remote_possible: ["在宅勤務あり", "在宅勤務なし"]
# overtime: ["残業なし", "残業あり"]




#----------------------------------------
# データベースへの格納
#----------------------------------------
conn = sqlite3.connect("company_data.db")
c = conn.cursor()





#----------------------------------------
# Streamlit アプリ
#----------------------------------------
st.title("就活マッチングサービス（プロトタイプ）")

st.write("以下の条件で企業を検索できます。")

# フィルタ条件入力UI
st.subheader("雇用形態")
selected_employment = []
if st.checkbox("正社員"):
    selected_employment.append("正社員")
if st.checkbox("契約社員"):
    selected_employment.append("契約社員")
if st.checkbox("アルバイト/インターン"):
    selected_employment.append("アルバイト/インターン")

st.subheader("勤務地（エリア指定）")
selected_location = []
if st.checkbox("首都圏（東京・神奈川・千葉・埼玉）"):
    selected_location.append("首都圏")
if st.checkbox("関西圏（大阪・京都・兵庫）"):
    selected_location.append("関西圏")
if st.checkbox("地方（東北・九州 など）"):
    selected_location.append("地方")

st.subheader("給与条件")
# ラジオボタンでひとつ選択でも良いが、複数条件を想定するならチェックボックスでもOK
# 今回は一つだけ選ぶケースを想定し、ラジオボタンにする
salary_option = st.radio(
    "給与条件を選択してください",
    ("~300", "300~500", "500~700", "700~")
)

st.subheader("在宅勤務可否")
selected_remote = []
if st.checkbox("在宅勤務あり"):
    selected_remote.append("在宅勤務あり")
if st.checkbox("在宅勤務なし"):
    selected_remote.append("在宅勤務なし")

st.subheader("残業の有無")
selected_overtime = []
if st.checkbox("残業なし"):
    selected_overtime.append("残業なし")
if st.checkbox("残業あり"):
    selected_overtime.append("残業あり")

#----------------------------------------
# クエリの生成
#----------------------------------------
query = "SELECT * FROM companies WHERE 1=1"
params = []

if selected_employment:
    # 複数選択されている場合はIN句を使う
    placeholders = ",".join(["?"]*len(selected_employment))
    query += f" AND employment_type IN ({placeholders})"
    params.extend(selected_employment)

if selected_location:
    placeholders = ",".join(["?"]*len(selected_location))
    query += f" AND work_location IN ({placeholders})"
    params.extend(selected_location)

if salary_option:
    query += " AND salary_range = ?"
    params.append(salary_option)

if selected_remote:
    placeholders = ",".join(["?"]*len(selected_remote))
    query += f" AND remote_possible IN ({placeholders})"
    params.extend(selected_remote)

if selected_overtime:
    placeholders = ",".join(["?"]*len(selected_overtime))
    query += f" AND overtime IN ({placeholders})"
    params.extend(selected_overtime)

#----------------------------------------
# 結果の表示
#----------------------------------------
if st.button("検索"):
    c.execute(query, params)
    results = c.fetchall()
    if results:
        st.write(f"該当企業数: {len(results)} 件")
        for r in results:
            st.write({
                "社名": r[0],
                "雇用形態": r[1],
                "勤務地": r[2],
                "給与条件": r[3],
                "在宅勤務可否": r[4],
                "残業の有無": r[5]
            })
    else:
        st.write("該当する企業はありませんでした。")

# データベースに登録されているデータを出力
c.execute("SELECT * FROM companies")
all_data = c.fetchall()

st.write("登録されている全データ:")
for data in all_data:
    st.write({
        "社名": data[1],
        "雇用形態": data[2],
        "勤務地": data[3],
        "給与条件": data[4],
        "在宅勤務可否": data[5],
        "残業の有無": data[6]
    })

# 接続クローズ（Streamlit上では常駐することも多いため必要に応じて）
# conn.close()
