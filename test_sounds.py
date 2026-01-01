"""
PicSort - 通知音テストツール
カスタム生成した「ポコン」音の候補を再生して、好きな音を選択できます。
"""

import winsound
import time
import os
from organizer import Config

# soundsフォルダ内の音ファイル
SOUNDS_DIR = "sounds"
SOUNDS = {
    1: {
        "name": "シンプルなポコン（高めの音で短く明るい）",
        "file": f"{SOUNDS_DIR}/pokon_simple.wav"
    },
    2: {
        "name": "柔らかいポコン（倍音を含んだ優しい音）",
        "file": f"{SOUNDS_DIR}/pokon_soft.wav"
    },
    3: {
        "name": "かわいいポコン（ピッチベンド付き）",
        "file": f"{SOUNDS_DIR}/pokon_cute.wav"
    },
    4: {
        "name": "明るいポコン（明るくて元気な音）",
        "file": f"{SOUNDS_DIR}/pokon_bright.wav"
    },
    5: {
        "name": "まろやかなポコン（耳に優しい落ち着いた音）",
        "file": f"{SOUNDS_DIR}/pokon_mellow.wav"
    }
}


def check_sound_files():
    """音ファイルが存在するか確認"""
    if not os.path.exists(SOUNDS_DIR):
        return False

    for sound_info in SOUNDS.values():
        if not os.path.exists(sound_info["file"]):
            return False

    return True


def play_sound(filename):
    """指定された音ファイルを再生"""
    try:
        winsound.PlaySound(filename, winsound.SND_FILENAME)
    except Exception as e:
        print(f"音の再生に失敗しました: {e}")


def test_all_sounds():
    """すべての候補音を順番に再生"""
    print("=" * 60)
    print("PicSort - 通知音選択ツール")
    print("=" * 60)
    print("\n各カスタム音を順番に再生します...\n")

    for num, sound_info in SOUNDS.items():
        print(f"[{num}] {sound_info['name']}")
        print("    再生中...", end=" ", flush=True)
        play_sound(sound_info['file'])
        time.sleep(0.3)  # 少し待機
        print("完了")
        time.sleep(1.2)  # 次の音まで間隔を空ける

    print("\n" + "=" * 60)


def select_sound():
    """ユーザーに音を選択させる"""
    while True:
        print("\n好きな音の番号を入力してください (1-5):")
        print("もう一度聞きたい場合は 0 を入力してください")
        print("終了する場合は q を入力してください")

        choice = input("\n選択: ").strip()

        if choice.lower() == 'q':
            print("\n設定を変更せずに終了します。")
            return None

        if choice == '0':
            test_all_sounds()
            continue

        try:
            num = int(choice)
            if num in SOUNDS:
                # 選択した音を再生して確認
                print(f"\n選択した音: [{num}] {SOUNDS[num]['name']}")
                print("確認のため再生します...", end=" ", flush=True)
                play_sound(SOUNDS[num]['file'])
                print("完了")

                # 確認
                confirm = input("\nこの音でよろしいですか？ (y/n): ").strip().lower()
                if confirm == 'y':
                    return num
                else:
                    print("\nもう一度選択してください。")
            else:
                print(f"\nエラー: 1-5 の番号を入力してください。")
        except ValueError:
            print(f"\nエラー: 有効な番号を入力してください。")


def save_sound_setting(sound_number):
    """選択した音を設定ファイルに保存"""
    try:
        config = Config()
        config.data["notification_sound"] = f"custom_{sound_number}"
        config.save()
        print(f"\n✓ 通知音を設定しました: [{sound_number}] {SOUNDS[sound_number]['name']}")
        print("設定はconfig.jsonに保存されました。")
    except Exception as e:
        print(f"\nエラー: 設定の保存に失敗しました: {e}")


def main():
    """メイン処理"""
    # 音ファイルの存在確認
    if not check_sound_files():
        print("=" * 60)
        print("エラー: 音ファイルが見つかりません")
        print("=" * 60)
        print("\n最初に音を生成する必要があります。")
        print("以下のいずれかの方法で音を生成してください：\n")
        print("1. コマンドプロンプトで実行:")
        print("   python generate_sounds.py\n")
        print("2. または、numpyをインストール:")
        print("   pip install numpy")
        print("   その後、もう一度 python generate_sounds.py を実行\n")
        print("=" * 60)
        input("\nEnterキーを押して終了...")
        return

    # すべての音を順番に再生
    test_all_sounds()

    # ユーザーに音を選択させる
    selected = select_sound()

    if selected:
        # 設定を保存
        save_sound_setting(selected)
        print("\nPicSortを再起動すると、新しい通知音が適用されます。")

    print("\n" + "=" * 60)
    input("\nEnterキーを押して終了...")


if __name__ == "__main__":
    main()
