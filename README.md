# makeandroidicon

入力画像から白い余白を除去し、Androidアプリ向けのランチャーアイコン素材を自動生成するCLIツールです。ビルド済みのアイコンは density ごとの `mipmap-*` ディレクトリと Play ストア提出用の 512px アイコンとして出力されます。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt  # pytest / black / ruff などの開発用ツール
```

## 使い方

インストール後は `python -m makeandroidicon`、`python main.py`、またはエントリーポイントの `makeandroidicon` コマンドが利用できます。

```bash
makeandroidicon path/to/source.png --output build/icons
```

### 主なオプション

- `--tolerance`: 白背景を検出するための許容値 (0〜255、デフォルト10)。背景がやや灰色の場合は大きめに調整します。
- `--filename`: 各 density フォルダ内に書き出すファイル名。既定値は `ic_launcher.png`。

背景は外周から同じ色（許容値以内）の領域を探索し、透明化したあとでトリミングするため、四隅の白地などは自動的に透過へ変換されます。アイコン内部の白いパーツは背景に連続していない限り保持されます。

### 出力例

```
build/icons/
├── mipmap-mdpi/ic_launcher.png   # 48x48 px
├── mipmap-hdpi/ic_launcher.png   # 72x72 px
├── mipmap-xhdpi/ic_launcher.png  # 96x96 px
├── mipmap-xxhdpi/ic_launcher.png # 144x144 px
├── mipmap-xxxhdpi/ic_launcher.png# 192x192 px
└── play-store/ic_launcher.png    # 512x512 px
```

## テスト

```bash
venv/bin/python -m pytest
```

※ 事前に `pip install -r requirements-dev.txt` で `pytest` をインストールしてください。
