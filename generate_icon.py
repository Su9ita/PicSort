"""
PicSort - アイコン生成スクリプト
画像フォルダのようなアイコンを生成します
"""

from PIL import Image, ImageDraw

def generate_icon():
    """PicSortのアイコンを生成"""
    # 256x256のキャンバスを作成（透明背景）
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # フォルダの色（明るい青）
    folder_color = (52, 152, 219, 255)
    # 画像のアクセントカラー（オレンジ）
    image_color = (230, 126, 34, 255)
    # 影の色
    shadow_color = (0, 0, 0, 80)

    # 影を描画
    shadow_offset = 8
    folder_points = [
        (30 + shadow_offset, 80 + shadow_offset),
        (80 + shadow_offset, 80 + shadow_offset),
        (100 + shadow_offset, 60 + shadow_offset),
        (210 + shadow_offset, 60 + shadow_offset),
        (210 + shadow_offset, 210 + shadow_offset),
        (30 + shadow_offset, 210 + shadow_offset)
    ]
    draw.polygon(folder_points, fill=shadow_color)

    # フォルダ本体を描画
    folder_points = [
        (30, 80),
        (80, 80),
        (100, 60),
        (210, 60),
        (210, 210),
        (30, 210)
    ]
    draw.polygon(folder_points, fill=folder_color)

    # フォルダの縁取り
    draw.polygon(folder_points, outline=(41, 128, 185, 255), width=3)

    # 画像アイコン（山と太陽のシンプルなイラスト）を描画
    # 太陽
    sun_center = (140, 110)
    sun_radius = 15
    draw.ellipse(
        [sun_center[0] - sun_radius, sun_center[1] - sun_radius,
         sun_center[0] + sun_radius, sun_center[1] + sun_radius],
        fill=image_color
    )

    # 山（2つの三角形）
    # 左の山
    mountain1 = [
        (70, 180),
        (100, 130),
        (130, 180)
    ]
    draw.polygon(mountain1, fill=(41, 128, 185, 255))

    # 右の山
    mountain2 = [
        (110, 180),
        (150, 120),
        (190, 180)
    ]
    draw.polygon(mountain2, fill=(52, 152, 219, 255))

    # 複数サイズのアイコンを作成（.icoファイル用）
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = [img.resize(size, Image.Resampling.LANCZOS) for size in icon_sizes]

    # .icoファイルとして保存
    img.save('icon.ico', format='ICO', sizes=icon_sizes)
    print("✓ アイコンファイルを生成しました: icon.ico")

    # プレビュー用にPNGも保存
    img.save('icon_preview.png', format='PNG')
    print("✓ プレビューファイルを生成しました: icon_preview.png")


if __name__ == "__main__":
    print("=" * 60)
    print("PicSort - アイコン生成")
    print("=" * 60)
    print("\nアイコンを生成しています...\n")

    try:
        generate_icon()
        print("\n" + "=" * 60)
        print("完了しました！")
        print("=" * 60)
    except ImportError:
        print("エラー: Pillowライブラリが必要です")
        print("\n以下のコマンドでインストールしてください：")
        print("  pip install Pillow")
    except Exception as e:
        print(f"エラー: {e}")

    input("\nEnterキーを押して終了...")
