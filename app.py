import random
import streamlit as st

st.set_page_config(page_title="魔法陣武器生成 RPG", layout="centered")

# 定数定義
ATTRIBUTES = ["炎", "水", "風", "地", "光", "闇"]
WEAPON_TYPES = ["剣", "杖", "弓", "盾", "槍"]
LEVELS = ["初級", "中級", "上級", "王級", "神級"]
LEVEL_MULTIPLIERS = {"初級": 1, "中級": 1.5, "上級": 2.2, "王級": 3.0, "神級": 4.5}
STATS = ["HP", "攻撃力", "防御力", "回復力"]

# セッション状態の初期化
if "stage" not in st.session_state:
  st.session_state.stage = 1
  st.session_state.phase = "generate"  # generate, equip, battle, gameover, clear
  st.session_state.players = [
      {"name": "戦士アレン", "hp": 120, "max_hp": 120, "atk": 25, "def": 15, "rec": 5, "weapon": None},
      {"name": "魔導士リリア", "hp": 90, "max_hp": 90, "atk": 30, "def": 8, "rec": 20, "weapon": None},
      {"name": "騎士レオン", "hp": 150, "max_hp": 150, "atk": 18, "def": 25, "rec": 10, "weapon": None},
  ]
  st.session_state.enemies = []
  st.session_state.available_parts = {}
  st.session_state.crafted_weapons = []
  st.session_state.battle_log = []


def generate_stage_parts():
  # ステージに応じた部品のドロップ生成
  st.session_state.available_parts = {
      "attr": random.choices(ATTRIBUTES, k=6),
      "type": random.choices(WEAPON_TYPES, k=4),
      "level": random.choices(LEVELS, k=4),
      "stat": random.choices(STATS, k=4),
  }


def generate_enemies():
  stage = st.session_state.stage
  enemies = []
  for i in range(3):
    e_hp = 60 + stage * 25
    enemies.append({
        "name": f"魔物 Lv.{stage}-{i+1}",
        "hp": e_hp,
        "max_hp": e_hp,
        "atk": 15 + stage * 5,
        "def": 5 + stage * 2,
    })
  st.session_state.enemies = enemies


if not st.session_state.available_parts and st.session_state.phase == "generate":
  generate_stage_parts()

st.title(f"魔法陣構築 RPG (ステージ {st.session_state.stage} / 10)")

# フェーズ1: 武器生成フェーズ
if st.session_state.phase == "generate":
  st.subheader("⚙️ 魔法陣構築・武器生成フェーズ")
  st.write("ドロップした部品を組み合わせて、3つの武器を作成してください。")

  parts = st.session_state.available_parts
  st.write(f"利用可能な属性: {', '.join(parts['attr'])}")
  st.write(f"利用可能な武器種: {', '.join(parts['type'])}")
  st.write(f"利用可能なレベル: {', '.join(parts['level'])}")
  st.write(f"利用可能な強化ステータス: {', '.join(parts['stat'])}")

  st.markdown("---")
  st.write("### 武器 1 の構築")
  w1_attr1 = st.selectbox("属性1 (コア)", ATTRIBUTES, key="w1_a1")
  w1_attr2 = st.selectbox("属性2 (コア)", ATTRIBUTES, key="w1_a2")
  w1_type = st.selectbox("武器種", WEAPON_TYPES, key="w1_t")
  w1_lvl = st.selectbox("レベル", LEVELS, key="w1_l")
  w1_stat = st.selectbox("強化ステータス", STATS, key="w1_s")

  st.write("### 武器 2 の構築")
  w2_attr1 = st.selectbox("属性1 (コア)", ATTRIBUTES, key="w2_a1")
  w2_attr2 = st.selectbox("属性2 (コア)", ATTRIBUTES, key="w2_a2")
  w2_type = st.selectbox("武器種", WEAPON_TYPES, key="w2_t")
  w2_lvl = st.selectbox("レベル", LEVELS, key="w2_l")
  w2_stat = st.selectbox("強化ステータス", STATS, key="w2_s")

  st.write("### 武器 3 の構築")
  w3_attr1 = st.selectbox("属性1 (コア)", ATTRIBUTES, key="w3_a1")
  w3_attr2 = st.selectbox("属性2 (コア)", ATTRIBUTES, key="w3_a2")
  w3_type = st.selectbox("武器種", WEAPON_TYPES, key="w3_t")
  w3_lvl = st.selectbox("レベル", LEVELS, key="w3_l")
  w3_stat = st.selectbox("強化ステータス", STATS, key="w3_s")

  if st.button("武器を生成して装備フェーズへ進む"):
    st.session_state.crafted_weapons = [
        {
            "name": f"{w1_attr1}・{w1_attr2}の{w1_lvl}{w1_type}",
            "attr": [w1_attr1, w1_attr2],
            "type": w1_type,
            "level": w1_lvl,
            "stat": w1_stat,
            "value": int(10 * LEVEL_MULTIPLIERS[w1_lvl]),
        },
        {
            "name": f"{w2_attr1}・{w2_attr2}の{w2_lvl}{w2_type}",
            "attr": [w2_attr1, w2_attr2],
            "type": w2_type,
            "level": w2_lvl,
            "stat": w2_stat,
            "value": int(10 * LEVEL_MULTIPLIERS[w2_lvl]),
        },
        {
            "name": f"{w3_attr1}・{w3_attr2}の{w3_lvl}{w3_type}",
            "attr": [w3_attr1, w3_attr2],
            "type": w3_type,
            "level": w3_lvl,
            "stat": w3_stat,
            "value": int(10 * LEVEL_MULTIPLIERS[w3_lvl]),
        },
    ]
    st.session_state.phase = "equip"
    st.rerun()

# フェーズ2: 装備フェーズ
elif st.session_state.phase == "equip":
  st.subheader("🛡️ 装備フェーズ")
  st.write("作成した3つの武器を3人のキャラクターに割り当ててください。")

  weapons = st.session_state.crafted_weapons
  weapon_options = {w["name"]: w for w in weapons}
  w_names = list(weapon_options.keys())

  assigned_weapons = []
  for idx, p in enumerate(st.session_state.players):
    selected_w_name = st.selectbox(
        f"{p['name']} の装備武器", w_names, key=f"equip_{idx}"
    )
    assigned_weapons.append(weapon_options[selected_w_name])

  if st.button("バトルフェーズへ進む"):
    # 武器を装備し、ステータスに反映
    for i, p in enumerate(st.session_state.players):
      w = assigned_weapons[i]
      p["weapon"] = w
      # ステータス一時強化の適用 (HPは上限も上げる)
      if w["stat"] == "HP":
        p["max_hp"] += w["value"] * 3
        p["hp"] = p["max_hp"]
      elif w["stat"] == "攻撃力":
        p["atk"] += w["value"]
      elif w["stat"] == "防御力":
        p["def"] += w["value"]
      elif w["stat"] == "回復力":
        p["rec"] += w["value"]

    generate_enemies()
    st.session_state.phase = "battle"
    st.session_state.battle_log = ["バトル開始！"]
    st.rerun()

# フェーズ3: バトルフェーズ
elif st.session_state.phase == "battle":
  st.subheader("⚔️ バトルフェーズ (3 vs 3)")

  col1, col2 = st.columns(2)
  with col1:
    st.write("### プレイヤーチーム")
    for p in st.session_state.players:
      w_name = p["weapon"]["name"] if p["weapon"] else "なし"
      st.markdown(
          f"- **{p['name']}** (HP: {p['hp']}/{p['max_hp']})<br><small>武器: {w_name}</small>",
          unsafe_allow_html=True,
      )

  with col2:
    st.write("### 敵チーム")
    for e in st.session_state.enemies:
      if e["hp"] > 0:
        st.write(f"- {e['name']} (HP: {e['hp']}/{e['max_hp']})")
      else:
        st.write(f"- ~~{e['name']}~~ (戦闘不能)")

  st.markdown("---")

  if st.button("ターンを進める (攻撃実行)"):
    logs = []
    # プレイヤーの攻撃
    for p in st.session_state.players:
      if p["hp"] > 0:
        living_enemies = [e for e in st.session_state.enemies if e["hp"] > 0]
        if living_enemies:
          target = random.choice(living_enemies)
          dmg = max(5, p["atk"] - target["def"] // 2)
          target["hp"] = max(0, target["hp"] - dmg)
          logs.append(f"{p['name']} の攻撃！ {target['name']} に {dmg} のダメージ！")

    # 敵の攻撃
    for e in st.session_state.enemies:
      if e["hp"] > 0:
        living_players = [pl for pl in st.session_state.players if pl["hp"] > 0]
        if living_players:
          target = random.choice(living_players)
          dmg = max(3, e["atk"] - target["def"] // 2)
          target["hp"] = max(0, target["hp"] - dmg)
          logs.append(f"{e['name']} の攻撃！ {target['name']} に {dmg} のダメージ！")

    # 回復行動
    for p in st.session_state.players:
      if p["hp"] > 0 and p["rec"] > 0:
        living_players = [pl for pl in st.session_state.players if pl["hp"] > 0]
        if living_players:
          target = min(living_players, key=lambda x: x["hp"] / x["max_hp"])
          heal = p["rec"]
          target["hp"] = min(target["max_hp"], target["hp"] + heal)
          logs.append(
              f"{p['name']} のスキル発動！ {target['name']} のHPが {heal}"
              " 回復した！"
          )

    st.session_state.battle_log.extend(logs)

    # 勝敗判定
    all_enemies_dead = all(e["hp"] <= 0 for e in st.session_state.enemies)
    all_players_dead = all(p["hp"] <= 0 for p in st.session_state.players)

    if all_enemies_dead:
      if st.session_state.stage >= 10:
        st.session_state.phase = "clear"
      else:
        st.session_state.stage += 1
        st.session_state.phase = "generate"
        st.session_state.available_parts = {}
        # 次のステージに向けてHP回復
        for p in st.session_state.players:
          p["hp"] = p["max_hp"]
      st.rerun()
    elif all_players_dead:
      st.session_state.phase = "gameover"
      st.rerun()

  st.write("### 戦闘ログ")
  for log in reversed(st.session_state.battle_log[-6:]):
    st.text(log)

elif st.session_state.phase == "gameover":
  st.error("💀 ゲームオーバー... 全滅してしまいました。")
  if st.button("最初からやり直す"):
    st.session_state.clear()
    st.rerun()

elif st.session_state.phase == "clear":
  st.success(
      "🎉 祝・全10ステージクリア！ 魔法陣のマスターとして世界を救いました！"
  )
  if st.button("もう一度プレイする"):
    st.session_state.clear()
    st.rerun()
