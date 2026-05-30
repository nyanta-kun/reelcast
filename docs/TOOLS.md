# ツール選定（reelcast）

> ⚠️ 価格・規約は変動が激しい。**契約・実装の直前に各公式で必ず再確認**すること。本書は2026年5月時点の調査に基づく。

## 音楽生成 — 決定: **Suno Pro（$10/月）＋ 人間アシスト**

### 決定内容
- **Suno Pro（$10/月、年払い $8）** を採用。
- **music 工程は「人間アシスト生成 ＋ 自動取り込み」**：人間が Suno Web で週次バッチ生成し、ダウンロードして `data/assets/music/` に投入。パイプラインは取り込み・検証して合成へ回す。
- 完全自動化（公式 API）が必要になったら **Premier（~$24/月）** へ上げる。

### 根拠と重要事実（⚠️要再確認）
- Pro は商用ライセンスを付与。**解約後も生成済み曲の商用権は継続**。ストリーミング印税の Suno 徴収は **0%**。
- **公式 API は Pro に含まれない**（Premier 以上 / 一部はパートナー beta）。$10 のまま自動化はできない。
- **第三者 API ラッパー（sunoapi.org / apiframe 等, ~$19/月）は不採用**：アカウントプール運用・スクレイピング由来で、Suno 公式 ToS 違反・商用権の不確実性・突然の停止リスクがあり、「規約フル遵守」方針に反する。
- **YouTube は2026年もAI音楽の収益化を許容**。ただし「5ポリシー遵守＋意味のある人間のキュレーション」が条件。→ 人間アシスト＋承認ゲートがこの要件を満たす。
- **米国著作権局見解：純AI生成楽曲は著作権登録不可**。→ 自AI音楽を Content ID 登録して守るのは困難。収益化はプラットフォームの商用ライセンスで可能（登録可否とは別問題）。
- WMG×Suno は2025/11に訴訟和解。Content ID リスクは低減方向。

### 比較（参考）
| ツール | 月額 | API自動化 | 商用権 | DL | Content ID 安全性 | 判定 |
|---|---|---|---|---|---|---|
| **Suno Pro** | $10 | ✗ | ◎ 継続・印税0% | ✓ | △→改善(WMG和解) | **採用** |
| Suno Premier | ~$24 | ✓ 公式API | ◎ | ✓ | △→改善 | 将来の自動化用 |
| ElevenLabs Music | 要確認 | ✓ | ◎ | ✓ | ◎ 大手照合なし | 代替候補（Content ID重視時） |
| Udio | $10 / 商用は$30 | ✓ | ○($30〜) | ✗ DL停止中(2025/10〜) | △ | 除外（DL不可） |
| 第三者Suno API | ~$19 | ✓ | 主張のみ | ✓ | △ | 除外（非公式・規約リスク） |

## 画像生成 — 決定: **Gemini Nano Banana 2**（参照画像でキャラ固定）

### 決定内容
- **静止画＝Gemini Nano Banana 2**。猫の正典 `assets/brand/cat_ref_v1.png` を**参照画像**に与え、各世界を一貫生成。キャラ一貫性が最大の強み。
- **動き＝別工程・微細ループ**（ffmpeg の compose 工程）。フルアニメは不採用。
- 画風＝**日本アニメ調**で確定。

### 根拠と注意（⚠️要再確認）
- 商用利用OK・Google は出力の所有権を主張しない（コンテンツポリシー順守前提）。
- ⚠️ **無料 gemini.google.com 画像は可視透かし（Geminiロゴ）付き → 本番フレーム不可**。透かし無しは **Gemini API（従量・自動化可）** か Gemini Ultra。→ 設計探索は無料アプリ、本番は API。**「必要な一点だけ最小有料」の例外**（音楽と同様）。
- SynthID（不可視透かし）常時付与。商用に支障なく、**AI開示方針と整合**。
- Leonardo Character Reference は有料（$12〜 Apprentice）で機能は同等以上だが、Nano Banana が使えるため不採用。ローカルSD/Firefly も候補から外す。

### 比較（参考・不採用分）
| 候補 | コスト | キャラ固定 | 備考 |
|---|---|---|---|
| **Gemini Nano Banana 2** | 無料(透かし)/API従量 | ◎ 参照画像 | **採用** |
| Leonardo（Apprentice） | $12〜 | ◎ Character Reference | 不採用（Nano Bananaで足りる） |
| ローカル Stable Diffusion | 無料 | △ 要LoRA等 | 不採用（セットアップ重い） |
| Adobe Firefly | 無料枠 | △ | 不採用 |

## Sources（2026-05 調査）
- [Suno Pricing（公式）](https://suno.com/pricing)
- [Suno Commercial Use: Free vs Pro Rights 2026 — Dynamoi](https://dynamoi.com/learn/ai-music-distribution/suno-commercial-rights-explained)
- [The 2026 Suno AI Legal Guide — mystats.music](https://mystats.music/blog/suno-ai-legal-guide-2026)
- [Suno adjusts AI music ownership terms after Warner partnership — Music In Africa](https://www.musicinafrica.net/magazine/suno-adjusts-ai-music-ownership-terms-after-warner-music-partnership)
- [YouTube AI Generated Music Policy 2026 — Music Make AI](https://musicmake.ai/blog/youtube-ai-generated-music-policy-2026)
- [AI-Generated Music on YouTube: Monetization 2026 — OutlierKit](https://outlierkit.com/resources/ai-generated-music-youtube-monetization-2026/)
- [Udio Terms of Service 2026 — Music Make AI](https://musicmake.ai/blog/udio-terms-of-service-commercial-use-2026)
- [AI Music Generators with Commercial Rights 2026 — Dynamoi](https://dynamoi.com/learn/ai-music-distribution/which-ai-music-generators-allow-commercial-distribution)
- [Suno API Review and Integration Guide — Evolink](https://evolink.ai/blog/suno-api-review-complete-guide-ai-music-generation-integration)
- [Best Free AI Image Generators 2026 — BasedLabs](https://www.basedlabs.ai/articles/best-ai-image-generator-free)
- [Leonardo.Ai Pricing（公式）](https://leonardo.ai/pricing)
