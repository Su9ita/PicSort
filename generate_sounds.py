"""
PicSort - カスタム通知音生成ツール
「ポコン」系のかわいい効果音を生成します。
"""

import numpy as np
import wave
import os


def apply_envelope(signal, attack=0.01, decay=0.05, sustain_level=0.3, release=0.1, sample_rate=44100):
    """
    ADSR エンベロープを適用

    Args:
        signal: 入力信号
        attack: アタック時間（秒）
        decay: ディケイ時間（秒）
        sustain_level: サステインレベル（0-1）
        release: リリース時間（秒）
        sample_rate: サンプリングレート

    Returns:
        エンベロープを適用した信号
    """
    length = len(signal)
    envelope = np.ones(length)

    # Attack
    attack_samples = int(attack * sample_rate)
    if attack_samples > 0 and attack_samples < length:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay
    decay_samples = int(decay * sample_rate)
    decay_end = min(attack_samples + decay_samples, length)
    if decay_samples > 0 and decay_end > attack_samples:
        envelope[attack_samples:decay_end] = np.linspace(1, sustain_level, decay_end - attack_samples)

    # Sustain (constant level)
    sustain_end = max(0, length - int(release * sample_rate))
    if sustain_end > decay_end:
        envelope[decay_end:sustain_end] = sustain_level

    # Release
    if sustain_end < length:
        envelope[sustain_end:] = np.linspace(sustain_level, 0, length - sustain_end)

    return signal * envelope


def generate_pokon_simple(filename="pokon_simple.wav"):
    """
    シンプルなポコン音を生成
    高めの音で短く明るい音
    """
    sample_rate = 44100
    duration = 0.15  # 150ms
    frequency = 800  # 高めの音

    t = np.linspace(0, duration, int(sample_rate * duration))

    # 基本波形（サイン波）
    signal = np.sin(2 * np.pi * frequency * t)

    # ピッチベンド（高音から少し下がる）
    pitch_bend = np.linspace(1.2, 1.0, len(t))
    signal = np.sin(2 * np.pi * frequency * t * pitch_bend)

    # エンベロープ適用（短くてパキッとした音）
    signal = apply_envelope(signal, attack=0.005, decay=0.04, sustain_level=0.2, release=0.1)

    # 正規化
    signal = signal / np.max(np.abs(signal)) * 0.7

    # 16ビット整数に変換
    signal_int = np.int16(signal * 32767)

    # WAVファイルに保存
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # モノラル
        wav_file.setsampwidth(2)  # 16ビット
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(signal_int.tobytes())

    return filename


def generate_pokon_soft(filename="pokon_soft.wav"):
    """
    柔らかいポコン音を生成
    倍音を含んだ優しい音
    """
    sample_rate = 44100
    duration = 0.2  # 200ms
    frequency = 600  # 中音

    t = np.linspace(0, duration, int(sample_rate * duration))

    # 基本波形 + 倍音
    signal = (
        np.sin(2 * np.pi * frequency * t) * 0.7 +
        np.sin(2 * np.pi * frequency * 2 * t) * 0.2 +
        np.sin(2 * np.pi * frequency * 3 * t) * 0.1
    )

    # エンベロープ適用（柔らかい音）
    signal = apply_envelope(signal, attack=0.01, decay=0.08, sustain_level=0.3, release=0.11)

    # 正規化
    signal = signal / np.max(np.abs(signal)) * 0.7

    # 16ビット整数に変換
    signal_int = np.int16(signal * 32767)

    # WAVファイルに保存
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(signal_int.tobytes())

    return filename


def generate_pokon_cute(filename="pokon_cute.wav"):
    """
    かわいいポコン音を生成
    ピッチベンド付きで遊び心のある音
    """
    sample_rate = 44100
    duration = 0.18  # 180ms
    frequency = 900  # 高め

    t = np.linspace(0, duration, int(sample_rate * duration))

    # ピッチベンド（ポーンと上がってコンと下がる）
    pitch_curve = np.concatenate([
        np.linspace(1.0, 1.3, len(t) // 3),
        np.linspace(1.3, 0.9, 2 * len(t) // 3)
    ])

    # 基本波形
    signal = np.sin(2 * np.pi * frequency * t * pitch_curve)

    # 少し倍音を追加
    signal += np.sin(2 * np.pi * frequency * 2 * t * pitch_curve) * 0.15

    # エンベロープ適用
    signal = apply_envelope(signal, attack=0.008, decay=0.05, sustain_level=0.25, release=0.12)

    # 正規化
    signal = signal / np.max(np.abs(signal)) * 0.7

    # 16ビット整数に変換
    signal_int = np.int16(signal * 32767)

    # WAVファイルに保存
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(signal_int.tobytes())

    return filename


def generate_pokon_bright(filename="pokon_bright.wav"):
    """
    明るいポコン音を生成
    明るくて元気な音
    """
    sample_rate = 44100
    duration = 0.16  # 160ms
    frequency = 1000  # 高音

    t = np.linspace(0, duration, int(sample_rate * duration))

    # 基本波形 + 明るい倍音
    signal = (
        np.sin(2 * np.pi * frequency * t) * 0.6 +
        np.sin(2 * np.pi * frequency * 2 * t) * 0.25 +
        np.sin(2 * np.pi * frequency * 4 * t) * 0.15
    )

    # 短いピッチベンド
    pitch_bend = np.linspace(1.15, 1.0, len(t))
    signal = signal * np.sin(2 * np.pi * t * pitch_bend)

    # エンベロープ適用（短めでパキッと）
    signal = apply_envelope(signal, attack=0.003, decay=0.03, sustain_level=0.2, release=0.13)

    # 正規化
    signal = signal / np.max(np.abs(signal)) * 0.7

    # 16ビット整数に変換
    signal_int = np.int16(signal * 32767)

    # WAVファイルに保存
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(signal_int.tobytes())

    return filename


def generate_pokon_mellow(filename="pokon_mellow.wav"):
    """
    まろやかなポコン音を生成
    耳に優しい落ち着いた音
    """
    sample_rate = 44100
    duration = 0.22  # 220ms
    frequency = 550  # 中低音

    t = np.linspace(0, duration, int(sample_rate * duration))

    # 基本波形（倍音多め）
    signal = (
        np.sin(2 * np.pi * frequency * t) * 0.5 +
        np.sin(2 * np.pi * frequency * 2 * t) * 0.3 +
        np.sin(2 * np.pi * frequency * 3 * t) * 0.15 +
        np.sin(2 * np.pi * frequency * 4 * t) * 0.05
    )

    # エンベロープ適用（ゆったりめ）
    signal = apply_envelope(signal, attack=0.015, decay=0.1, sustain_level=0.35, release=0.105)

    # 正規化
    signal = signal / np.max(np.abs(signal)) * 0.7

    # 16ビット整数に変換
    signal_int = np.int16(signal * 32767)

    # WAVファイルに保存
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(signal_int.tobytes())

    return filename


def main():
    """すべての音を生成"""
    print("=" * 60)
    print("PicSort - カスタム通知音生成ツール")
    print("=" * 60)
    print("\n「ポコン」系の効果音を生成します...\n")

    sounds_dir = "sounds"
    if not os.path.exists(sounds_dir):
        os.makedirs(sounds_dir)
        print(f"フォルダを作成: {sounds_dir}")

    sounds = [
        ("シンプルなポコン", lambda: generate_pokon_simple(f"{sounds_dir}/pokon_simple.wav")),
        ("柔らかいポコン", lambda: generate_pokon_soft(f"{sounds_dir}/pokon_soft.wav")),
        ("かわいいポコン", lambda: generate_pokon_cute(f"{sounds_dir}/pokon_cute.wav")),
        ("明るいポコン", lambda: generate_pokon_bright(f"{sounds_dir}/pokon_bright.wav")),
        ("まろやかなポコン", lambda: generate_pokon_mellow(f"{sounds_dir}/pokon_mellow.wav"))
    ]

    for name, generator in sounds:
        print(f"生成中: {name}...", end=" ", flush=True)
        try:
            filename = generator()
            print(f"✓ 完了 ({filename})")
        except Exception as e:
            print(f"✗ エラー: {e}")

    print("\n" + "=" * 60)
    print(f"すべての音を '{sounds_dir}' フォルダに保存しました。")
    print("次に「音を選択.bat」を実行して、好きな音を選んでください。")
    print("=" * 60)

    input("\nEnterキーを押して終了...")


if __name__ == "__main__":
    main()
