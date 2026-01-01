"""
PicSort - バックグラウンド実行用スクリプト
GUIウィンドウを表示せずにファイル振り分けを実行します。
タスクスケジューラでの定期実行に最適です。
"""

from organizer import Config, FileOrganizer
import logging
from datetime import datetime

# ログファイルの設定（オプション）
logging.basicConfig(
    filename='organizer.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding='utf-8'
)

def log_message(message):
    """ログメッセージを記録"""
    logging.info(message)

# 設定を読み込み
config = Config()

# ファイル振り分けを実行
organizer = FileOrganizer(config, log_message)
stats = organizer.organize()

# 結果をログに記録
logging.info(f"実行完了 - 移動: {stats['moved_files']}, スキップ: {stats['skipped_files']}, エラー: {stats['errors']}")
