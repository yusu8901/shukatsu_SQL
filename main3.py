# 単純なルールベースの絞り込みを、クエリ作成
# streamlitで実装
#step2
#AIによるフィードバック

import sqlite3
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

#----------------------------------------
# データベースへの格納
#----------------------------------------
conn = sqlite3.connect("company_data.db")
c = conn.cursor()

#----------------------------------------
# セッションステートの初期化
#----------------------------------------
if 'evaluation_response' not in st.session_state:
    st.session_state.evaluation_response = ""
if 'communication_response' not in st.session_state:
    st.session_state.communication_response = ""
if 'global_response' not in st.session_state:
    st.session_state.global_response = ""
if 'event_response' not in st.session_state:
    st.session_state.event_response = ""

#----------------------------------------
# Streamlit アプリ
#----------------------------------------
st.title("就活マッチングサービス（プロトタイプ）")

st.write("以下の条件で企業を検索できます。")

# フィルタ条件入力UI
st.subheader("評価制度において、どのような基準を重視する企業を希望しますか？")
evaluation_options = ["年功序列型", "成果主義型", "バランス型", "特にこだわりなし"]
selected_evaluation = st.radio(
    label="評価制度において、どのような基準を重視する企業を希望しますか？",
    options=evaluation_options,
    key="evaluation_radio"
)
evaluation_reason = st.text_area(
        label="選択理由を入力してください。AIからのフィードバックがもらえます。",
        key="evaluation_reason"
    )
if st.button("送信", key="evaluation_submit"):
    if evaluation_reason.strip():
            evaluation_response = client.chat.completions.create(
                                model="gpt-4",
                                messages=[
                                    {"role": "system", "content": "あなたは優秀な就活コンサルタントです。[評価制度において、どのような基準を重視する企業を希望しますか？][1.年功序列型 2.成果主義型 3.バランス型 4.特にこだわりなし]という質問に対してユーザーが選択肢を選び、その選択理由を入力しています。ユーザーがより良い選択ができるように、ときには批判する形でユーザーにアドバイスをしてください。100字程度"},
                                    {"role": "user", "content": selected_evaluation},
                                    {"role": "system", "content": "選択理由を入力してください。"},
                                    {"role": "user", "content": evaluation_reason}
                                ],
                            )
            st.session_state.evaluation_response = evaluation_response.choices[0].message.content

# AIからの応答を表示
if st.session_state.evaluation_response:
    with st.chat_message("assistant"):
        st.markdown(st.session_state.evaluation_response)
            

st.subheader("上司や先輩とのコミュニケーションについて、どのような環境を望みますか？")
communication_options = ["密接型", "上下関係重視型（立場を尊重）", "自律型（最小限のやり取り）", "特にこだわりなし"]
selected_communication = st.radio(
    label="上司や先輩とのコミュニケーションについて、どのような環境を望みますか？",
    options=communication_options,
    key="communication_radio"
)
communication_reason = st.text_area(
        label="選択理由を入力してください。AIからのフィードバックがもらえます。",
        key="communication_reason"
    )

if st.button("送信", key="communication_submit"):
    if communication_reason.strip():
            communication_response = client.chat.completions.create(
                                model="gpt-4",
                                messages=[
                                    {"role": "system", "content": "あなたは優秀な就活コンサルタントです。[上司や先輩とのコミュニケーションについて、どのような環境を望みますか？][1.密接型 2.上下関係重視型（立場を尊重） 3.自律型（最小限のやり取り） 4.特にこだわりなし]という質問に対してユーザーが選択肢を選び、その選択理由を入力しています。ユーザーがより良い選択ができるように、ときには批判する形でユーザーにアドバイスをしてください。100字程度"},
                                    {"role": "user", "content": selected_communication},
                                    {"role": "system", "content": "選択理由を入力してください。"},
                                    {"role": "user", "content": communication_reason}
                                ],
                            )
            with st.chat_message("assistant"):
                st.markdown(communication_response.choices[0].message.content)
        

st.subheader("外国籍のメンバーが多い企業を希望しますか？")
global_environment_options = ["希望する", "希望しない", "特にこだわりなし"]
selected_global_environment = st.radio(
    label="外国籍のメンバーが多い企業を希望しますか？",
    options=global_environment_options,
    key="global_environment_radio"
)
global_reason = st.text_area(
        label="選択理由を入力してください。AIからのフィードバックがもらえます。",
        key="global_reason"
    )

if st.button("送信", key="global_submit"):
    if global_reason.strip():
            global_response = client.chat.completions.create(
                                model="gpt-4",
                                messages=[
                                    {"role": "system", "content": "あなたは優秀な就活コンサルタントです。[外国籍のメンバーが多い企業を希望しますか？][1.希望する 2.希望しない 3.特にこだわりなし]という質問に対してユーザーが選択肢を選び、その選択理由を入力しています。ユーザーがより良い選択ができるように、ときには批判する形でユーザーにアドバイスをしてください。100字程度"},
                                    {"role": "user", "content": selected_global_environment},
                                    {"role": "system", "content": "選択理由を入力してください。"},
                                    {"role": "user", "content": global_reason}
                                ],
                            )
            with st.chat_message("assistant"):
                st.markdown(global_response.choices[0].message.content)
        

st.subheader("社内で行われるイベントが多い企業を希望しますか？")
internal_events_options = ["積極的に参加したい", "参加したくない", "特にこだわりなし"]
selected_internal_events = st.radio(
    label="社内で行われるイベントが多い企業を希望しますか？",
    options=internal_events_options,
    key="internal_events_radio"
)
event_reason = st.text_area(
        label="選択理由を入力してください。AIからのフィードバックがもらえます。",
        key="event_reason"
    )
if st.button("送信", key="event_submit"):
    if event_reason.strip():
            event_response = client.chat.completions.create(
                                model="gpt-4",
                                messages=[
                                    {"role": "system", "content": "あなたは優秀な就活コンサルタントです。[社内で行われるイベントが多い企業を希望しますか？][1.積極的に参加したい 2.参加したくない 3.特にこだわりなし]という質問に対してユーザーが選択肢を選び、その選択理由を入力しています。ユーザーがより良い選択ができるように、ときには批判する形でユーザーにアドバイスをしてください。100字程度"},
                                    {"role": "user", "content": selected_internal_events},
                                    {"role": "system", "content": "選択理由を入力してください。"},
                                    {"role": "user", "content": event_reason}
                                ],
                            )
            
            with st.chat_message("assistant"):
                st.markdown(event_response.choices[0].message.content)
        

#----------------------------------------
# クエリの生成
#----------------------------------------
query = "SELECT * FROM companies2 WHERE 1=1"
params = []

if selected_evaluation != "特にこだわりなし":
    query += " AND evaluation = ?"
    params.append(selected_evaluation)

if selected_communication != "特にこだわりなし":
    query += " AND communication = ?"
    params.append(selected_communication)

if selected_global_environment != "特にこだわりなし":
    if selected_global_environment == "希望する":
        params.append("yes")
    elif selected_global_environment == "希望しない":
        params.append("no")
    query += " AND global_environment = ?"

if selected_internal_events != "特にこだわりなし":
    if selected_internal_events == "積極的に参加したい":
        params.append("参加したい")
    elif selected_internal_events == "参加したくない":
        params.append("参加したくない")
    query += " AND internal_events = ?"

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
                "社名": r[1],
                "評価制度": r[2],
                "コミュニケーション": r[3],
                "グローバル": r[4],
                "イベント": r[5]
            })
    else:
        st.write("該当する企業はありませんでした。")

# データベースに登録されているデータを出力
c.execute("SELECT * FROM companies2")
all_data = c.fetchall()

st.write("登録されている全データ:")
for data in all_data:
    st.write({
        "社名": data[1],
        "評価制度": data[2],
        "コミュニケーション": data[3],
        "グローバル": data[4],
        "イベント": data[5]
    })

# 接続クローズ（Streamlit上では常駐することも多いため必要に応じて）
# conn.close()