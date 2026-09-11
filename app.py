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
  all_pairs = [
      ("炎", "風"),
      ("水", "光"),
      ("土", "闇"),
      ("炎", "水"),
      ("風", "土"),
      ("光", "闇"),
  ]
  selected_pairs = random.sample(all_pairs, 3)
  selected_types = random.sample(WEAPON_TYPES, 3)

  st.session_state.available_parts = {
      "attr_pairs": selected_pairs,
      "type": selected_types,
      "level": ["初級", "初級", "初級"],
  }


def generate_enemies():
  stage = st.session_state.stage
  enemies = []
  
  # ステージごとに異なるボス名・雑魚敵名を決定
  boss_titles = ["魔王", "邪竜", "覇王", "魔神", "深淵の獣", "混沌の主", "絶望の使者", "虚無の王", "破壊神", "神話の終焉"]
  minion_titles = ["ゴブリン", "スライム", "オーク", "スケルトン", "インプ", "ハーピー", "ゴーレム", "ファントム", "リザードマン", "キメラ"]
  
  b_name = f"{boss_titles[(stage - 1) % len(boss_titles)]} Lv.{stage}"
  e_hp_boss = 120 + stage * 40
  
  # 3x3 (計9体) の配置生成：インデックス 4 が中央（ボス）、他は雑魚敵
  for i in range(9):
    if i == 4:
      enemies.append({
          "name": b_name,
          "hp": e_hp_boss,
          "max_hp": e_hp_boss,
          "atk": 22 + stage * 6,
          "def": 10 + stage * 3,
          "img": "images/enemy_boss.jpg",
          "is_boss": True,
      })
    else:
      m_name = f"{minion_titles[(stage + i) % len(minion_titles)]} Lv.{stage}-{i+1}"
      e_hp_minion = 50 + stage * 20
      enemies.append({
          "name": m_name,
          "hp": e_hp_minion,
          "max_hp": e_hp_minion,
          "atk": 14 + stage * 4,
          "def": 5 + stage * 2,
          "img": "images/enemy_boss.jpg",
          "is_boss": False,
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
    .enemy-card { background-color: #fff0f0; padding: 10px; border-radius: 8px; border: 1px solid #ffcccc; margin-bottom: 8px; text-align: center; }
    .boss-card { background-color: #ffe6e6; padding: 12px; border-radius: 8px; border: 2px solid #ff4d4d; margin-bottom: 8px; text-align: center; }
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
        "ドロップした3つの属性ペア、異なる3種類の武器種、初級レベルを組み合わせて、3つの円形魔法陣と初期武器を構築してください。"
    )

    parts = st.session_state.available_parts

    st.markdown("#### 🎁 ステージ1 ドロップ部品")
    c1, c2, c3 = st.columns(3)

    with c1:
      st.markdown("**属性ペア部品 (3種類)**")
      for pair in parts["attr_pairs"]:
        st.info(f"✨ 属性ペア: {pair[0]} と {pair[1]}")

    with c2:
      st.markdown("**武器種部品 (異なる3種)**")
      for t in parts["type"]:
        st.info(f"⚔️ {t}")

    with c3:
      st.markdown("**レベル部品**")
      st.info("🌟 初級 (固定)")

    st.markdown("---")
    st.subheader("🌀 円形魔法陣の構築と武器プレビュー")

    col_w1, col_w2, col_w3 = st.columns(3)

    def render_magic_slot(slot_num, assigned_pair):
      st.markdown(
          f"<div class='magic-slot'><h5>🔮 魔法陣スロット #{slot_num}</h5>",
          unsafe_allow_html=True,
      )
      st.markdown(
          f"<b>【中央コア】指定属性ペア: {assigned_pair[0]} &"
          f" {assigned_pair[1]}</b>",
          unsafe_allow_html=True,
      )
      a1 = assigned_pair[0]
      a2 = assigned_pair[1]
      st.write(f"コア属性: **{a1}** / **{a2}**")

      st.markdown("<b>【外周リング】武器・レベル</b>", unsafe_allow_html=True)
      w_type = parts["type"][slot_num - 1]
      st.write(f"武器種: **{w_type}**")

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
      raw_w1 = render_magic_slot(1, parts["attr_pairs"][0])
    with col_w2:
      raw_w2 = render_magic_slot(2, parts["attr_pairs"][1])
    with col_w3:
      raw_w3 = render_magic_slot(3, parts["attr_pairs"][2])

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
      next_lvl = current_lvl

    st.markdown(f"**選択中の武器:** {target_weapon['name']}")
    st.write(
        f"現在のレベル: **{current_lvl}** ➔ アップグレード後のレベル: **{next_lvl}**"
    )

    if st.button("⬆️ 武器のレベルを1段階上げる", type="primary"):
      if next_lvl != current_lvl:
        target_weapon["level"] = next_lvl
        base_val = target_weapon["value"] / LEVEL_MULTIPLIERS[current_lvl]
        target_weapon["value"] = int(base_val * LEVEL_MULTIPLIERS[next_lvl])

        parts_name = target_weapon["name"].split("の")
        attrs = parts_name[0]
        w_type = target_weapon["type"]
        target_weapon["name"] = f"{attrs}の{next_lvl}{w_type}"

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
      p_img = load_image(p["img"], width=200)
      if p_img:
        st.image(p_img, width=200)
      else:
        st.markdown(f"### 🛡️ {p['name']}")

      st.write(
          f"基礎 ATK: {p['atk']} / DEF: {p['def']} / REC: {p['rec']}"
      )

      default_idx = 0
      if p["weapon"] and p["weapon"]["name"] in w_names:
        default_idx = w_names.index(p["weapon"]["name"])

      selected_w_name = st.selectbox(
          f"装備選択", w_names, index=default_idx, key=f"equip_{idx}"
      )
      chosen_weapon = weapon_options[selected_w_name]
      assigned_weapons.append(chosen_weapon)

      # 武器タイプに応じた射程範囲の説明を表示
      w_type = chosen_weapon["type"]
      range_desc = {
          "剣": "前衛単体（指定した1体）",
          "槍": "縦一列（3体）",
          "弓": "ランダム3体",
          "杖": "全体（9体すべて）"
      }.get(w_type, "単体")
      st.info(f"🎯 射程範囲: **{range_desc}**")

      img_col1, img_col2 = st.columns(2)
      with img_col1:
        c_img = load_image(chosen_weapon["circle_img"], width=200)
        if c_img:
          st.image(c_img, width=200, caption="陣")
      with img_col2:
        w_img = load_image(chosen_weapon["weapon_img"], width=200)
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
    st.session_state.battle_log = ["⚔️ バトルが開始されました！ 敵が3×3グリッドで立ちはだかる！"]
    st.rerun()

# ==========================================
# フェーズ 3: バトルフェーズ (プレイヤー vs 3x3グリッドエネミー)
# ==========================================
elif st.session_state.phase == "battle":
  st.subheader("⚔️ バトルフェーズ (3×3グリッド戦)")

  col_p, col_e = st.columns([1, 1])

  with col_p:
    st.markdown("### 🔵 プレイヤーチーム")
    for p in st.session_state.players:
      p_img = load_image(p["img"], width=200)
      hp_ratio = max(0, min(1, p["hp"] / p["max_hp"]))
      w = p["weapon"]
      w_img = load_image(w["weapon_img"], width=200) if w else None
      c_img = load_image(w["circle_img"], width=200) if w else None

      st.markdown(f"<div class='card'>", unsafe_allow_html=True)
      pc1, pc2, pc3, pc4 = st.columns([1, 1, 1, 2])
      with pc1:
        if p_img:
          st.image(p_img, width=200)
        else:
          st.write("👤")
      with pc2:
        if c_img:
          st.image(c_img, width=120, caption="陣")
      with pc3:
        if w_img:
          st.image(w_img, width=120, caption="武")
      with pc4:
        w_type = w["type"] if w else ""
        st.markdown(
            f"**{p['name']}** <small>({w_type})</small><br><small>{w['name'] if w else ''}</small>",
            unsafe_allow_html=True,
        )
        st.progress(
            hp_ratio, text=f"HP: {max(0, p['hp'])} / {p['max_hp']}"
        )
      st.markdown("</div>", unsafe_allow_html=True)

  with col_e:
    st.markdown("### 🔴 エネミーチーム (3×3グリッド)")
    
    # 3x3 グリッドを描画
    enemies = st.session_state.enemies
    for r in range(3):
      grid_cols = st.columns(3)
      for c in range(3):
        idx = r * 3 + c
        if idx < len(enemies):
          e = enemies[idx]
          with grid_cols[c]:
            hp_ratio = max(0, min(1, e["hp"] / e["max_hp"]))
            card_class = "boss-card" if e.get("is_boss") else "enemy-card"
            st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
            if e["hp"] > 0:
              boss_tag = "👑 **[BOSS]**<br>" if e.get("is_boss") else ""
              st.markdown(f"{boss_tag}<b>{e['name']}</b>", unsafe_allow_html=True)
              st.progress(hp_ratio, text=f"{max(0, e['hp'])}/{e['max_hp']}")
            else:
              st.markdown(f"~~{e['name']}~~<br><b>【撃破】</b>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

  st.markdown("---")

  if st.button("⚔️ ターン進行 (攻撃＆回復)", type="primary"):
    logs = []
    enemies = st.session_state.enemies

    # プレイヤーの攻撃処理（武器の射程範囲に基づく）
    for p in st.session_state.players:
      if p["hp"] > 0:
        w = p["weapon"]
        w_type = w["type"] if w else "剣"
        
        # 射程範囲による対象の選定
        target_indices = []
        living_indices = [i for i, e in enumerate(enemies) if e["hp"] > 0]
        
        if not living_indices:
          continue

        if w_type == "剣":
          # 剣: 前衛単体（生き残っている敵の中からランダムで1体、または前方優先）
          target_indices = [random.choice(living_indices)]
        elif w_type == "槍":
          # 槍: 縦一列（0,3,6 / 1,4,7 / 2,5,8 のいずれか列を選択してその列の生存者全員）
          cols_available = []
          for col_idx in range(3):
            col_members = [col_idx, col_idx + 3, col_idx + 6]
            if any(enemies[m]["hp"] > 0 for m in col_members):
              cols_available.append(col_members)
          if cols_available:
            chosen_col = random.choice(cols_available)
            target_indices = [m for m in chosen_col if enemies[m]["hp"] > 0]
          else:
            target_indices = [random.choice(living_indices)]
        elif w_type == "弓":
          # 弓: ランダムに最大3体
          count = min(3, len(living_indices))
          target_indices = random.sample(living_indices, count)
        elif w_type == "杖":
          # 杖: 全体（生存しているすべての敵）
          target_indices = living_indices

        # ダメージ計算と適用
        for t_idx in target_indices:
          target = enemies[t_idx]
          dmg = max(5, p["atk"] - target["def"] // 3)
          target["hp"] = max(0, target["hp"] - dmg)
          logs.append(f"🟢 {p['name']} ({w_type}) の攻撃！ {target['name']} に {dmg} のダメージ！")

    # エネミーの反撃処理
    living_enemies = [e for e in enemies if e["hp"] > 0]
    for e in living_enemies:
      living_players = [pl for pl in st.session_state.players if pl["hp"] > 0]
      if living_players:
        target = random.choice(living_players)
        dmg = max(4, e["atk"] - target["def"] // 3)
        target["hp"] = max(0, target["hp"] - dmg)
        logs.append(f"🔴 {e['name']} の反撃！ {target['name']} に {dmg} のダメージ！")

    # プレイヤーの回復スキル処理
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

    all_enemies_dead = all(e["hp"] <= 0 for e in enemies)
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
