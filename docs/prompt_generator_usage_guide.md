# Prompt Generator Usage Guide

このガイドでは、`PromptGenerator`クラスの使用方法と実際のユースケースについて説明します。

## 目次

1. [概要](#概要)
2. [セットアップ](#セットアップ)
3. [基本的な使い方](#基本的な使い方)
4. [応用例](#応用例)
5. [ユースケース](#ユースケース)
6. [トラブルシューティング](#トラブルシューティング)

## 概要

`PromptGenerator`は、画像生成用のプロンプトを動的に作成するためのツールです。特に、ゴミ検出用のデータセット生成や環境内の特定オブジェクトのシーン変化などに役立ちます。このモジュールは以下の機能を提供します：

- 静的なシーン記述を使用したプロンプト生成
- Google Gemini APIを活用した動的で多様なシーン生成
- コントロール可能なパラメータによる柔軟なプロンプト作成
- APIエラー時のフォールバック機構

## セットアップ

### 環境変数の設定

1. `.env`ファイルを作成するか、既存のファイルを編集して、Gemini APIキーを追加します：

```
GEMINI_API_KEY=your_api_key_here
```

`.env.example`ファイルをコピーして始めることもできます：

```bash
cp .env.example .env
# .envファイルを編集してGEMINI_API_KEYを追加
```

### インストールと初期化

```python
from studio_data_tools.core.prompt_generator import PromptGenerator

# 環境変数からAPIキーを取得（.envファイルから）
generator = PromptGenerator()

# または明示的にAPIキーを指定
generator = PromptGenerator(api_key="your_api_key_here")

# モデルを指定することも可能
generator = PromptGenerator(model="gemini-1.5-pro")
```

## 基本的な使い方

### 1. シンプルなプロンプト生成

最も基本的な使い方として、オブジェクト名からシンプルなプロンプトを生成できます：

```python
# 空き缶のシンプルなプロンプトを生成
prompt, scene, count = generator.generate_simple_prompt("empty can")
print(f"シーン: {scene}")
print(f"オブジェクト数: {count}")
print(f"プロンプト: {prompt}")
```

### 2. プリセットシーンの取得

特定のオブジェクトに適したシーン一覧を取得：

```python
# 空き缶に適したシーンのリストを取得
scenes = generator.get_appropriate_scenes("empty can")
for scene in scenes:
    print(scene)
```

### 3. LLMを使用した多様なシーン生成

```python
# LLMを使って空き缶のための多様なシーン10個を生成
diverse_scenes = generator.generate_diverse_scenes("empty can", num_scenes=10)
for i, scene in enumerate(diverse_scenes, 1):
    print(f"{i}. {scene}")
```

### 4. リアリスティックなプロンプト生成

詳細な写真特性を含むリアリスティックなプロンプトを生成：

```python
# 特定のシーンと条件でリアリスティックなプロンプトを生成
result = generator.generate_realistic_prompt(
    object_name="plastic bottle",
    scene_type="urban sidewalk with discarded trash",
    num_objects=3
)

print(f"シーン: {result['scene']}")
print(f"オブジェクト: {result['object']} (数量: {result['object_count']})")
print(f"プロンプト: {result['prompt']}")
```

### 5. 複数のプロンプトを一度に生成

```python
# 空き缶のシンプルなプロンプトを5つ生成
simple_prompts = generator.generate_simple_prompts("empty can", count=5)
for i, p in enumerate(simple_prompts, 1):
    print(f"プロンプト {i}: {p['scene']}")
```

## 応用例

### 様々なオブジェクトタイプの組み合わせ

```python
# 様々なゴミタイプのプロンプトを生成
garbage_types = ["empty can", "plastic bottle", "paper cup", "glass bottle"]
all_prompts = []

for garbage_type in garbage_types:
    # 各タイプで3つのプロンプトを生成
    prompts = generator.generate_llm_prompts(
        object_type=garbage_type,
        count=3,
        min_objects=1,
        max_objects=5,
        advanced=True
    )
    all_prompts.extend(prompts)

print(f"合計 {len(all_prompts)} プロンプトが生成されました")
```

### 高度なカスタマイズ

```python
# 特定の数のオブジェクトを持つ高度なプロンプトを生成
advanced_prompts = generator.generate_llm_prompts(
    object_type="plastic bottle",
    count=5,
    exact_objects=3,  # 常に3つのオブジェクト
    advanced=True     # 詳細な写真家スタイルの説明
)

for p in advanced_prompts:
    print(f"シーン: {p['scene']}")
    print(f"プロンプト: {p['prompt'][:150]}...\n")
```

### APIを使わないフォールバックモード

```python
# APIなしでシンプルなプロンプトを生成（スタティックデータを使用）
offline_prompt, scene, count = generator.generate_simple_prompt(
    "empty can", 
    use_llm=False  # LLMを使用せず、静的データに頼る
)
print(f"オフラインプロンプト: {offline_prompt[:100]}...")
```

## ユースケース

### ユースケース1: ゴミ検出・分類のためのトレーニングデータ生成

```python
import os
from pathlib import Path

# 生成したいプロンプトの種類と数を定義
generation_specs = [
    {"object": "empty can", "count": 20},
    {"object": "plastic bottle", "count": 20},
    {"object": "paper cup", "count": 15},
    {"object": "glass bottle", "count": 15}
]

# プロンプトをファイルに保存するディレクトリ
output_dir = Path("generated_prompts")
os.makedirs(output_dir, exist_ok=True)

# 各オブジェクトタイプに対してプロンプトを生成
for spec in generation_specs:
    obj_type = spec["object"]
    count = spec["count"]
    
    # ファイル名を準備
    filename = f"{obj_type.replace(' ', '_')}_prompts.txt"
    filepath = output_dir / filename
    
    # 高度なプロンプトを生成
    prompts = generator.generate_llm_prompts(
        object_type=obj_type,
        count=count,
        min_objects=1,
        max_objects=4,
        advanced=True
    )
    
    # プロンプトをファイルに保存
    with open(filepath, "w") as f:
        for i, p in enumerate(prompts, 1):
            f.write(f"Prompt {i}:\n")
            f.write(f"Scene: {p['scene']}\n")
            f.write(f"Object: {p['object']} (Count: {p['object_count']})\n")
            f.write(f"Text: {p['prompt']}\n\n")
    
    print(f"{count} プロンプトが {filepath} に保存されました")
```

### ユースケース2: 環境データの拡張のためのバッチ処理

```python
import json
from datetime import datetime

# バッチ処理の設定
settings = {
    "object_types": ["empty can", "plastic bottle"],
    "scenes_per_object": 10,
    "prompts_per_scene": 3,
    "min_objects": 1,
    "max_objects": 5
}

# 結果を格納する辞書
batch_results = {
    "generated_date": datetime.now().isoformat(),
    "settings": settings,
    "results": {}
}

# 各オブジェクトタイプに対して処理
for obj_type in settings["object_types"]:
    # 多様なシーンを生成
    scenes = generator.generate_diverse_scenes(
        obj_type, 
        num_scenes=settings["scenes_per_object"]
    )
    
    batch_results["results"][obj_type] = {
        "scenes": scenes,
        "prompts": []
    }
    
    # 各シーンに対してプロンプトを生成
    for scene in scenes:
        for _ in range(settings["prompts_per_scene"]):
            result = generator.generate_realistic_prompt(
                object_name=obj_type,
                scene_type=scene,
                min_objects=settings["min_objects"],
                max_objects=settings["max_objects"]
            )
            batch_results["results"][obj_type]["prompts"].append(result)
    
    print(f"{obj_type}: {len(batch_results['results'][obj_type]['prompts'])} プロンプト生成完了")

# 結果をJSONファイルに保存
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"batch_prompts_{timestamp}.json"

with open(output_file, "w") as f:
    json.dump(batch_results, f, indent=2, ensure_ascii=False)

print(f"バッチ処理結果が {output_file} に保存されました")
```

### ユースケース3: リアルタイムプロンプト生成APIの実装

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# 依存関係としてのPromptGenerator
def get_prompt_generator():
    try:
        return PromptGenerator()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

# リクエストモデル
class PromptRequest(BaseModel):
    object_type: str
    scene_type: Optional[str] = None
    num_objects: Optional[int] = None
    advanced: bool = False

# レスポンスモデル
class PromptResponse(BaseModel):
    prompt: str
    scene: str
    object_type: str
    object_count: int

# シンプルなプロンプト生成エンドポイント
@app.post("/generate_prompt", response_model=PromptResponse)
def generate_prompt(
    request: PromptRequest,
    generator: PromptGenerator = Depends(get_prompt_generator)
):
    try:
        if request.advanced:
            result = generator.generate_realistic_prompt(
                object_name=request.object_type,
                scene_type=request.scene_type,
                num_objects=request.num_objects
            )
            return PromptResponse(
                prompt=result["prompt"],
                scene=result["scene"],
                object_type=result["object"],
                object_count=result["object_count"]
            )
        else:
            prompt, scene, count = generator.generate_simple_prompt(
                object_name=request.object_type,
                scene_type=request.scene_type,
                num_objects=request.num_objects
            )
            return PromptResponse(
                prompt=prompt,
                scene=scene,
                object_type=request.object_type,
                object_count=count
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# APIの使用例（クライアント側）:
# import requests
# response = requests.post(
#     "http://localhost:8000/generate_prompt",
#     json={"object_type": "empty can", "advanced": True}
# )
# print(response.json())
```

## トラブルシューティング

### APIキーの問題

```
ValueError: API key is required. Please provide it or set GEMINI_API_KEY in .env file.
```

**解決策**：
1. `.env`ファイルが正しく作成されていることを確認
2. 環境変数が読み込まれていることを確認
3. APIキーを直接コンストラクタに渡す

```python
import os
from dotenv import load_dotenv
from studio_data_tools.core.prompt_generator import PromptGenerator

# 環境変数を明示的に読み込む
load_dotenv()
print(f"環境変数GEMINI_API_KEYが設定されています: {'GEMINI_API_KEY' in os.environ}")

# もしくはAPIキーを直接渡す
generator = PromptGenerator(api_key="your_api_key_here")
```

### LLM API エラー

LLM APIでエラーが発生した場合、システムは自動的に静的な生成方法にフォールバックします。以下のようなログメッセージが表示されることがあります：

```
Warning: Failed to generate scenes with LLM, using default scenes instead.
Error generating realistic prompt: HTTPError: HTTP status code 400: Unsupported response format (not JSON): ...
```

**解決策**：
1. APIレート制限のタイミング調整のため、リクエスト間に遅延を追加
2. APIキーが有効であることを確認
3. ネットワーク接続を確認
4. 静的生成を明示的に使用（APIに依存しない）

```python
import time

# API呼び出し間隔を空けてレート制限を回避
for i in range(5):
    prompt, scene, count = generator.generate_simple_prompt("empty can")
    print(f"プロンプト {i+1} 生成完了")
    time.sleep(1)  # APIコールの間に1秒待機
```

### オブジェクトタイプが見つからない

```
ValueError: Unsupported object type: ...
```

**解決策**：
サポートされているオブジェクトタイプを使用するか、新しいタイプをOBJECT_SCENE_MAPに追加します。

```python
from studio_data_tools.core.prompt_generator import OBJECT_SCENE_MAP

# サポートされているオブジェクトタイプを確認
print("サポートされているオブジェクトタイプ:", list(OBJECT_SCENE_MAP.keys()))
``` 