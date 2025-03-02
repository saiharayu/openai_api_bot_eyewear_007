
import streamlit as st
import openai

# OpenAI APIキーの取得（Secretsに登録されているキーを読み取る）
try:
    if "openai_api_key" in st.secrets:
        openai_api_key = st.secrets["openai_api_key"]
    elif "openai" in st.secrets and "openai_api_key" in st.secrets["openai"]:
        openai_api_key = st.secrets["openai"]["openai_api_key"]
    else:
        raise KeyError("OpenAI APIキーが見つかりません。StreamlitのSecretsに設定してください。")
except KeyError as e:
    st.error(f"❌ {e}")
    st.stop()

# OpenAI クライアントの初期化
client = openai.OpenAI(api_key=openai_api_key)

# アプリのタイトル
st.title("👓 眼鏡デザイン診断")

# セッション状態の初期化
if "question_index" not in st.session_state:
    st.session_state["question_index"] = 0
    st.session_state["answers"] = {}

# 質問リスト（Q1で性別を確認）
questions = [
    {"text": "Q1. あなたの性別を選んでください", "choices": ["男性", "女性"]},
    {"text": "Q2. あなたの顔の印象に近いのは？", "choices": ["丸みがあり、やわらかい印象", "直線的で、シャープな印象", "スッキリと縦のラインが際立つ"]},
    {"text": "Q3. あなたの理想の雰囲気は？", "choices": ["知的で洗練された印象", "柔らかく親しみやすい雰囲気", "独自のスタイルを際立たせたい"]},
    {"text": "Q4. あなたのファッションスタイルは？", "choices": ["シンプルで洗練されたスタイル", "自然体でリラックスしたファッション", "個性的でトレンドを意識"]},
    {"text": "Q5. 眼鏡を主に使うシーンは？", "choices": ["仕事やフォーマルな場面で活躍させたい", "日常の相棒として、自然に取り入れたい", "ファッションのアクセントとして楽しみたい"]},
]

# 質問の表示（1問ずつ）
index = st.session_state["question_index"]
if index < len(questions):
    q = questions[index]
    st.subheader(q["text"])
    
    for option in q["choices"]:
        if st.button(option):
            st.session_state["answers"][q["text"]] = option
            st.session_state["question_index"] += 1
            st.experimental_rerun()
else:
    st.success("✅ すべての質問に回答しました！")

    # 診断結果を生成
    if "result" not in st.session_state:
        with st.spinner("診断中..."):
            gender = st.session_state["answers"]["Q1. あなたの性別を選んでください"]
            prompt = f"""
            You are a professional eyewear designer. Based on the following user preferences, recommend the best eyeglass design for a {gender}.
            
            Face Impression: {st.session_state["answers"]["Q2. あなたの顔の印象に近いのは？"]}
            Desired Atmosphere: {st.session_state["answers"]["Q3. あなたの理想の雰囲気は？"]}
            Fashion Style: {st.session_state["answers"]["Q4. あなたのファッションスタイルは？"]}
            Usage Scene: {st.session_state["answers"]["Q5. 眼鏡を主に使うシーンは？"]}

            Provide the eyeglass design name and a stylish description in Japanese (within 250 characters).
            """
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7
            )
            result_text = response.choices[0].message.content
            st.session_state["result"] = result_text

    st.subheader("👓 診断結果")
    st.write(st.session_state["result"])

    # 眼鏡のデザイン画像を生成
    if "image_url" not in st.session_state:
        with st.spinner("画像を生成中..."):
            image_prompt = f"A simple and stylish {gender} eyeglass design. Minimalist, clean, no text, no background elements."
            image_response = client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024"
            )
            st.session_state["image_url"] = image_response.data[0].url

    # 画像の表示
    st.image(st.session_state["image_url"], caption="あなたにおすすめの眼鏡デザイン", use_column_width=True)

    # LINEで共有ボタン
    share_text = f"私の眼鏡診断結果！\n{st.session_state['result']}\n"
    share_url = f"https://line.me/R/msg/text/?{share_text}"
    st.markdown(f"[📤 LINEで共有]({share_url})", unsafe_allow_html=True)
