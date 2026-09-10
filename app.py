import os
import random
from PIL import Image
import streamlit as st

# ページ基本設定
st.set_page_config(
    page_title="魔法陣構築 RPG App", page_icon="🔮", layout="wide"
)

# 定数定義
ATTRIBUTES = ["炎", "水", "風", "土", "光", "闇"]
WEAPON_TYPES = ["剣", "杖", "弓", "槍"]
LEVELS = ["初級", "中級", "上級", "王級", "神級"]
LEVEL_MULTIPLIERS = {"初級": 1.0, "中級": 1.5, "上級": 2.2, "王級": 3.0, "神級": 4.5}
STATS = ["HP", "攻撃力", "防御力", "回復力"]


# 画像読み込み補助関数 (.jpg対応)
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
          "img": "images/player_アレン.jpg",
      },
      {
          "name": "魔導士リリア",
          "hp": 90,
          "max_hp": 90,
          "atk": 30,
          "def": 8,
          "rec": 20,
          "weapon": None,
          "img": "images/player_リリア.jpg",
      },
      {
          "name": "騎士レオン",
          "hp": 150,
          "max_hp": 150,
          "atk": 18,
          "def": 25,
          "rec": 10,
          "weapon": None,
          "img": "images/player_レオン.jpg",
      },
  ]
  st.session_state.enemies = []
  st.session_state.available_parts = {}
  st.session_state.crafted_weapons = []
  st.session_state.battle_log = []


def generate_stage1_parts():
  # 異なる2つの属性をランダムに選ぶ（例として2つチョイス、あるいは重複なしのペアなど）
  selected_attrs = random.sample(ATTRIBUTES, 2)
  st.session_state.available_parts = {
      "attr": selected_attrs,
      "type": random.choices(WEAPON_TYPES, k=3),
      "level": ["初級", "初級", "初級"],
  }


def generate_enemies():
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
        "img": "images/enemy_boss.jpg",
    })
  st.session_state.enemies = enemies


if not st.session_state.available_parts and st.session_state.phase == "generate":
  if st.session_state.stage == 1:
    generate_stage1_parts()

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
# フェーズ 1: 武器生成・強化フェーズ
# ==========================================
if st.session_state.phase == "generate":
  if st.session_state.stage == 1:
    st.subheader("⚙️ ステージ1：初期魔法陣構築・武器生成フェーズ")
    st.write(
        "ドロップした初級の部品と2つの属性を組み合わせて、3つの円形魔法陣と初期武器を構築してください。"
    )

    parts = st.session_state.available_parts

    st.markdown("#### 🎁 ステージ1 ドロップ部品")
    c1, c2, c3 = st.columns(3)

    with c1:
      st.markdown("**属性部品 (固定2種)**")
      for a in parts["attr"]:
        st.info(f"✨ {a}")

    with c2:
      st.markdown("**武器種部品 (3個)**")
      for t in parts["type"]:
        st.info(f"⚔️ {t}")

    with c3:
      st.markdown("**レベル部品**")
      st.info("🌟 初級 (固定)")

    st.markdown("---")
    st.subheader("🌀 円形魔法陣の構築と武器プレビュー")

    col_w1, col_w2, col_w3 = st.columns(3)

    def render_magic_slot(slot_num):
      st.markdown(
          f"<div class='magic-slot'><h5>🔮 魔法陣スロット #{slot_num}</h5>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<b>【中央コア】ドロップした2属性から選択</b>", unsafe_allow_html=True
      )
      a1 = st.selectbox("属性 1 (コア)", parts["attr"], key=f"w{slot_num}_a1")
      a2 = st.selectbox("属性 2 (コア)", parts["attr"], key=f"w{slot_num}_a2")

      st.markdown("<b>【外周リング】武器・レベル</b>", unsafe_allow_html=True)
      # 武器種はドロップした3つから選択
      w_type = st.selectbox(
          "武器種", parts["type"], key=f"w{slot_num}_t"
      )
      w_lvl = "初級"
      st.write(f"レベル: **{w_lvl}**")

      circle_img_path = f"images/magic_circle_{a1}_{a2}_{w_type}_{w_lvl}.jpg"
      if not os.path.exists(circle_img_path):
        circle_img_path = "images/magic_circle_base.jpg"

      weapon_img_path = f"images/weapon_{a1}_{a2}_{w_type}_{w_lvl}.jpg"
      if not os.path.exists(weapon_img_path):
        fallback_path = f"images/weapon_{w_type}_{w_lvl}.jpg"
        weapon_img_path = (
            fallback_path if os.path.exists(fallback_path) else weapon_img_path
        )

      st.markdown("---")
      p_col1, p_col2 = st.columns(2)
      with p_col1:
        c_img = load_image(circle_img_path, width=200)
        if c_img:
          st.image(c_img, width=200, caption="完成魔法陣")
        else:
          st.write("🌐 [魔法陣陣形]")
      with p_col2:
        w_img = load_image(weapon_img_path, width=200)
        if w_img:
          st.image(w_img, width=200, caption="生成武器")
        else:
          st.write(f"⚔️ {w_lvl}{w_type}")

      st.markdown("</div>", unsafe_allow_html=True)

      return {
          "a1": a1,
          "a2": a2,
          "type": w_type,
          "level": w_lvl,
          "circle_img": circle_img_path,
          "weapon_img": weapon_img_path,
      }

    with col_w1:
      raw_w1 = render_magic_slot(1)
    with col_w2:
      raw_w2 = render_magic_slot(2)
    with col_w3:
      raw_w3 = render_magic_slot(3)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(
        "✨ 3つの魔法陣を起動し、初期武器を生成して装備フェーズへ",
        type="primary",
    ):
      crafted = []
      for raw in [raw_w1, raw_w2, raw_w3]:
        rand_stat = random.choice(STATS)
        base_val = random.randint(5, 15)
        val = int(base_val * LEVEL_MULTIPLIERS[raw["level"]])

        crafted.append({
            "name": f"{raw['a1']}・{raw['a2']}の{raw['level']}{raw['type']}",
            "type": raw["type"],
            "level": raw["level"],
            "stat": rand_stat,
            "value": val,
            "circle_img": raw["circle_img"],
            "weapon_img": raw["weapon_img"],
        })

      st.session_state.crafted_weapons = crafted
      st.session_state.phase = "equip"
      st.rerun()

  else:
    # ステージ2以降：武器のレベルを1段階上げるフェーズ
    st.subheader(f"🛠️ ステージ {st.session_state.stage}：武器レベルアップフェーズ")
    st.write(
        "保有している3つの武器から1つを選び、レベルを1段階アップグレードしてください。"
    )

    weapons = st.session_state.crafted_weapons
    weapon_options = {
        f"{w['name']} (Lv:{w['level']} / 効果:{w['stat']}+{w['value']})": i
        for i, w in enumerate(weapons)
    }

    selected_desc = st.selectbox(
        "レベルアップさせる武器を選択", list(weapon_options.keys())
    )
    target_idx = weapon_options[selected_desc]
    target_weapon = weapons[target_idx]

    current_lvl = target_weapon["level"]
    lvl_list = LEVELS
    curr_idx = lvl_list.index(current_lvl)

    if curr_idx < len(lvl_list) - 1:
      next_lvl = lvl_list[curr_idx + 1]
    else:
      next_lvl = current_lvl  # すでに最高ランク

    st.markdown(f"**選択中の武器:** {target_weapon['name']}")
    st.write(
        f"現在のレベル: **{current_lvl}** ➔ アップグレード後のレベル: **{next_lvl}**"
    )

    if st.button("⬆️ 武器のレベルを1段階上げる", type="primary"):
      if next_lvl != current_lvl:
        target_weapon["level"] = next_lvl
        # レベルアップに伴い効果値も再計算・上昇
        base_val = target_weapon["value"] / LEVEL_MULTIPLIERS[current_lvl]
        target_weapon["value"] = int(base_val * LEVEL_MULTIPLIERS[next_lvl])

        # 名前や画像パスの更新処理
        parts_name = target_weapon["name"].split("の")
        attrs = parts_name[0]
        w_type = target_weapon["type"]
        target_weapon["name"] = f"{attrs}の{next_lvl}{w_type}"

        # 属性名の分割（例: "炎・水" -> a1="炎", a2="水"）
        attr_split = attrs.split("・")
        a1 = attr_split[0]
        a2 = attr_split[1] if len(attr_split) > 1 else a1

        circle_img_path = f"images/magic_circle_{a1}_{a2}_{w_type}_{next_lvl}.jpg"
        if os.path.exists(circle_img_path):
          target_weapon["circle_img"] = circle_img_path

        weapon_img_path = f"images/weapon_{a1}_{a2}_{w_type}_{next_lvl}.jpg"
        if os.path.exists(weapon_img_path):
          target_weapon["weapon_img"] = weapon_img_path

      st.session_state.phase = "equip"
      st.rerun()

# ==========================================
# フェーズ 2: 装備フェーズ
# ==========================================
elif st.session_state.phase == "equip":
  st.subheader("🛡️ キャラクター装備フェーズ")
  st.write(
      "構築・強化された武器と魔法陣を、味方パーティーの3人に割り当てます。"
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

      # 既に装備していればデフォルトで選択状態にする
      default_idx = 0
      if p["weapon"] and p["weapon"]["name"] in w_names:
        default_idx = w_names.index(p["weapon"]["name"])

      selected_w_name = st.selectbox(
          f"装備選択", w_names, index=default_idx, key=f"equip_{idx}"
      )
      chosen_weapon = weapon_options[selected_w_name]
      assigned_weapons.append(chosen_weapon)

      img_col1, img_col2 = st.columns(2)
      with img_col1:
        c_img = load_image(chosen_weapon["circle_img"], width=50)
        if c_img:
          st.image(c_img, width=200, caption="陣")
      with img_col2:
        w_img = load_image(chosen_weapon["weapon_img"], width=50)
        if w_img:
          st.image(w_img, width=200, caption="武器")

      st.markdown(
          f"<small><b>{chosen_weapon['name']}</b><br>🔮効果: {chosen_weapon['stat']} +{chosen_weapon['value']}</small>",
          unsafe_allow_html=True,
      )
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
        st.markdown(
            f"**{p['name']}**<br><small>{w['name']} ({w['stat']}+{w['value']})</small>",
            unsafe_allow_html=True,
        )
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
