"""
PicSort - 画像ファイル自動振り分けツールのコアロジック
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Callable


class Config:
    """設定管理クラス"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.data = self._load_config()

    def _load_config(self) -> dict:
        """設定ファイルを読み込む"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"設定ファイル読み込みエラー: {e}")
                return self._default_config()
        return self._default_config()

    def _default_config(self) -> dict:
        """デフォルト設定"""
        return {
            "source_folder": "",
            "mappings": []
        }

    def save(self):
        """設定をファイルに保存"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, indent=2, ensure_ascii=False, fp=f)
        except Exception as e:
            raise Exception(f"設定ファイル保存エラー: {e}")

    def get_source_folder(self) -> str:
        """ソースフォルダのパスを取得"""
        return self.data.get("source_folder", "")

    def set_source_folder(self, path: str):
        """ソースフォルダのパスを設定"""
        self.data["source_folder"] = path
        self.save()

    def get_mappings(self) -> List[Dict[str, str]]:
        """振り分けルールのリストを取得"""
        return self.data.get("mappings", [])

    def add_mapping(self, pattern: str, destination: str):
        """振り分けルールを追加"""
        self.data["mappings"].append({
            "pattern": pattern,
            "destination": destination
        })
        self.save()

    def update_mapping(self, index: int, pattern: str, destination: str):
        """振り分けルールを更新"""
        if 0 <= index < len(self.data["mappings"]):
            self.data["mappings"][index] = {
                "pattern": pattern,
                "destination": destination
            }
            self.save()

    def delete_mapping(self, index: int):
        """振り分けルールを削除"""
        if 0 <= index < len(self.data["mappings"]):
            self.data["mappings"].pop(index)
            self.save()


class FileOrganizer:
    """ファイル振り分けクラス"""

    def __init__(self, config: Config, log_callback: Optional[Callable[[str], None]] = None):
        """
        初期化

        Args:
            config: 設定オブジェクト
            log_callback: ログ出力用のコールバック関数
        """
        self.config = config
        self.log_callback = log_callback or print

    def log(self, message: str):
        """ログを出力"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_callback(log_message)

    def organize(self) -> Dict[str, int]:
        """
        ファイルを振り分ける

        Returns:
            統計情報（移動したファイル数、エラー数など）
        """
        source_folder = self.config.get_source_folder()
        mappings = self.config.get_mappings()

        stats = {
            "total_files": 0,
            "moved_files": 0,
            "skipped_files": 0,
            "errors": 0
        }

        if not source_folder or not os.path.exists(source_folder):
            self.log(f"エラー: ソースフォルダが存在しません: {source_folder}")
            return stats

        if not mappings:
            self.log("警告: 振り分けルールが設定されていません")
            return stats

        self.log(f"振り分け開始: {source_folder}")

        # ソースフォルダ内のファイルを走査
        try:
            files = [f for f in os.listdir(source_folder)
                    if os.path.isfile(os.path.join(source_folder, f))]
            stats["total_files"] = len(files)

            self.log(f"対象ファイル数: {len(files)}")

            for filename in files:
                source_path = os.path.join(source_folder, filename)
                moved = False

                # 各マッピングルールをチェック
                for mapping in mappings:
                    pattern = mapping["pattern"]
                    destination_folder = mapping["destination"]

                    if pattern in filename:
                        # パターンにマッチした場合、ファイルを移動
                        try:
                            self._move_file(source_path, destination_folder, filename)
                            stats["moved_files"] += 1
                            moved = True
                            break
                        except Exception as e:
                            self.log(f"エラー: {filename} の移動に失敗: {e}")
                            stats["errors"] += 1
                            break

                if not moved:
                    stats["skipped_files"] += 1

            self.log(f"振り分け完了: 移動={stats['moved_files']}, "
                    f"スキップ={stats['skipped_files']}, エラー={stats['errors']}")

        except Exception as e:
            self.log(f"エラー: ファイル走査中にエラーが発生: {e}")
            stats["errors"] += 1

        return stats

    def _move_file(self, source_path: str, destination_folder: str, filename: str):
        """
        ファイルを移動

        Args:
            source_path: 移動元ファイルのフルパス
            destination_folder: 移動先フォルダ
            filename: ファイル名
        """
        # 移動先フォルダが存在しない場合は作成
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
            self.log(f"フォルダを作成: {destination_folder}")

        destination_path = os.path.join(destination_folder, filename)

        # 同名ファイルが既に存在する場合の処理
        if os.path.exists(destination_path):
            # ファイル名に番号を付けてリネーム
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(destination_path):
                new_filename = f"{base}_{counter}{ext}"
                destination_path = os.path.join(destination_folder, new_filename)
                counter += 1
            self.log(f"同名ファイルが存在するため、リネームします: {os.path.basename(destination_path)}")

        # ファイルを移動
        shutil.move(source_path, destination_path)
        self.log(f"移動: {filename} → {destination_folder}")
