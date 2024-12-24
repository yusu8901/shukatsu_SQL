#threadを使ってない
# assistant apiではない
# chat apiデモfunction callingは使える
# threadはchat apiでは使えない
# function_callingされたタイミングですべての結果が表示される仕様
# function_callingは実行する関数を選び、引数を設定してくれるだけで、実際に実行はしてくれない。

import sqlite3
import streamlit as st
from openai import OpenAI
import json

# OpenAI APIキーの設定
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# データベースへの接続
DATABASE = "company_data.db"

# データベース操作関数
def search_companies(employment_type=None, work_location=None, salary_range=None, remote_possible=None, overtime=None):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    query = "SELECT company_name, employment_type, work_location, salary_range, remote_possible, overtime FROM companies WHERE 1=1"
    params = []

    if employment_type:
        query += " AND employment_type = ?"
        params.append(employment_type)
    if work_location:
        query += " AND work_location = ?"
        params.append(work_location)
    if salary_range:
        query += " AND salary_range = ?"
        params.append(salary_range)
    if remote_possible:
        query += " AND remote_possible = ?"
        params.append(remote_possible)
    if overtime:
        query += " AND overtime = ?"
        params.append(overtime)

    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return results

# Function Callingで使用する関数の定義
functions = [
    {
        "name": "search_companies",
        "description": "ユーザーの条件に基づいて企業を検索します。",
        "parameters": {
            "type": "object",
            "properties": {
                "employment_type": {
                    "type": "string",
                    "enum": ["正社員", "契約社員", "アルバイト/インターン"],
                    "description": "雇用形態"
                },
                "work_location": {
                    "type": "string",
                    "enum": ["首都圏", "関西圏", "地方"],
                    "description": "勤務地"
                },
                "salary_range": {
                    "type": "string",
                    "enum": ["~300", "300~500", "500~700", "700~"],
                    "description": "給与条件"
                },
                "remote_possible": {
                    "type": "string",
                    "enum": ["在宅勤務あり", "在宅勤務なし"],
                    "description": "在宅勤務の可否"
                },
                "overtime": {
                    "type": "string",
                    "enum": ["残業なし", "残業あり"],
                    "description": "残業の有無"
                }
            },
            "required": []
        }
    }
]

# Streamlit アプリ
st.title("就活マッチングサービス（プロトタイプ）")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "あなたは優秀な就活エージェントです。質問事項は１つずつしてください。出力の最後に選択肢をマークダウン形式のリストで出力してください。データベースを検索する前に、ユーザーに他に条件がないか必ず聞いてください。"},
        {"role": "assistant", "content": "あなたに最適な企業を紹介させていただきます！雇用形態や勤務地、給与条件、在宅勤務の可否、残業の有無など、他に具体的な条件はありますか？"}
    ]

for message in st.session_state.messages:
    if message["role"] not in ["system", "function"]:  # システムメッセージと関数メッセージを表示しない
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("検索条件を入力してください"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = client.chat.completions.create(
        model="gpt-4o", # またはその他の適切なモデル
        messages=st.session_state.messages,
        functions=functions,
        function_call="auto",
    )
    response_message = response.choices[0].message

    if response_message.function_call:
        st.info("関数 `search_companies` が呼び出されました。")
        available_functions = {
            "search_companies": search_companies,
        }
        function_name = response_message.function_call.name
        function_to_call = available_functions.get(function_name)
        if function_to_call:
            try:
                function_args = json.loads(response_message.function_call.arguments)
                function_response = function_to_call(**function_args)

                # 関数呼び出しの結果をメッセージに追加
                st.session_state.messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_response)
                })

                if function_response:
                    result_text = "あなたにこの企業をお勧めします！ \n他に追加したい条件がありましたら教えてください！\n検索結果:\n"
                    for company in function_response:
                        result_text += f"- 社名: {company[0]}, 雇用形態: {company[1]}, 勤務地: {company[2]}, 給与: {company[3]}, 在宅: {company[4]}, 残業: {company[5]}\n"
                else:
                    result_text = "該当する企業は見つかりませんでした。"

                # アシスタントの応答として結果を追加
                st.session_state.messages.append({"role": "assistant", "content": result_text})
                with st.chat_message("assistant"):
                    st.markdown(result_text)

                # 追加の会話を継続するために、会話履歴を更新
                continue_response = client.chat.completions.create(
                    model="gpt-4",
                    messages=st.session_state.messages,
                )
                continue_message = continue_response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": continue_message})
                with st.chat_message("assistant"):
                    st.markdown(continue_message)

            except json.JSONDecodeError:
                st.error("関数呼び出しの引数を解析できませんでした。")
        else:
            st.error(f"利用可能な関数に `{function_name}` は存在しません。")
            

    else:
        st.session_state.messages.append({"role": "assistant", "content": response_message.content})
        with st.chat_message("assistant"):
            st.markdown(response_message.content)