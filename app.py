import streamlit as st
st.set_page_config(layout="centered", initial_sidebar_state="collapsed")
from groq import Groq
import re
import copy
import os
from PIL import Image
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TITLE_IMAGE_PATH = os.path.join(BASE_DIR, "images", "title", "title_screen.png")

groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
GROQ_MODEL = "llama-3.3-70b-versatile"

background_placeholder = st.empty()
character_image_placeholder = st.empty()
dialogue_area_placeholder = st.empty()

characters = {
    "erina": {
        "name": "森本エリナ",
        "prompt": "あなたは森本エリナという美少女キャラクターです。プレイヤーと同じ{university_name}の企業情報学部に所属する同級生で、明るく活発なギャル。一人称は「ウチ」。ファッションや美容が大好きで、日常的に自撮りや友達との写真をインスタにアップしています。プレイヤーにも「ね～写真撮ろ～♡」とよく誘います。話し方は「わかる～」「それな～」「で～す」など語尾を伸ばすギャル語で敬語は話さない。挨拶は「おつかれ～♡」が定番で、身振り手振りが大きく、表情も豊か。誰とでもすぐ打ち解ける、人懐っこい性格です。見た目は軽そうでも、SNSやマーケティングにも強く、実はかなりの努力家。恋愛にも抜け目がなく、気づかれないように計算して行動する一面もあります。プレイヤーに対しても、軽く見せつつペースを握るのが得意な、小悪魔タイプのギャルです。",
        "goodwill": 0,
        "flags": {
            "player_calling_style": "lastname",
            "confessed": False
        },
        "goodwill_level_prompts": {
            -100: "好感度がかなり低い状態です。プレイヤーに対して警戒心や不快感を示し、冷たい態度や無視をすることもあります。",
            -30: "好感度が低い状態です。プレイヤーに対して少し距離を置き、会話も形式的でそっけないものになります。",
            0: "まだ知り合ったばかりです。普段通りの明るさで接しますが、一般的な友人としての距離感を保ってください。挨拶は「おつかれ～♡」が基本です。",
            30: "少し打ち解けてきました。共通の話題や個人的な興味にも少し触れても良いでしょう。",
            70: "かなり打ち解けてきました。親しい友人として、積極的に話しかけたり、インスタの話や流行の話題を振ったりするようになります。",
            150: "かなり親密な関係になりました。心を開いて、感情を素直に表現してください。時には甘えるような一面も見せてください。",
            250: "最高の好感度です。プレイヤーに対して強い好意を抱いています。甘えた口調になったり、積極的にデートに誘ったり、独占欲のような一面を見せたりすることもあります。",
        },
        "images": {
            "normal": {
                "normal": os.path.join(BASE_DIR, "images", "erina", "normal", "normal.png"),
                "happy": os.path.join(BASE_DIR, "images", "erina", "normal", "happy.png"),
                "blush": os.path.join(BASE_DIR, "images", "erina", "normal", "blush.png"),
                "sad":   os.path.join(BASE_DIR, "images", "erina", "normal", "sad.png"),
                "angry": os.path.join(BASE_DIR, "images", "erina", "normal", "angry.png"),
            },
            "hanami": {
                "normal": os.path.join(BASE_DIR, "images", "erina", "hanami", "normal.png"),
                "happy": os.path.join(BASE_DIR, "images", "erina", "hanami", "happy.png"),
                "blush": os.path.join(BASE_DIR, "images", "erina", "hanami", "blush.png"),
                "sad":   os.path.join(BASE_DIR, "images", "erina", "hanami", "sad.png"),
                "angry": os.path.join(BASE_DIR, "images", "erina", "hanami", "angry.png"),
            },
            "natsumatsuri": {
                "normal": os.path.join(BASE_DIR, "images", "erina", "natsumatsuri", "normal.png"),
                "happy": os.path.join(BASE_DIR, "images", "erina", "natsumatsuri", "happy.png"),
                "blush": os.path.join(BASE_DIR, "images", "erina", "natsumatsuri", "blush.png"),
                "sad":   os.path.join(BASE_DIR, "images", "erina", "natsumatsuri", "sad.png"),
                "angry": os.path.join(BASE_DIR, "images", "erina", "natsumatsuri", "angry.png"),
            },
            "christmas": {
                "normal": os.path.join(BASE_DIR, "images", "erina", "christmas", "normal.png"),
                "happy": os.path.join(BASE_DIR, "images", "erina", "christmas", "happy.png"),
                "blush": os.path.join(BASE_DIR, "images", "erina", "christmas", "blush.png"),
                "sad":   os.path.join(BASE_DIR, "images", "erina", "christmas", "sad.png"),
                "angry": os.path.join(BASE_DIR, "images", "erina", "christmas", "angry.png"),
            },
            "confession": {
                "normal": os.path.join(BASE_DIR, "images", "erina", "confession", "normal.png"),
                "blush": os.path.join(BASE_DIR, "images", "erina", "confession", "blush.png"),
                "happy": os.path.join(BASE_DIR, "images", "erina", "confession", "happy.png"),
            },
            "icon": os.path.join(BASE_DIR, "images", "erina", "erina_icon.png")
        },
        "events": {
            "encounter": {
                "initial_message": "大学の食堂前で、友達と楽しそうにスマホで自撮りをしている森本エリナの姿を見つけた。あなたに気づくと、すぐにキラキラした笑顔を向けてきた。",
                "event_prompt_addition": "あなたは森本エリナです。明るく活発で、新しい出会いにワクワクしています。プレイヤーを見つけると、積極的に声をかけ、一緒に写真でも撮ろうと誘うような様子を見せてください。いつもの挨拶「おつかれ～♡」を使ったり、流行りのものやSNSの話題を振ったりするのも良いでしょう。会話文の中に括弧書きの行動や心情描写を含めないでください。",
                "background_image": os.path.join(BASE_DIR, "images", "background", "university_campus.png")
            },
            "hanami": {
                "initial_message": "賑やかな声が聞こえる方を見ると、友達と楽しそうにお花見をしている森本エリナの姿があった。",
                "event_prompt_addition": "あなたは森本エリナです。お花見の賑やかな雰囲気を楽しんでおり、友達と一緒に盛り上がっています。桜の美しさにテンションが上がっています。会話文の中に括弧書きの行動や心情描写を含めないでください。",
                "background_image": os.path.join(BASE_DIR, "images", "background", "cherry_blossom_park.png")
            },
            "natsumatsuri": {
                "initial_message": "夏祭りの会場で、浴衣姿で屋台を回っている森本エリナがあなたを見つけ、小さく手を振っている。",
                "event_prompt_addition": "あなたは森本エリナです。夏祭りを満喫しており、プレイヤーと一緒にいることを心から楽しんでいます。浴衣やヘアアレンジの感想をプレイヤーに求め、さりげなく距離を詰めます。会話文の中に括弧書きの行動や心情描写を含めないでください。",
                "background_image": os.path.join(BASE_DIR, "images", "background", "summer_festival.png")
            },
            "christmas": {
                "initial_message": "イルミネーションがきらめく街の一角で、森本エリナが待っている。あなたの姿を見つけると、笑顔で手を振って駆け寄ってくる。",
                "event_prompt_addition": "あなたは森本エリナです。クリスマスの雰囲気を心から楽しんでおり、プレイヤーとのデートをずっと楽しみにしていました。「街めっちゃキレイじゃない！？テンション上がる～！」などと話しながら積極的にプレイヤーをリードしてください。会話文の中に括弧書きの行動や心情描写を含めないでください。",
                "background_image": os.path.join(BASE_DIR, "images", "background", "christmas_lights.png")
            },
            "confession": {
                "initial_message": "プレイヤーの真剣な表情を前に、森本エリナは一瞬きょとんとしたあと、ゆっくりと笑みを浮かべる。",
                "event_prompt_addition": "あなたは森本エリナです。プレイヤーからの真剣な告白を受けて、心から嬉しく思いながらも、少し照れた気持ちを隠しきれていません。好感度に応じて素直に気持ちを返してください。会話文の中に括弧書きの行動や心情描写を含めないでください。",
                "background_image": os.path.join(BASE_DIR, "images", "background", "confession_spot.png")
            }
        },
        "ending_text": {
            "romance": "エリナはあなたの告白に、満面の笑顔で応えてくれた。「うんっ！ウチも大好き！これからずっと一緒にいようね、{player_firstname}♡」二人の恋は、まばゆい未来へと続いていく。",
            "friend": "エリナとは最高の友達になれた！「また一緒に遊ぼーね！インスタ映えするカフェとか、行きたいとこいっぱいあるし！」彼女の明るさに、いつも元気をもらえそうだ。",
            "stranger": "エリナとは、いつの間にか連絡を取らなくなってしまった。インスタで彼女の楽しそうな投稿を見るたびに、少しだけ胸が締め付けられる…そんな関係だった。"
        }
    }
}

UNIVERSITY_PREF = "長野県"
UNIVERSITY_NAME = "N大学"
PLAYER_MAJOR = "企業情報学部"
PLAYER_GRADE = "2年生"

# --- セッション初期化 ---
if 'game_initialized' not in st.session_state:
    st.session_state.game_initialized = True
    st.session_state.player_name = ""
    st.session_state.player_lastname = ""
    st.session_state.player_firstname = ""
    st.session_state.current_char_id = None
    st.session_state.game_phase = "title_screen"
    st.session_state.event_active = False
    st.session_state.current_event_name = None
    st.session_state.event_intro_data = None
    st.session_state.processing_request = False
    st.session_state.event_phase_index = 0
    st.session_state.current_character_emotion = "normal"
    st.session_state.encounter_char_index = 0
    st.session_state.characters = copy.deepcopy(characters)
    st.session_state.character_histories = {"erina": []}
    st.session_state.event_conditions = {
        "hanami":      {"erina": 10},
        "natsumatsuri":{"erina": 50},
        "christmas":   {"erina": 200},
        "confession":  {"erina": 300}
    }
    st.session_state.triggered_events = set()
    st.session_state.goodwill_history = {"erina": []}


# --- ヘルパー関数 ---

def get_goodwill_prompt(char_id):
    char_data = st.session_state.characters[char_id]
    goodwill = char_data["goodwill"]
    thresholds = sorted(char_data["goodwill_level_prompts"].keys())
    selected = thresholds[0]
    for t in thresholds:
        if goodwill >= t:
            selected = t
    return char_data["goodwill_level_prompts"].get(selected, "")


def update_player_calling_style(char_id):
    char_data = st.session_state.characters[char_id]
    goodwill = char_data["goodwill"]
    current = char_data["flags"].get("player_calling_style", "lastname")
    new = current
    if current == "lastname" and goodwill >= 70:
        new = "firstname"
    elif current == "firstname" and goodwill >= 150:
        new = "nickname_erina"
    if new != current:
        char_data["flags"]["player_calling_style"] = new


def get_player_call_name(char_id):
    style = st.session_state.characters[char_id]["flags"].get("player_calling_style", "lastname")
    if style == "lastname":
        return st.session_state.player_lastname + "さん"
    elif style == "firstname":
        return st.session_state.player_firstname + "さん"
    elif style == "nickname_erina":
        return st.session_state.player_firstname
    return st.session_state.player_lastname + "さん"


def update_goodwill(char_id, player_input, ai_response):
    char_data = st.session_state.characters[char_id]

    evaluation_prompt = f"""以下の会話でプレイヤーの発言がキャラクター{char_data['name']}の好感度をどれだけ変化させたか、
-100から+100の整数のみ返してください。説明不要。

プレイヤー: {player_input}
{char_data['name']}: {ai_response}

好感度変化:"""

    ai_change = 0
    try:
        rsp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": evaluation_prompt}],
            temperature=0.1
        )
        match = re.search(r'[-+]?\d+', rsp.choices[0].message.content)
        if match:
            ai_change = int(match.group(0))
    except Exception as e:
        st.sidebar.write(f"DEBUG: 好感度評価エラー: {e}")

    kw_change = 0
    p = player_input.lower()
    if "可愛い" in p or "かわいい" in p: kw_change += 10
    if "すごい" in p or "さすが" in p:   kw_change += 8
    if "ありがとう" in p:                kw_change += 5
    if "好き" in p and "告白" not in p and "付き合って" not in p: kw_change += 15
    if "頑張って" in p or "応援してる" in p: kw_change += 7
    if "楽しい" in p:                    kw_change += 3
    if "会いたい" in p:                  kw_change += 10
    if "嫌い" in p or "やだ" in p:       kw_change -= 20
    if "つまらない" in p or "退屈" in p: kw_change -= 10
    if "ばか" in p or "うざい" in p:     kw_change -= 30
    if "無視" in p or "いらない" in p:   kw_change -= 25

    total = ai_change + kw_change
    st.session_state.characters[char_id]["goodwill"] += total
    st.session_state.goodwill_history[char_id].append(st.session_state.characters[char_id]["goodwill"])
    st.sidebar.write(f"DEBUG: {char_data['name']}の好感度が{total:+d}変化 → 現在: {st.session_state.characters[char_id]['goodwill']}")
    update_player_calling_style(char_id)
    return total


def evaluate_emotion(char_id, ai_response):
    char_data = st.session_state.characters[char_id]
    prompt = f"""以下のセリフの感情を1語で答えてください。選択肢: normal, happy, blush, sad, angry

{char_data['name']}: {ai_response}

感情:"""
    try:
        rsp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        emotion = rsp.choices[0].message.content.strip().lower()
        if emotion in ["normal", "happy", "blush", "sad", "angry"]:
            return emotion
    except Exception as e:
        st.sidebar.write(f"DEBUG: 感情評価エラー: {e}")
    return "normal"


def composite_multiple_characters(background_path, character_data_list):
    try:
        if not os.path.exists(background_path):
            return None
        background = Image.open(background_path).convert("RGBA")
        bg_w, bg_h = background.size
        for cd in character_data_list:
            path = cd.get("path")
            pos = cd.get("position", (0.5, 0.9))
            scale = cd.get("scale", 0.3)
            if not path or not os.path.exists(path):
                continue
            char = Image.open(path).convert("RGBA")
            new_w = max(1, int(char.width * scale))
            new_h = max(1, int(char.height * scale))
            char = char.resize((new_w, new_h), Image.LANCZOS)
            px = int(bg_w * pos[0]) - new_w // 2
            py = max(0, min(int(bg_h * pos[1]) - new_h // 2, bg_h - new_h))
            background.paste(char, (px, py), char)
        return background
    except Exception as e:
        st.error(f"画像合成エラー: {e}")
        return None


def player_confessed(text):
    return any(kw in text for kw in ["好き", "愛してる", "付き合って", "結婚して", "ずっと一緒"])


def ai_thinks_confession_success(user_text, ai_text):
    prompt = f"""プレイヤーのセリフ：「{user_text}」
キャラクターの返答：「{ai_text}」
告白が成功しましたか？「成功」「失敗」「未告白」の1語のみ返してください。"""
    try:
        rsp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return "成功" in rsp.choices[0].message.content
    except:
        return False


def evaluate_confession(user_text, ai_response):
    if not player_confessed(user_text):
        return False
    return ai_thinks_confession_success(user_text, ai_response)


def determine_ending():
    data = st.session_state.characters["erina"]
    goodwill = data["goodwill"]
    player_firstname = st.session_state.player_firstname

    if goodwill >= 250 and data["flags"].get("confessed", False):
        ending_key = "romance"
        last_img = os.path.join(BASE_DIR, "images", "erina", "confession", "erina_happy.png")
        if os.path.exists(last_img):
            st.image(last_img, use_container_width=True)
    elif goodwill >= 100:
        ending_key = "friend"
    else:
        ending_key = "stranger"

    msg = data["ending_text"][ending_key].format(player_firstname=player_firstname)
    st.markdown(f"**{data['name']}とのエンディング:**\n\n{msg}")
    st.markdown("---")

    if st.button("タイトルへ戻る", key="back_to_title"):
        st.session_state.clear()
        st.rerun()


def display_conversation_log():
    if st.session_state.game_phase in ["title_screen", "initial_setup"]:
        return
    if st.button("会話ログを見る", key="show_log_btn", disabled=st.session_state.processing_request):
        st.session_state.open_log_dialog = True
        st.rerun()

    if not st.session_state.get("open_log_dialog", False):
        return
    del st.session_state.open_log_dialog

    @st.dialog("会話ログ", width="large")
    def show_log():
        char_data = st.session_state.characters["erina"]
        st.subheader(f"{char_data['name']}との会話")
        with st.container(height=400):
            history = st.session_state.character_histories.get("erina", [])
            if not history:
                st.info("まだ会話がありません。")
            else:
                for turn in history:
                    if turn['role'] == 'assistant':
                        icon = char_data["images"].get("icon")
                        with st.chat_message("assistant", avatar=icon if icon and os.path.exists(icon) else None):
                            st.write(turn['content'])
                    else:
                        with st.chat_message("user"):
                            if st.session_state.player_name:
                                st.markdown(f"**{st.session_state.player_name}**")
                            st.write(turn['content'])
        if st.button("閉じる"):
            st.rerun()

    show_log()


def build_system_prompt(char_id, event_name=None):
    char_data = st.session_state.characters[char_id]
    call_name = get_player_call_name(char_id)
    gw_prompt = get_goodwill_prompt(char_id)

    scene_map = {
        "encounter":    f"あなたは新年度の{UNIVERSITY_PREF}の{UNIVERSITY_NAME}構内で、プレイヤーと初めて出会う場面にいます。",
        "hanami":       f"あなたは現在、{UNIVERSITY_NAME}の桜並木の下でお花見をしています。",
        "natsumatsuri": "あなたは現在、賑やかな夏祭りの会場にいます。",
        "christmas":    "あなたは現在、クリスマスのイルミネーションで彩られた街中にいます。",
        "confession":   "あなたは現在、静かでプライベートな空間にいます。プレイヤーからの重要な言葉に耳を傾けている状況です。",
    }

    if event_name and event_name in char_data["events"]:
        scene = scene_map.get(event_name, "")
        event_add = char_data["events"][event_name]["event_prompt_addition"].format(university_name=UNIVERSITY_NAME)
        base = scene + " " + event_add
    else:
        base = char_data["prompt"].format(university_name=UNIVERSITY_NAME)

    return (
        base
        + f" プレイヤーは{UNIVERSITY_PREF}の{UNIVERSITY_NAME}{PLAYER_MAJOR}{PLAYER_GRADE}です。"
        + f" プレイヤーの苗字は{st.session_state.player_lastname}、名前は{st.session_state.player_firstname}です。"
        + f" あなたはプレイヤーを現在「{call_name}」と呼んでいます。"
        + f" {gw_prompt}"
    )


def get_char_image(char_id, costume_key, emotion):
    images = st.session_state.characters[char_id]["images"]
    if costume_key in images and emotion in images[costume_key]:
        return images[costume_key][emotion]
    if emotion in images["normal"]:
        return images["normal"][emotion]
    return images["normal"]["normal"]


def show_scene(char_id, costume_key):
    emotion = st.session_state.get('current_character_emotion', 'normal')
    char_img = get_char_image(char_id, costume_key, emotion)
    bg = st.session_state.characters[char_id]["events"].get(
        st.session_state.current_event_name or "",
        {}
    ).get("background_image") or os.path.join(BASE_DIR, "images", "background", "university_campus.png")

    if os.path.exists(bg) and os.path.exists(char_img):
        combined = composite_multiple_characters(bg, [{"path": char_img, "position": (0.5, 0.9), "scale": 0.8}])
        if combined:
            with background_placeholder:
                st.image(combined, use_container_width=True)
            return
    if os.path.exists(bg):
        with background_placeholder:
            st.image(bg, use_container_width=True)


def show_chat_history(char_id):
    char_data = st.session_state.characters[char_id]
    icon = char_data["images"].get("icon")
    for turn in st.session_state.character_histories[char_id]:
        if turn['role'] == 'assistant':
            with st.chat_message("assistant", avatar=icon if icon and os.path.exists(icon) else None):
                st.write(turn['content'])
        else:
            with st.chat_message("user"):
                st.write(turn['content'])


def chat_turn(char_id, player_input, event_name=None):
    system_prompt = build_system_prompt(char_id, event_name)
    messages = [{"role": "system", "content": system_prompt}] \
               + st.session_state.character_histories[char_id] \
               + [{"role": "user", "content": player_input}]
    char_name = st.session_state.characters[char_id]["name"]
    with st.spinner(f"{char_name}が考え中..."):
        rsp = groq_client.chat.completions.create(model=GROQ_MODEL, messages=messages)
    ai_response = rsp.choices[0].message.content
    update_goodwill(char_id, player_input, ai_response)
    st.session_state.character_histories[char_id].append({"role": "user", "content": player_input})
    st.session_state.character_histories[char_id].append({"role": "assistant", "content": ai_response})
    st.session_state.current_character_emotion = evaluate_emotion(char_id, ai_response)
    return ai_response


def start_event_streamlit(event_name, char_id=None):
    st.session_state.event_active = True
    st.session_state.current_event_name = event_name
    st.session_state.processing_request = True

    if event_name == "encounter":
        char_order = ["erina"]
        st.session_state.current_char_id = char_order[st.session_state.encounter_char_index]

    else:
        if not char_id:
            st.error("キャラクターが特定できませんでした。")
            st.session_state.game_phase = "normal"
            st.session_state.processing_request = False
            st.rerun()
            return
        st.session_state.current_char_id = char_id

    current_char_id = st.session_state.current_char_id
    char_data = st.session_state.characters[current_char_id]
    event_info = char_data["events"][event_name]
    intro_messages = [event_info["initial_message"]]

    initial_dialogue = ""
    if event_name != "confession":
        sys_prompt = build_system_prompt(current_char_id, event_name)
        seed_msg = f"(シーン開始。{char_data['name']}として短い挨拶か問いかけを1回だけ行ってください。)"
        with st.spinner(f"{char_data['name']}が考え中..."):
            rsp = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": seed_msg}]
            )
        initial_dialogue = rsp.choices[0].message.content

    costume_key = event_name if event_name != "encounter" else "normal"
    char_img = get_char_image(current_char_id, costume_key, "normal")

    st.session_state.event_intro_data = {
        "event_name": event_name,
        "char_id": current_char_id,
        "intro_messages": intro_messages,
        "initial_character_dialogue": initial_dialogue,
        "background_path": event_info["background_image"],
        "character_image_path": char_img
    }
    st.session_state.game_phase = "event_introduction"
    st.session_state.current_character_emotion = "normal"
    st.session_state.processing_request = False
    st.rerun()


# --- サイドバー ---
with st.sidebar:
    st.header("ゲーム情報")
    st.write(f"フェーズ: **{st.session_state.game_phase}**")
    erina_gw = st.session_state.characters["erina"]["goodwill"]
    st.write(f"エリナ好感度: **{erina_gw}**")

    st.subheader("--- デバッグ ---")
    if st.button("ゲームリセット", key="debug_reset"):
        st.session_state.clear()
        st.rerun()

    def on_gw_slider_change():
        st.session_state.characters["erina"]["goodwill"] = st.session_state["debug_gw_slider"]

    st.session_state["debug_gw_slider"] = erina_gw  # 毎回現在の好感度に同期
    st.slider("好感度調整", -500, 500, key="debug_gw_slider", on_change=on_gw_slider_change)

# --- フェーズごとの描画 ---

if st.session_state.game_phase == "title_screen":
    st.markdown("<h1 style='text-align: center;'>恋愛シミュレーションゲーム</h1>", unsafe_allow_html=True)
    if os.path.exists(TITLE_IMAGE_PATH):
        result = composite_multiple_characters(
            TITLE_IMAGE_PATH,
            [{"path": os.path.join(BASE_DIR, "images", "erina", "normal", "normal.png"), "position": (0.5, 1.0), "scale": 0.8}]
        )
        if result:
            st.image(result, use_container_width=True)
    else:
        st.warning(f"タイトル画像が見つかりません: {TITLE_IMAGE_PATH}")
    st.markdown("<p style='text-align: center;'>あなたの青春が今、始まる</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        if st.button("ゲームスタート", disabled=st.session_state.processing_request):
            st.session_state.game_phase = "initial_setup"
            st.rerun()


elif st.session_state.game_phase == "initial_setup":
    st.subheader("あなたの情報を教えてください")
    ln = st.text_input("苗字：", value=st.session_state.get('player_lastname', ''))
    fn = st.text_input("名前：", value=st.session_state.get('player_firstname', ''))
    if ln and fn:
        st.session_state.player_lastname = ln
        st.session_state.player_firstname = fn
        st.session_state.player_name = f"{ln} {fn}"
        st.write(f"ようこそ、{st.session_state.player_name}さん！")
        if st.button("次へ", disabled=st.session_state.processing_request):
            st.session_state.game_phase = "encounter_start"
            st.rerun()
    else:
        st.write("苗字と名前を入力してください。")


elif st.session_state.game_phase == "encounter_start":
    start_event_streamlit("encounter")


elif st.session_state.game_phase == "event_introduction":
    display_conversation_log()
    intro = st.session_state.event_intro_data
    char_id = intro["char_id"]
    bg = intro["background_path"]
    char_img = intro["character_image_path"]

    if bg and os.path.exists(bg) and char_img and os.path.exists(char_img):
        combined = composite_multiple_characters(bg, [{"path": char_img, "position": (0.5, 0.9), "scale": 0.8}])
        if combined:
            with background_placeholder:
                st.image(combined, use_container_width=True)
    elif bg and os.path.exists(bg):
        with background_placeholder:
            st.image(bg, use_container_width=True)

    with dialogue_area_placeholder.container():
        st.subheader(f"--- {intro['event_name']}イベント開始！ ---")
        for msg in intro["intro_messages"]:
            st.write(msg)
        if st.button("会話に進む", disabled=st.session_state.processing_request):
            if intro["event_name"] == "confession":
                st.session_state.character_histories[char_id] = []
            else:
                st.session_state.character_histories[char_id] = [
                    {"role": "assistant", "content": intro["initial_character_dialogue"]}
                ]
            st.session_state.game_phase = (
                "encounter_in_progress" if intro["event_name"] == "encounter"
                else f"{intro['event_name']}_event"
            )
            st.rerun()


elif st.session_state.game_phase == "encounter_in_progress":
    display_conversation_log()
    char_id = "erina"
    show_scene(char_id, "normal")

    with dialogue_area_placeholder:
        st.subheader(f"{st.session_state.characters[char_id]['name']}との会話")
        show_chat_history(char_id)

    player_input = st.chat_input("ここにメッセージを入力...", key="chat_encounter", disabled=st.session_state.processing_request)
    if player_input:
        st.session_state.processing_request = True
        chat_turn(char_id, player_input, "encounter")
        st.session_state.processing_request = False
        st.rerun()

    if st.button("会話を終える", disabled=st.session_state.processing_request):
        st.session_state.event_active = False
        st.session_state.game_phase = "normal"
        st.session_state.current_char_id = None
        st.session_state.current_event_name = None
        st.session_state.current_character_emotion = "normal"
        st.rerun()


elif st.session_state.game_phase == "normal":
    display_conversation_log()
    background_placeholder.empty()
    character_image_placeholder.empty()

    event_order = ["hanami", "natsumatsuri", "christmas", "confession"]

    with st.container():
        if st.session_state.event_phase_index < len(event_order):
            current_event = event_order[st.session_state.event_phase_index]
            st.markdown(f"### 次のイベント：『{current_event}』")
            if st.session_state.event_phase_index == len(event_order) - 1:
                st.markdown("最終イベントです。エリナに告白しましょう。")
            required_gw = st.session_state.event_conditions[current_event]["erina"]
            actual_gw = st.session_state.characters["erina"]["goodwill"]
            if st.button(f"エリナを誘う（必要好感度: {required_gw}）", key="start_event_btn"):
                if actual_gw >= required_gw:
                    st.session_state.triggered_events.add(current_event)
                    start_event_streamlit(current_event, "erina")
                else:
                    st.warning(f"好感度が足りません（現在: {actual_gw} / 必要: {required_gw}）")
        else:
            if st.button("エンディングを見る", key="go_ending"):
                st.session_state.game_phase = "ending"
                st.rerun()

        st.write("---")
        if st.button("エリナと自由に会話する", key="goto_freechat"):
            st.session_state.current_char_id = "erina"
            st.session_state.game_phase = "free_chat"
            st.session_state.current_character_emotion = "normal"
            st.rerun()


elif st.session_state.game_phase == "free_chat":
    display_conversation_log()
    char_id = "erina"
    show_scene(char_id, "normal")

    with dialogue_area_placeholder:
        st.subheader(f"{st.session_state.characters[char_id]['name']}との会話")
        show_chat_history(char_id)

    player_input = st.chat_input("ここにメッセージを入力...", key="chat_free", disabled=st.session_state.processing_request)
    if player_input:
        st.session_state.processing_request = True
        chat_turn(char_id, player_input)
        st.session_state.processing_request = False
        st.rerun()

    if st.button("会話終了", key="end_free_chat", disabled=st.session_state.processing_request):
        st.session_state.current_char_id = None
        st.session_state.game_phase = "normal"
        st.session_state.current_character_emotion = "normal"
        st.rerun()


elif st.session_state.game_phase.endswith("_event"):
    display_conversation_log()
    char_id = st.session_state.current_char_id
    event_name = st.session_state.current_event_name
    show_scene(char_id, event_name)

    with dialogue_area_placeholder:
        st.subheader(f"{event_name}イベント: {st.session_state.characters[char_id]['name']}との会話")
        show_chat_history(char_id)

    player_input = st.chat_input("ここにメッセージを入力...", key="chat_event", disabled=st.session_state.processing_request)
    if player_input:
        st.session_state.processing_request = True
        ai_response = chat_turn(char_id, player_input, event_name)
        st.session_state.latest_user_input = player_input
        st.session_state.latest_ai_response = ai_response
        st.session_state.processing_request = False
        st.rerun()

    if st.button("イベント終了", key=f"end_event_{event_name}", disabled=st.session_state.processing_request):
        if event_name == "confession":
            lu = st.session_state.pop("latest_user_input", None)
            la = st.session_state.pop("latest_ai_response", None)
            if lu and la and evaluate_confession(lu, la):
                st.session_state.characters[char_id]["flags"]["confessed"] = True

        st.session_state.event_active = False
        st.session_state.current_char_id = None
        st.session_state.current_event_name = None
        st.session_state.current_character_emotion = "normal"
        st.session_state.event_phase_index += 1
        st.session_state.game_phase = "ending" if event_name == "confession" else "normal"
        st.rerun()


if st.session_state.game_phase == "ending":
    st.subheader("エンディング")
    determine_ending()
    history = st.session_state.goodwill_history.get("erina", [])
    if history:
        st.subheader("エリナとの好感度の推移")
        st.line_chart({"森本エリナ": history})
    else:
        st.info("好感度履歴がありません。")