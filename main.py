"""
PicSort - 画像ファイル自動振り分けツール GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import winsound
from organizer import Config, FileOrganizer


# システム音のマッピング
SOUND_MAP = {
    1: winsound.MB_OK,
    2: winsound.MB_ICONASTERISK,
    3: winsound.MB_ICONEXCLAMATION,
    4: winsound.MB_ICONHAND,
    5: winsound.MB_ICONQUESTION
}


class FileOrganizerApp:
    """ファイル振り分けGUIアプリケーション"""

    def __init__(self, root):
        self.root = root
        self.root.title("PicSort - 画像ファイル自動振り分けツール")
        self.root.geometry("800x600")

        # アイコンを設定
        try:
            # PyInstallerでEXE化した場合のパスを取得
            if getattr(sys, 'frozen', False):
                # EXE化されている場合
                base_path = sys._MEIPASS
            else:
                # 通常のPythonスクリプトとして実行されている場合
                base_path = os.path.dirname(os.path.abspath(__file__))

            icon_path = os.path.join(base_path, 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass  # アイコン設定に失敗しても続行

        # 設定を読み込み
        self.config = Config()
        self.organizer = FileOrganizer(self.config, self.log_message)

        # ソート状態を保持
        self.sort_column = None
        self.sort_reverse = False

        # UIを構築
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        """UIウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # ウィンドウのサイズ調整を有効化
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # === ソースフォルダ設定エリア ===
        source_frame = ttk.LabelFrame(main_frame, text="ダウンロード元フォルダ", padding="5")
        source_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        source_frame.columnconfigure(0, weight=1)

        source_inner_frame = ttk.Frame(source_frame)
        source_inner_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        source_inner_frame.columnconfigure(0, weight=1)

        self.source_folder_var = tk.StringVar()
        ttk.Entry(source_inner_frame, textvariable=self.source_folder_var, state="readonly").grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5)
        )
        ttk.Button(source_inner_frame, text="フォルダを選択", command=self.select_source_folder).grid(
            row=0, column=1
        )

        # === 振り分けルール管理エリア ===
        rules_frame = ttk.LabelFrame(main_frame, text="振り分けルール", padding="5")
        rules_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        rules_frame.columnconfigure(0, weight=1)

        # テーブル
        table_frame = ttk.Frame(rules_frame)
        table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Treeview（テーブル）
        self.tree = ttk.Treeview(table_frame, columns=("pattern", "destination"), show="headings", height=8)
        self.tree.heading("pattern", text="条件（含まれる文字列）", command=lambda: self.sort_by_column("pattern"))
        self.tree.heading("destination", text="振り分け先フォルダ", command=lambda: self.sort_by_column("destination"))
        self.tree.column("pattern", width=200)
        self.tree.column("destination", width=400)

        # スクロールバー
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # ボタン
        button_frame = ttk.Frame(rules_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Button(button_frame, text="追加", command=self.add_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="編集", command=self.edit_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="削除", command=self.delete_rule).pack(side=tk.LEFT, padx=(0, 5))

        # エクスポート・インポートボタン（右側）
        ttk.Button(button_frame, text="エクスポート", command=self.export_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="インポート", command=self.import_settings).pack(side=tk.RIGHT)

        # === 実行ボタン ===
        execute_frame = ttk.Frame(main_frame)
        execute_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(execute_frame, text="今すぐ実行", command=self.execute_organize, style="Accent.TButton").pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(execute_frame, text="ログをクリア", command=self.clear_log).pack(side=tk.LEFT)

        # === ログ表示エリア ===
        log_frame = ttk.LabelFrame(main_frame, text="実行ログ", padding="5")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state="disabled", wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def load_settings(self):
        """設定を読み込んでUIに反映"""
        # ソースフォルダ
        self.source_folder_var.set(self.config.get_source_folder())

        # 振り分けルール
        self.refresh_rules_table()

    def refresh_rules_table(self):
        """振り分けルールのテーブルを更新"""
        # 既存の項目をクリア
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 設定から読み込んで追加
        for mapping in self.config.get_mappings():
            self.tree.insert("", tk.END, values=(mapping["pattern"], mapping["destination"]))

    def select_source_folder(self):
        """ソースフォルダを選択"""
        folder = filedialog.askdirectory(title="ダウンロード元フォルダを選択")
        if folder:
            self.source_folder_var.set(folder)
            self.config.set_source_folder(folder)
            self.log_message(f"ソースフォルダを設定: {folder}")

    def add_rule(self):
        """振り分けルールを追加"""
        dialog = RuleDialog(self.root, "振り分けルールを追加")
        if dialog.result:
            pattern, destination = dialog.result
            self.config.add_mapping(pattern, destination)
            self.refresh_rules_table()
            self.log_message(f"ルールを追加: {pattern} → {destination}")

    def edit_rule(self):
        """選択された振り分けルールを編集"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "編集するルールを選択してください")
            return

        # 選択されたアイテムのインデックスを取得
        item = selection[0]
        index = self.tree.index(item)

        # 現在の値を取得
        values = self.tree.item(item, "values")
        current_pattern = values[0]
        current_destination = values[1]

        # ダイアログを表示
        dialog = RuleDialog(self.root, "振り分けルールを編集", current_pattern, current_destination)
        if dialog.result:
            pattern, destination = dialog.result
            self.config.update_mapping(index, pattern, destination)
            self.refresh_rules_table()
            self.log_message(f"ルールを更新: {pattern} → {destination}")

    def delete_rule(self):
        """選択された振り分けルールを削除"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "削除するルールを選択してください")
            return

        if messagebox.askyesno("確認", "選択されたルールを削除しますか？"):
            item = selection[0]
            index = self.tree.index(item)
            self.config.delete_mapping(index)
            self.refresh_rules_table()
            self.log_message("ルールを削除しました")

    def export_settings(self):
        """設定をエクスポート"""
        import json
        from datetime import datetime

        # デフォルトのファイル名（日時付き）
        default_filename = f"PicSort_設定_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # ファイル保存ダイアログ
        filename = filedialog.asksaveasfilename(
            title="設定をエクスポート",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=default_filename
        )

        if not filename:
            return

        try:
            # 現在の設定をファイルに保存
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.config.data, f, indent=2, ensure_ascii=False)

            self.log_message(f"設定をエクスポートしました: {filename}")
            messagebox.showinfo("成功", f"設定をエクスポートしました\n\n{filename}")

        except Exception as e:
            self.log_message(f"エクスポートエラー: {e}")
            messagebox.showerror("エラー", f"設定のエクスポートに失敗しました\n\n{e}")

    def import_settings(self):
        """設定をインポート"""
        import json

        # ファイル選択ダイアログ
        filename = filedialog.askopenfilename(
            title="設定をインポート",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not filename:
            return

        # 確認ダイアログ
        if not messagebox.askyesno(
            "確認",
            "現在の設定を上書きしてインポートしますか？\n\n"
            "※ 現在の設定は失われます。\n"
            "※ 事前にエクスポートしてバックアップすることをおすすめします。"
        ):
            return

        try:
            # ファイルから設定を読み込み
            with open(filename, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)

            # 設定の検証
            if not isinstance(imported_data, dict):
                raise ValueError("無効な設定ファイルです")

            if "mappings" not in imported_data:
                raise ValueError("振り分けルールが含まれていません")

            # 設定を更新
            self.config.data = imported_data
            self.config.save()

            # UIを更新
            self.load_settings()

            self.log_message(f"設定をインポートしました: {filename}")
            messagebox.showinfo(
                "成功",
                f"設定をインポートしました\n\n{filename}\n\n"
                f"ルール数: {len(imported_data.get('mappings', []))}"
            )

        except json.JSONDecodeError as e:
            error_msg = (
                f"JSONファイルの形式が正しくありません\n\n"
                f"エラー箇所: {e.lineno}行目 {e.colno}列目\n"
                f"詳細: {e.msg}\n\n"
                f"ファイルが破損しているか、手動で編集された可能性があります。\n"
                f"PicSortから正しくエクスポートされたファイルを使用してください。"
            )
            self.log_message(f"インポートエラー (JSON形式): {e}")
            messagebox.showerror("JSONエラー", error_msg)

        except ValueError as e:
            self.log_message(f"インポートエラー (検証): {e}")
            messagebox.showerror("エラー", f"設定ファイルの検証に失敗しました\n\n{e}")

        except Exception as e:
            self.log_message(f"インポートエラー: {e}")
            messagebox.showerror("エラー", f"設定のインポートに失敗しました\n\n{e}")

    def execute_organize(self):
        """ファイル振り分けを実行"""
        if not self.config.get_source_folder():
            messagebox.showwarning("警告", "ソースフォルダを設定してください")
            return

        if not self.config.get_mappings():
            messagebox.showwarning("警告", "振り分けルールを追加してください")
            return

        self.log_message("=" * 50)
        self.log_message("ファイル振り分けを開始します...")

        stats = self.organizer.organize()

        self.log_message("=" * 50)

        # 通知音を再生
        self.play_notification_sound()

        # カスタム完了ダイアログ（システム音が鳴らない）
        self.show_completion_dialog(stats)

    def log_message(self, message: str):
        """ログメッセージを表示"""
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)

    def clear_log(self):
        """ログをクリア"""
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state="disabled")

    def sort_by_column(self, column):
        """
        指定された列でルールをソート

        Args:
            column: ソート対象の列（"pattern" または "destination"）
        """
        # 同じ列をクリックした場合は昇順・降順を切り替え
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        # マッピングデータを取得
        mappings = self.config.get_mappings()

        if not mappings:
            return

        # ソートキーを決定
        if column == "pattern":
            key_func = lambda x: x["pattern"].lower()
        else:  # destination
            key_func = lambda x: x["destination"].lower()

        # ソート実行
        sorted_mappings = sorted(mappings, key=key_func, reverse=self.sort_reverse)

        # 設定を更新
        self.config.data["mappings"] = sorted_mappings
        self.config.save()

        # テーブルを更新
        self.refresh_rules_table()

        # ヘッダーにソート方向を表示
        self.update_column_headers()

    def update_column_headers(self):
        """列ヘッダーにソート方向のインジケーターを表示"""
        # パターン列
        pattern_text = "条件（含まれる文字列）"
        if self.sort_column == "pattern":
            pattern_text += " ▼" if self.sort_reverse else " ▲"
        self.tree.heading("pattern", text=pattern_text)

        # 振り分け先列
        destination_text = "振り分け先フォルダ"
        if self.sort_column == "destination":
            destination_text += " ▼" if self.sort_reverse else " ▲"
        self.tree.heading("destination", text=destination_text)

    def play_notification_sound(self):
        """通知音を再生"""
        try:
            # 設定から通知音の種類を取得
            sound_setting = self.config.data.get("notification_sound", "custom_2")

            # カスタム音の場合
            if isinstance(sound_setting, str) and sound_setting.startswith("custom_"):
                sound_number = int(sound_setting.split("_")[1])
                sound_file = f"sounds/pokon_{['simple', 'soft', 'cute', 'bright', 'mellow'][sound_number - 1]}.wav"

                if os.path.exists(sound_file):
                    winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
                else:
                    # ファイルが見つからない場合はデフォルトのシステム音
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
            # システム音の場合（後方互換性）
            elif isinstance(sound_setting, int):
                sound_type = SOUND_MAP.get(sound_setting, winsound.MB_ICONASTERISK)
                winsound.MessageBeep(sound_type)
            else:
                # デフォルト音
                winsound.MessageBeep(winsound.MB_ICONASTERISK)

        except Exception as e:
            # 音の再生に失敗しても処理は続行
            self.log_message(f"通知音の再生に失敗: {e}")

    def show_completion_dialog(self, stats):
        """完了ダイアログを表示（システム音なし）"""
        dialog = tk.Toplevel(self.root)
        dialog.title("完了")
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()

        # フレーム
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # メッセージ
        ttk.Label(
            frame,
            text="ファイル振り分けが完了しました",
            font=("", 11, "bold")
        ).pack(pady=(0, 15))

        # 統計情報
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(pady=(0, 15))

        stats_text = f"""対象ファイル数: {stats['total_files']}
移動: {stats['moved_files']}
スキップ: {stats['skipped_files']}
エラー: {stats['errors']}"""

        ttk.Label(stats_frame, text=stats_text, justify=tk.LEFT).pack()

        # OKボタン
        ttk.Button(
            frame,
            text="OK",
            command=dialog.destroy,
            width=10
        ).pack()

        # ダイアログを中央に配置
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Enterキーで閉じる
        dialog.bind("<Return>", lambda e: dialog.destroy())
        dialog.bind("<Escape>", lambda e: dialog.destroy())


class RuleDialog:
    """振り分けルール追加/編集ダイアログ"""

    def __init__(self, parent, title, pattern="", destination=""):
        self.result = None

        # ダイアログウィンドウ
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # フレーム
        frame = ttk.Frame(self.dialog, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        # 条件入力
        ttk.Label(frame, text="条件（含まれる文字列）:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.pattern_var = tk.StringVar(value=pattern)
        ttk.Entry(frame, textvariable=self.pattern_var).grid(
            row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        # 振り分け先入力
        ttk.Label(frame, text="振り分け先フォルダ:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        dest_frame = ttk.Frame(frame)
        dest_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        dest_frame.columnconfigure(0, weight=1)

        self.destination_var = tk.StringVar(value=destination)
        ttk.Entry(dest_frame, textvariable=self.destination_var).grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5)
        )
        ttk.Button(dest_frame, text="参照", command=self.select_destination).grid(row=0, column=1)

        # ボタン
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.E))

        ttk.Button(button_frame, text="OK", command=self.ok).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="キャンセル", command=self.cancel).pack(side=tk.LEFT)

        # Enterキーで確定
        self.dialog.bind("<Return>", lambda e: self.ok())
        self.dialog.bind("<Escape>", lambda e: self.cancel())

        # ダイアログを中央に配置
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # モーダル表示
        self.dialog.wait_window()

    def select_destination(self):
        """振り分け先フォルダを選択"""
        folder = filedialog.askdirectory(title="振り分け先フォルダを選択")
        if folder:
            self.destination_var.set(folder)

    def ok(self):
        """OKボタン処理"""
        pattern = self.pattern_var.get().strip()
        destination = self.destination_var.get().strip()

        if not pattern:
            messagebox.showwarning("警告", "条件を入力してください", parent=self.dialog)
            return

        if not destination:
            messagebox.showwarning("警告", "振り分け先フォルダを指定してください", parent=self.dialog)
            return

        self.result = (pattern, destination)
        self.dialog.destroy()

    def cancel(self):
        """キャンセルボタン処理"""
        self.dialog.destroy()


def main():
    """メイン関数"""
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
