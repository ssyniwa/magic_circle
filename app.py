import os
from PIL import Image
import streamlit as st

# ページ基本設定
st.set_page_config(
    page_title="魔法陣構築 RPG App", page_icon="🔮", layout="wide"
)

# 定数定義
ATTRIBUTES = ["炎", "水", "風", "地", "光", "闇"]
WEAPON_TYPES = ["剣", "杖", "弓", "盾", "槍"]
LEVELS = ["初級", "中級", "上級", "王級", "神級"]
LEVEL_MULTIPLIERS = {"初級": 1.0, "中級": 1.5, "上級": 2.2, "王級": 3.0, "神級": 4.5}
STATS = ["HP", "攻撃力", "防御力", "回復力"]


# 画像読み込み補助関数
def load_image(path, width=80):
  if os.path.exists(path):
    try:
      img = Image.open(path)
      return img
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
        "img": f"images/enemy_boss.png",
    })
  st.session_state.enemies = enemies


if not st.session_state.available_parts and st.session_state.phase == "generate":
  generate_stage_parts()

# --- UI デザイン・カスタムCSS ---
st.markdown(
    """
    <style>
    .main-title { text-align: center; color: #6C63FF; font-family: 'Helvetica', sans-serif; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; margin-bottom: 10px; }
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
      "ドロップした15個の魔法陣部品を確認し、3つの強力な武器を構築してください。"
  )

  parts = st.session_state.available_parts

  st.markdown("#### 🎁 今回ドロップした魔法陣部品一覧")
  c1, c2, c3, c4 = st.columns(4)

  with c1:
    st.markdown("**属性部品 (6個)**")
    for a in parts["attr"]:
      img = load_image(f"images/attr_{a}.png")
      if img:
        st.image(img, width=40, caption=a)
      else:
        st.info(f"✨ {a}")

  with c2:
    st.markdown("**武器種部品 (3個)**")
    for t in parts["type"]:
      img = load_image(f"images/type_{t}.png")
      if img:
        st.image(img, width=40, caption=t)
      else:
        st.info(f"⚔️ {t}")

  with c3:
    st.markdown("**レベル部品 (3個)**")
    for l in parts["level"]:
      img = load_image(f"images/level_{l}.png")
      if img:
        st.image(img, width=40, caption=l)
      else:
        st.info(f"🌟 {l}")

  with c4:
    st.markdown("**ステータス部品 (3個)**")
    for s in parts["stat"]:
      img = load_image(f"images/stat_{s}.png")
      if img:
        st.image(img, width=40, caption=s)
      else:
        st.info(f"📈 {s}")

  st.markdown("---")
  st.subheader("🛠️ 魔法陣の組み合わせによる武器のクラフト")

  col_w1, col_w2, col_w3 = st.columns(3)

  with col_w1:
    st.markdown("##### 武器 1")
    w1_a1 = st.selectbox("属性1 (コア)", ATTRIBUTES, key="w1_a1")
    w1_a2 = st.selectbox("属性2 (コア)", ATTRIBUTES, key="w1_a2")
    w1_type = st.selectbox("武器種", WEAPON_TYPES, key="w1_t")
    w1_lvl = st.selectbox("レベル", LEVELS, key="w1_l")
    w1_stat = st.selectbox("強化ステータス", STATS, key="w1_s")
    # プレビュー画像表示
    w1_img_path = f"images/weapon_{w1_type}_{w1_lvl}.png"
    img1 = load_image(w1_img_path, width=70)
    if img1:
      st.image(img1, width=70, caption="生成予定武器")

  with col_w2:
    st.markdown("##### 武器 2")
    w2_a1 = st.selectbox("属性1 (コア)", ATTRIBUTES, key="w2_a1")
    w2_a2 = st.selectbox("属性2 (コア)", ATTRIBUTES, key="w2_a2")
    w2_type = st.selectbox("武器種", WEAPON_TYPES, key="w2_t")
    w2_lvl = st.selectbox("レベル", LEVELS, key="w2_l")
    w2_stat = st.selectbox("強化ステータス", STATS, key="w2_s")
    w2_img_path = f"images/weapon_{w2_type}_{w2_lvl}.png"
    img2 = load_image(w2_img_path, width=70)
    if img2:
      st.image(img2, width=70, caption="生成予定武器")

  with col_w3:
    st.markdown("##### 武器 3")
    w3_a1 = st.selectbox("属性1 (コア)", ATTRIBUTES, key="w3_a1")
    w3_a2 = st.selectbox("属性2 (コア)", ATTRIBUTES, key="w3_a2")
    w3_type = st.selectbox("武器種", WEAPON_TYPES, key="w3_t")
    w3_lvl = st.selectbox("レベル", LEVELS, key="w3_l")
    w3_stat = st.selectbox("強化ステータス", STATS, key="w3_s")
    w3_img_path = f"images/weapon_{w3_type}_{w3_lvl}.png"
    img3 = load_image(w3_img_path, width=70)
    if img3:
      st.image(img3, width=70, caption="生成予定武器")

  st.markdown("<br>", unsafe_allow_html=True)
  if st.button("✨ 武器を生成して装備フェーズへ進む", type="primary"):
    st.session_state.crafted_weapons = [
        {
            "name": f"{w1_a1}・{w1_a2}の{w1_lvl}{w1_type}",
            "type": w1_type,
            "level": w1_lvl,
            "stat": w1_stat,
            "value": int(15 * LEVEL_MULTIPLIERS[w1_lvl]),
            "img": f"images/weapon_{w1_type}_{w1_lvl}.png",
        },
        {
            "name": f"{w2_a1}・{w2_a2}の{w2_lvl}{w2_type}",
            "type": w2_type,
            "level": w2_lvl,
            "stat": w2_stat,
            "value": int(15 * LEVEL_MULTIPLIERS[w2_lvl]),
            "img": f"images/weapon_{w2_type}_{w2_lvl}.png",
        },
        {
            "name": f"{w3_a1}・{w3_a2}の{w3_lvl}{w3_type}",
            "type": w3_type,
            "level": w3_lvl,
            "stat": w3_stat,
            "value": int(15 * LEVEL_MULTIPLIERS[w3_lvl]),
            "img": f"images/weapon_{w3_type}_{w3_lvl}.png",
        },
    ]
    st.session_state.phase = "equip"
    st.rerun()

# ==========================================
# フェーズ 2: 装備フェーズ
# ==========================================
elif st.session_state.phase == "equip":
  st.subheader("🛡️ キャラクター装備フェーズ")
  st.write("作成した3つの武器を味方パーティーの3人に割り当てます。")

  weapons = st.session_state.crafted_weapons
  weapon_options = {w["name"]: w for w in weapons}
  w_names = list(weapon_options.keys())

  cols = st.columns(3)
  assigned_weapons = []

  for idx, p in enumerate(st.session_state.players):
    with cols[idx]:
      st.markdown(f"<div class='card'>", unsafe_allow_html=True)
      p_img = load_image(p["img"], width=90)
      if p_img:
        st.image(p_img, width=90)
      else:
        st.markdown(f"### 🛡️ {p['name']}")

      st.write(
          f"ATK: {p['atk']} / DEF: {p['def']} / REC: {p['rec']}"
      )
      selected_w_name = st.selectbox(
          f"装備武器選択", w_names, key=f"equip_{idx}"
      )
      chosen_weapon = weapon_options[selected_w_name]
      assigned_weapons.append(chosen_weapon)

      # 選択中武器の画像表示
      w_img = load_image(chosen_weapon["img"], width=60)
      if w_img:
        st.image(w_img, width=60, caption=chosen_weapon["name"])
      else:
        st.caption(f"武器: {chosen_weapon['name']}")

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
      p_img = load_image(p["img"], width=50)
      hp_ratio = max(0, min(1, p["hp"] / p["max_hp"]))
      w = p["weapon"]
      w_img = load_image(w["img"], width=30) if w else None

      st.markdown(f"<div class='card'>", unsafe_allow_html=True)
      pc1, pc2, pc3 = st.columns([1, 1, 2])
      with pc1:
        if p_img:
          st.image(p_img, width=50)
        else:
          st.write("👤")
      with pc2:
        if w_img:
          st.image(w_img, width=35, caption="装備中")
        else:
          st.write("⚔️")
      with pc3:
        st.markdown(f"**{p['name']}**<br><small>{w['name']}</small>", unsafe_allow_html=True)
        st.progress(
            hp_ratio, text=f"HP: {max(0, p['hp'])} / {p['max_hp']}"
        )
      st.markdown("</div>", unsafe_allow_html=True)

  with col_e:
    st.markdown("### 🔴 エネミーチーム")
    for e in st.session_state.enemies:
      e_img = load_image(e["img"], width=50)
      hp_ratio = max(0, min(1, e["hp"] / e["max_hp"]))

      st.markdown(f"<div class='card'>", unsafe_allow_html=True)
      ec1, ec2 = st.columns([1, 3])
      with ec1:
        if e_img:
          st.image(e_img, width=50)
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
