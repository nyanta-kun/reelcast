# クリエイティブ・コンセプト（reelcast）

> 決定: 2026-05-30。需要は既存チャンネル群で実証済み（Sources 参照）。

## ブランドの核：1匹の「まったり猫マスコット」

- **不変の軸＝猫**。チャンネルの主役は世界ではなく**猫**。毎回**厳密に同一デザイン**で登場（固定キャラ資産方式）。
- 役割：**インスト機能性音楽の看板マスコット**。歌わない。佇む／ゆっくり揺れる程度の低コストループ。
- 完全フェイスレス・テキスト人格のみ（バーチャルレーベル名義）と整合。

## シリーズ＝猫が旅する「世界」

ブランド軸（猫）は固定し、**シリーズごとに世界（舞台）を変える**。登録フック＝「今回はどこに猫がいる？」。
初期は3世界に絞って立ち上げ（散漫を避ける）。各世界は**明確な用途（活動）＝SEOフック**に対応させる。

| シリーズ | 世界 | 主な用途（SEOフック） | 音楽の方向 |
|---|---|---|---|
| **Neon Night Cat** | 雨のネオン都市の部屋 | 夜のチル / 睡眠 / 深夜の集中 | rainy synthwave-lofi |
| **Cozy Cabin Cat** | 暖炉の山小屋 | 読書 / 就寝 / リラックス（季節フック強） | warm cozy lofi＋暖炉/雨アンビエンス |
| **Starship Cat** | 宇宙船の窓辺 | 集中 / 作業・コーディング / アンビエント | space lofi / ambient / epic focus |

> 用途の網羅：**睡眠・読書/リラックス・集中/作業** をカバー。将来 4〜5本目（瞑想、ドライブ synthwave 等）を追加可能。

## 差別化（競合は多い＝需要実証済み）

- 既存の猫lo-fiの多くは**1部屋に固定**。本企画は**「猫が複数世界を旅する」**で差別化。
- レバー：①記憶に残るオリジナル猫デザイン＋名前 ②世界の作り込み（固定キャラ＋背景差し替え）③一貫性の徹底。
- ⚠️ 既存名（Lofi Cat / Lofi Kitty / Simon's Cat Lofi 等）は回避。**完全オリジナルの猫・名前**を作る（#7）。

## 検討中の「爽快感のある宇宙×メカ」要素

- Starship Cat 世界で **epic / synthwave 寄り**にすれば、爽快感の志向を「集中・作業・ゲーム用」サブニッチとして回収できる。
- ただし**動的なロボット大戦アニメは不採用**（高コスト・週5h と矛盾・睡眠/背景音楽とトーン衝突）。メカは**雄大・静的な背景要素**に留める。⚠️ ガンダム等の既存IP風は権利侵害リスクのため**完全オリジナル**で。

## 猫のモデルシート（確定・ブランドの基準）

> 正典参照画像：[`assets/brand/cat_ref_v1.png`](../assets/brand/cat_ref_v1.png)（Gemini Nano Banana 2 で生成）。毎回これを基準に一貫性をチェックする。

- **柄**：グレー＆ホワイトのタビー（アメショ風マッカレル縞、額にうっすらM字）、白い胸・口元・足先
- **体型**：丸くぽっちゃり、香箱/伏せ（loaf）型
- **目**：半目、おだやかな琥珀色
- **目印（固定ブランド要素）**：**水色×白のオーバーイヤーヘッドホン**
- **表情/性格**：眠そう・脱力・マイペース（寡黙でどんな世界でもくつろぐ）
- **画風**：**日本アニメ調**（detailed anime background / soft cinematic lighting）、暖色シネマティック

### 一貫性の担保（確定）
- **Gemini Nano Banana 2** に `cat_ref_v1.png` を**参照画像**として与え、各世界を生成（キャラ固定）。
- ⚠️ 無料 gemini.google.com 画像は**可視透かし**付き → 本番フレームは **Gemini API（従量・自動化可）** を使う。設計探索は無料アプリで可。SynthID（不可視）は常時付与で、AI開示方針と整合。

### 動き（モーション）
- **フルアニメは作らない**（過剰投資・週5hと矛盾）。雨・湯気・ゆっくりズーム/パララックス等の**微細ループを compose 工程（ffmpeg）で安価に**付与。

## 未確定（→ 次工程で決定）
- **猫の名前・チャンネル名**（候補：Sora / Nimbus / Momo など。⚠️ 名称・ハンドル・商標の空き確認）
- Gemini 本番アクセス方式（API 従量 か Ultra）の最終確定（Phase 1 の visuals 実装時）

## Sources（2026-05 調査）
- [The 34 Best Lofi YouTube Channels 2026 — Gridfiti](https://gridfiti.com/best-lofi-youtube-channels/)
- [Lofi Cat（チャンネル）](https://www.youtube.com/@lofi_record_cat) / [Lofi Kitty](https://www.youtube.com/@LofiKittychannel) / [CatAndCode Lofi](https://www.youtube.com/channel/UCsDh-yhHA1u4by07LAXshlQ)
- [Lofi Girl — Wikipedia（猫を含む世界観の参考）](https://en.wikipedia.org/wiki/Lofi_Girl)
- Neon: [Night City Walk Cyberpunk Neon Rain](https://www.youtube.com/watch?v=KlcsGjI6Jms) / [NightCity Lofi](https://www.youtube.com/channel/UCVsJlAFHG7mb3idtMhBQSZw)
- Cozy: [Rainy Night Fireplace Cozy Cabin Lofi](https://www.youtube.com/watch?v=50i1x0HNMRg) / [Lofi Fireplace](https://www.youtube.com/@lofiwithfireplace/videos)
- Space: [ASTROHALL Ancient Space Ambient](https://www.youtube.com/watch?v=-a4vsVHNCus) / [SpaceAmbient](https://www.youtube.com/channel/UCZ8YN9u9H_tRTi2LTODoXLg)
