# Studio Data Tools クイックスタートガイド

このクイックスタートガイドでは、Studio Data Toolsの基本的な使い方を簡潔に説明します。

## インストール

```bash
# リポジトリをクローン
git clone <repo-url>
cd studio_data_tools

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してGemini APIキーを設定

# uvを使用したインストール
./setup_uv.sh
```

## 基本的な使い方

### 1. サンプル画像の生成（少数の高品質画像）

```bash
uv run python -m studio_data_tools samples --object "empty can" --count 5
```

### 2. 大量の画像生成

```bash
uv run python -m studio_data_tools generate --object "plastic bottle" --count 20 --advanced-prompts
```

### 3. データセットの準備

```bash
uv run python -m studio_data_tools prepare generated_images/plastic_bottle --output-file Cam0.zip
```

### 4. データ拡張の適用

```bash
uv run python -m studio_data_tools prepare generated_images/plastic_bottle --output-file Cam0_augmented.zip --augment --num-images 200
```

## 主なオプション

### 画像生成オプション

- `--object`: 生成する対象物（例：「empty can」「plastic bottle」）
- `--count`: 生成する画像の数
- `--min-objects`: 画像内の最小オブジェクト数（デフォルト：1）
- `--max-objects`: 画像内の最大オブジェクト数（デフォルト：3）
- `--num-objects`: 画像内の正確なオブジェクト数（min/maxより優先）
- `--output-dir`: 画像の保存先ディレクトリ
- `--advanced-prompts`: より高品質な画像生成のための高度なプロンプト生成を使用
- `--no-llm`: LLMによるシーン生成を無効化（より高速だが品質は低下）

### データセット準備オプション

- `--output-file`, `-o`: 出力ZIPファイル名（デフォルト：「Cam0.zip」）
- `--width`: 出力画像の幅（デフォルト：640）
- `--height`: 出力画像の高さ（デフォルト：480）
- `--augment`: データ拡張を適用
- `--num-images`, `-n`: 生成する拡張画像の数（デフォルト：100、`--augment`と共に使用）

## トラブルシューティング

### APIキーエラー

```
ValueError: API key is required. Please provide it or set GEMINI_API_KEY in .env file.
```

解決策：`.env`ファイルに有効なGemini APIキーを設定してください。

### 画像生成エラー

```
Error generating image with imagen-3.0-generate-002: ...
```

解決策：
- インターネット接続を確認
- APIキーの有効性を確認
- APIの使用量制限に達していないか確認

### データ拡張エラー

```
RuntimeError: imgaug is required for image augmentation.
```

解決策：`imgaug`パッケージをインストール：
```bash
uv pip install imgaug
```

## 次のステップ

詳細なドキュメントは[aitrios_studio_guide.md](./aitrios_studio_guide.md)を参照してください。

AITRIOSのStudioサービスについては、[AITRIOSの公式ウェブサイト](https://www.aitrios.sony-semicon.com/)をご確認ください。