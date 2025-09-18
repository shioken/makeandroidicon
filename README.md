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
- `--round-filename`: ラウンドアイコンのファイル名。既定値は `ic_launcher_round.webp`。空文字を指定すると生成をスキップします。
- `--round-format`: ラウンドアイコンのフォーマット。省略時は `--round-filename` の拡張子から推測します。
- `--adaptive`: アダプティブアイコン向けに foreground/background レイヤーと XML を生成します。
- `--adaptive-foreground`: アダプティブ foreground のファイル名（デフォルト: `ic_launcher_foreground.webp`）。
- `--adaptive-background`: アダプティブ background のファイル名（デフォルト: `ic_launcher_background.webp`）。
- `--adaptive-format`: アダプティブレイヤーのファイル形式（例: `webp`）。省略時はファイル名の拡張子から推測します。
- `--adaptive-color`: background レイヤーに使う色。`#RRGGBB` / `#AARRGGBB` / `transparent` に対応します。
- `--adaptive-scale`: foreground を背景サイズに対してどれくらい縮小するか (0〜1)。既定値は `0.9`。
- `--adaptive-xml` / `--adaptive-xml-round`: 生成する `adaptive-icon` XML 名。空文字を指定するとラウンド版 XML を省略します。

背景は外周から同じ色（許容値以内）の領域を探索し、透明化したあとでトリミングするため、四隅の白地などは自動的に透過へ変換されます。アイコン内部の白いパーツは背景に連続していない限り保持されます。

### 出力例

```
build/icons/
├── mipmap-mdpi/ic_launcher.webp        # 48x48 px（通常）
├── mipmap-mdpi/ic_launcher_round.webp  # 48x48 px（円形）
├── mipmap-hdpi/ic_launcher.webp        # 72x72 px
├── mipmap-hdpi/ic_launcher_round.webp  # 72x72 px
├── ...
└── play-store/ic_launcher.webp         # 512x512 px

`--adaptive` を付けると、追加で次のようなレイヤーと XML が生成されます。

```
build/icons/
├── mipmap-mdpi/ic_launcher_foreground.webp
├── mipmap-mdpi/ic_launcher_background.webp
├── ...
├── mipmap-xxxhdpi/ic_launcher_foreground.webp
├── mipmap-xxxhdpi/ic_launcher_background.webp
└── mipmap-anydpi-v26/
    ├── ic_launcher.xml
    └── ic_launcher_round.xml
```

## 既存のForeground/Background画像から生成する場合

すでにレイヤーが分かれている場合は、同梱のスクリプトで余白トリミングと各densityへの展開が可能です。

```bash
python scripts/generate_adaptive_from_layers.py foreground.png background.png \
  --output build/adaptive_manual \
  --format webp  # png など任意の形式に変更可能
```

- 入力画像の周囲に残る余白は自動でトリミングされ、背景に連続する色は透明化されます。
- 出力先には `mipmap-*` フォルダおよび `mipmap-anydpi-v26/` 配下の XML が作成されます。
```

## テスト

```bash
venv/bin/python -m pytest
```

※ 事前に `pip install -r requirements-dev.txt` で `pytest` をインストールしてください。
