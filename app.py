import os
from PIL import Image
import streamlit as st

# ページ基本設定
st.set_page_config(
    page_title="魔法陣構築 RPG App", page_icon="🔮", layout="wide"
)

# 定数定義
ATTRIBUTES = ["炎", "水", "風", "地", "光", "闇"]
WEAPON_TYPES = ["剣", "杖", "弓", "槍"]
LEVELS = ["初級", "中級", "上級", "王級", "神級"]
LEVEL_MULTIPLIERS = {"初級": 1.0, "中級": 1.5, "上級": 2.2, "王級": 3.0, "神級": 4.5}
STATS = ["HP", "攻撃力", "防御力", "回復力"]


# 画像読み込み補助関数
def load_image(path, width=80):
  if os.path.exists(path):
    try:
      return Image.open(path)
    except Exception:
      pass
  return None


# セッション状態の初期化
if "stage" not in st.session_state:
  st.session_state.stage = 1
  st.session_state.phase = "generate"  # generate, equip, battle, gameover, clear
  st.session_state.players = [
      {
          "name": "戦士アレン",
          "hp": 120,
          "max_hp": 120,
          "atk": 25,
          "def": 15,
          "rec": 5,
          "weapon": None,
          "img": "images/player_アレン.png",
      },
      {
          "name": "魔導士リリア",
          "hp": 90,
          "max_hp": 90,
          "atk": 30,
          "def": 8,
          "rec": 20,
          "weapon": None,
          "img": "images/player_リリア.png",
      },
      {
          "name": "騎士レオン",
          "hp": 150,
          "max_hp": 150,
          "atk": 18,
          "def": 25,
          "rec": 10,
          "weapon": None,
          "img": "images/player_レオン.png",
      },
  ]
  st.session_state.enemies = []
  st.session_state.available_parts = {}
  st.session_state.crafted_weapons = []
  st.session_state.battle_log = []


def generate_stage_parts():
  import random

  # 属性6個、他3個ずつ：計15個
  st.session_state.available_parts = {
      "attr": random.choices(ATTRIBUTES, k=6),
      "type": random.choices(WEAPON_TYPES, k=3),
      "level": random.choices(LEVELS, k=3),
      "stat": random.choices(STATS, k=3),
  }


def generate_enemies():
  import random

  stage = st.session_state.stage
  enemies = []
  for i in range(3):
    e_hp = 70 + stage * 30
    enemies.append({
        "name": f"魔物 Lv.{stage}-{i+1}",
        "hp": e_hp,
        "max_hp": e_hp,
        "atk": 18 + stage * 5,
        "def": 6 + stage * 2,
        "img": "images/enemy_boss.png",
    })
  st.session_state.enemies = enemies


if not st.session_state.available_parts and st.session_state.phase == "generate":
  generate_stage_parts()

# --- カスタムCSS ---
st.markdown(
    """
    <style>
    .main-title { text-align: center; color: #6C63FF; font-family: 'Helvetica', sans-serif; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; margin-bottom: 10px; }
    .magic-slot { background: linear-gradient(135deg, #1f4068, #162447); padding: 15px; border-radius: 12px; color: white; border: 2px solid #e43f5a; margin-bottom: 15px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"<h1 class='main-title'>🔮 魔法陣構築 RPG (ステージ {st.session_state.stage} /"
    " 10)</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ==========================================
# フェーズ 1: 武器生成フェーズ
# ==========================================
if st.session_state.phase == "generate":
  st.subheader("⚙️ 魔法陣構築・武器生成フェーズ")
  st.write(
      "ドロップした15個の部品を組み合わせて、3つの円形魔法陣と武器を構築してください。"
  )

  parts = st.session_state.available_parts

  # ドロップ部品の一覧表示
  st.markdown("#### 🎁 今回ドロップした魔法陣部品一覧")
  c1, c2, c3, c4 = st.columns(4)

  with c1:
    st.markdown("**属性部品 (6個)**")
    for a in parts["attr"]:
      img = load_image(f"images/attr_{a}.png")
      if img:
        st.image(img, width=35, caption=a)
      else:
        st.info(f"✨ {a}")

  with c2:
    st.markdown("**武器種部品 (3個)**")
    for t in parts["type"]:
      img = load_image(f"images/type_{t}.png")
      if img:
        st.image(img, width=35, caption=t)
      else:
        st.info(f"⚔️ {t}")

  with c3:
    st.markdown("**レベル部品 (3個)**")
    for l in parts["level"]:
      img = load_image(f"images/level_{l}.png")
      if img:
        st.image(img, width=35, caption=l)
      else:
        st.info(f"🌟 {l}")

  with c4:
    st.markdown("**ステータス部品 (3個)**")
    for s in parts["stat"]:
      img = load_image(f"images/stat_{s}.png")
      if img:
        st.image(img, width=35, caption=s)
      else:
        st.info(f"📈 {s}")

  st.markdown("---")
  st.subheader("🌀 円形魔法陣の構築と武器プレビュー")

  col_w1, col_w2, col_w3 = st.columns(3)

  # 共通の構築入力関数
  def render_magic_slot(slot_num):
    st.markdown(
        f"<div class='magic-slot'><h5>🔮 魔法陣スロット #{slot_num}</h5>",
        unsafe_allow_html=True,
    )
    st.markdown("<b>【中央コア】2色属性</b>", unsafe_allow_html=True)
    a1 = st.selectbox("属性 1 (コア)", ATTRIBUTES, key=f"w{slot_num}_a1")
    a2 = st.selectbox("属性 2 (コア)", ATTRIBUTES, key=f"w{slot_num}_a2")

    st.markdown(
        "<b>【外周リング】武器・レベル・強化</b>", unsafe_allow_html=True
    )
    w_type = st.selectbox("武器種", WEAPON_TYPES, key=f"w{slot_num}_t")
    w_lvl = st.selectbox("レベル", LEVELS, key=f"w{slot_num}_l")
    w_stat = st.selectbox("強化ステータス", STATS, key=f"w{slot_num}_s")

    # プレビュー表示（魔法陣の完成形 ＆ 武器画像）
    st.markdown("---")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
      # 完成形魔法陣画像（共通ベースまたは属性別画像）
      circle_img_path = f"images/magic_circle_{a1}_{a2}.png"
      if not os.path.exists(circle_img_path):
        circle_img_path = "images/magic_circle_base.png"
      c_img = load_image(circle_img_path, width=70)
      if c_img:
        st.image(c_img, width=70, caption="完成魔法陣")
      else:
        st.write("🌐 [魔法陣陣形]")

    with p_col2:
      # 武器画像
      weapon_img_path = f"images/weapon_{w_type}_{w_lvl}.png"
      w_img = load_image(weapon_img_path, width=70)
      if w_img:
        st.image(w_img, width=70, caption="生成武器")
      else:
        st.write(f"⚔️ {w_lvl}{w_type}")

    st.markdown("</div>", unsafe_allow_html=True)
    return {
        "name": f"{a1}・{a2}の{w_lvl}{w_type}",
        "type": w_type,
        "level": w_lvl,
        "stat": w_stat,
        "value": int(15 * LEVEL_MULTIPLIERS[w_lvl]),
        "circle_img": circle_img_path,
        "weapon_img": weapon_img_path,
    }

  with col_w1:
    w1 = render_magic_slot(1)
  with col_w2:
    w2 = render_magic_slot(2)
  with col_w3:
    w3 = render_magic_slot(3)

  st.markdown("<br>", unsafe_allow_html=True)
  if st.button(
      "✨ 3つの魔法陣を起動し、武器を生成して装備フェーズへ", type="primary"
  ):
    st.session_state.crafted_weapons = [w1, w2, w3]
    st.session_state.phase = "equip"
    st.rerun()

# ==========================================
# フェーズ 2: 装備フェーズ
# ==========================================
elif st.session_state.phase == "equip":
  st.subheader("🛡️ キャラクター装備フェーズ")
  st.write(
      "構築した魔法陣から生まれた武器と魔法陣を、味方パーティーの3人に割り当てます。"
  )

  weapons = st.session_state.crafted_weapons
  weapon_options = {w["name"]: w for w in weapons}
  w_names = list(weapon_options.keys())

  cols = st.columns(3)
  assigned_weapons = []

  for idx, p in enumerate(st.session_state.players):
    with cols[idx]:
      st.markdown(f"<div class='card'>", unsafe_allow_html=True)
      p_img = load_image(p["img"], width=80)
      if p_img:
        st.image(p_img, width=80)
      else:
        st.markdown(f"### 🛡️ {p['name']}")

      st.write(
          f"基礎 ATK: {p['atk']} / DEF: {p['def']} / REC: {p['rec']}"
      )
      selected_w_name = st.selectbox(
          f"装備選択", w_names, key=f"equip_{idx}"
      )
      chosen_weapon = weapon_options[selected_w_name]
      assigned_weapons.append(chosen_weapon)

      # 魔法陣と武器の画像を並べて表示
      img_col1, img_col2 = st.columns(2)
      with img_col1:
        c_img = load_image(chosen_weapon["circle_img"], width=50)
        if c_img:
          st.image(c_img, width=50, caption="陣")
      with img_col2:
        w_img = load_image(chosen_weapon["weapon_img"], width=50)
        if w_img:
          st.image(w_img, width=50, caption="武器")

      st.markdown(f"<small><b>{chosen_weapon['name']}</b></small>", unsafe_allow_html=True)
      st.markdown("</div>", unsafe_allow_html=True)

  if st.button("🚀 バトルフェーズへ突入！", type="primary"):
    for i, p in enumerate(st.session_state.players):
      w = assigned_weapons[i]
      p["weapon"] = w
      if w["stat"] == "HP":
        p["max_hp"] += w["value"] * 4
        p["hp"] = p["max_hp"]
      elif w["stat"] == "攻撃力":
        p["atk"] += w["value"]
      elif w["stat"] == "防御力":
        p["def"] += w["value"]
      elif w["stat"] == "回復力":
        p["rec"] += w["value"]

    generate_enemies()
    st.session_state.phase = "battle"
    st.session_state.battle_log = ["⚔️ バトルが開始されました！"]
    st.rerun()

# ==========================================
# フェーズ 3: バトルフェーズ (3対3)
# ==========================================
elif st.session_state.phase == "battle":
  st.subheader("⚔️ 3対3 バトルフェーズ")

  col_p, col_e = st.columns(2)

  with col_p:
    st.markdown("### 🔵 プレイヤーチーム")
    for p in st.session_state.players:
      p_img = load_image(p["img"], width=45)
      hp_ratio = max(0, min(1, p["hp"] / p["max_hp"]))
      w = p["weapon"]
      w_img = load_image(w["weapon_img"], width=30) if w else None
      c_img = load_image(w["circle_img"], width=30) if w else None

      st.markdown(f"<div class='card'>", unsafe_allow_html=True)
      pc1, pc2, pc3, pc4 = st.columns([1, 1, 1, 2])
      with pc1:
        if p_img:
          st.image(p_img, width=45)
        else:
          st.write("👤")
      with pc2:
        if c_img:
          st.image(c_img, width=30, caption="陣")
      with pc3:
        if w_img:
          st.image(w_img, width=30, caption="武")
      with pc4:
        st.markdown(f"**{p['name']}**<br><small>{w['name']}</small>", unsafe_allow_html=True)
        st.progress(
            hp_ratio, text=f"HP: {max(0, p['hp'])} / {p['max_hp']}"
        )
      st.markdown("</div>", unsafe_allow_html=True)

  with col_e:
    st.markdown("### 🔴 エネミーチーム")
    for e in st.session_state.enemies:
      e_img = load_image(e["img"], width=45)
      hp_ratio = max(0, min(1, e["hp"] / e["max_hp"]))

      st.markdown(f"<div class='card'>", unsafe_allow_html=True)
      ec1, ec2 = st.columns([1, 3])
      with ec1:
        if e_img:
          st.image(e_img, width=45)
        else:
          st.write("👾")
      with ec2:
        if e["hp"] > 0:
          st.markdown(f"**{e['name']}**")
          st.progress(
              hp_ratio, text=f"HP: {max(0, e['hp'])} / {e['max_hp']}"
          )
        else:
          st.markdown(f"~~{e['name']}~~ **【戦闘不能】**")
      st.markdown("</div>", unsafe_allow_html=True)

  st.markdown("---")

  if st.button("⚔️ ターン進行 (攻撃＆回復)", type="primary"):
    import random

    logs = []
    for p in st.session_state.players:
      if p["hp"] > 0:
        living_enemies = [e for e in st.session_state.enemies if e["hp"] > 0]
        if living_enemies:
          target = random.choice(living_enemies)
          dmg = max(5, p["atk"] - target["def"] // 3)
          target["hp"] = max(0, target["hp"] - dmg)
          logs.append(f"🟢 {p['name']} の攻撃！ {target['name']} に {dmg} のダメージ！")

    for e in st.session_state.enemies:
      if e["hp"] > 0:
        living_players = [pl for pl in st.session_state.players if pl["hp"] > 0]
        if living_players:
          target = random.choice(living_players)
          dmg = max(4, e["atk"] - target["def"] // 3)
          target["hp"] = max(0, target["hp"] - dmg)
          logs.append(f"🔴 {e['name']} の反撃！ {target['name']} に {dmg} のダメージ！")

    for p in st.session_state.players:
      if p["hp"] > 0 and p["rec"] > 0:
        living_players = [pl for pl in st.session_state.players if pl["hp"] > 0]
        if living_players:
          target = min(living_players, key=lambda x: x["hp"] / x["max_hp"])
          heal = p["rec"]
          target["hp"] = min(target["max_hp"], target["hp"] + heal)
          logs.append(
              f"✨ {p['name']} の治癒スキル！ {target['name']} のHPが {heal}"
              " 回復した！"
          )

    st.session_state.battle_log.extend(logs)

    all_enemies_dead = all(e["hp"] <= 0 for e in st.session_state.enemies)
    all_players_dead = all(p["hp"] <= 0 for p in st.session_state.players)

    if all_enemies_dead:
      if st.session_state.stage >= 10:
        st.session_state.phase = "clear"
      else:
        st.session_state.stage += 1
        st.session_state.phase = "generate"
        st.session_state.available_parts = {}
        for p in st.session_state.players:
          p["hp"] = p["max_hp"]
      st.rerun()
    elif all_players_dead:
      st.session_state.phase = "gameover"
      st.rerun()

  st.markdown("### 📜 戦闘ログ")
  log_container = st.container(height=200)
  with log_container:
    for log in reversed(st.session_state.battle_log[-12:]):
      st.text(log)

# ==========================================
# ゲームオーバー画面
# ==========================================
elif st.session_state.phase == "gameover":
  st.error(
      "💀 ゲームオーバー... パーティーが全滅してしまいました。世界に闇が訪れる..."
  )
  if st.button("🔄 最初から挑戦し直す"):
    st.session_state.clear()
    st.rerun()

# ==========================================
# クリア画面
# ==========================================
elif st.session_state.phase == "clear":
  st.balloons()
  st.success(
      "🎉 祝・全10ステージ完全クリア！！ 究極の魔法陣を極め、世界を救うことに成功しました！"
  )
  if st.button("🏆 もう一度最初から遊ぶ"):
    st.session_state.clear()
    st.rerun()
