# makeandroidicon

入力画像から白い余白を除去し、Androidアプリ向けのランチャーアイコン素材を自動生成するCLIツールです。ビルド済みのアイコンは density ごとの `mipmap-*` ディレクトリと Play ストア提出用の 512px アイコンとして出力されます。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt  # pytest / black / ruff などの開発用ツール

### GitHub への公開

GitHub CLI (`gh`) を利用する場合の一例です。

```bash
# GitHub へログイン（最初の一回のみ）
gh auth login

# 新規公開リポジトリを作成して push
gh repo create <USER>/<REPO> --public --source=. --remote=origin --push
```

サンドボックス環境やCI上で `gh auth` が利用できない場合は、手動で `git remote add` → `git push` を行ってください。
```

## 使い方

インストール後は `python -m makeandroidicon`、`python main.py`、またはエントリーポイントの `makeandroidicon` コマンドが利用できます。

```bash
makeandroidicon path/to/source.png --output build/icons
```

### 主なオプション

- `--tolerance`: 白背景を検出するための許容値 (0〜255、デフォルト10)。背景がやや灰色の場合は大きめに調整します。
- `--filename`: 各 density フォルダ内に書き出すファイル名。既定値は `ic_launcher.webp`。
- `--format`: 出力フォーマット（例: `webp`, `png`）。省略するとファイル拡張子から自動推測します。

背景は外周から同じ色（許容値以内）の領域を探索し、透明化したあとでトリミングするため、四隅の白地などは自動的に透過へ変換されます。アイコン内部の白いパーツは背景に連続していない限り保持されます。

### 出力例

```
build/icons/
├── mipmap-mdpi/ic_launcher.webp   # 48x48 px
├── mipmap-hdpi/ic_launcher.webp   # 72x72 px
├── mipmap-xhdpi/ic_launcher.webp  # 96x96 px
├── mipmap-xxhdpi/ic_launcher.webp # 144x144 px
├── mipmap-xxxhdpi/ic_launcher.webp# 192x192 px
└── play-store/ic_launcher.webp    # 512x512 px
```

## テスト

```bash
venv/bin/python -m pytest
```

※ 事前に `pip install -r requirements-dev.txt` で `pytest` をインストールしてください。
