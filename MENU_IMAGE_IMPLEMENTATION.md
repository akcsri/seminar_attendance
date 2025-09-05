# 🖼️ メニュー画像表示機能実装ガイド / Menu Image Display Implementation Guide

## 📋 概要 / Overview

注文フォームのメニュー項目に画像表示機能を追加しました。データベース変更制限ポリシーに準拠し、フロントエンドのみでの実装として対応しています。

Added image display functionality to menu items in the order form. Implementation complies with database change restriction policy using frontend-only solution.

## ✅ 実装内容 / Implementation Details

### 1. **画像表示ボタンの追加 / Image Display Button Addition**
- 各メニュー項目の右端に📷ボタンを追加
- Added 📷 button to the right side of each menu item

### 2. **ポップアップ機能 / Popup Functionality**  
- クリック時に画像をモーダルポップアップで表示
- Display images in modal popup when clicked
- ESCキーまたは×ボタンで閉じる機能
- Close functionality with ESC key or × button
- ポップアップ外をクリックして閉じる機能
- Click outside to close functionality

### 3. **画像URL管理システム / Image URL Management System**
- JavaScriptの設定オブジェクトで管理（データベース変更なし）
- Managed via JavaScript configuration object (no database changes)
- CSVインポートツールによる一括設定機能
- Bulk configuration via CSV import tool

## 🚫 データベース制約対応 / Database Constraints Compliance

この実装は以下の制約に完全準拠しています：
This implementation fully complies with the following restrictions:

- ❌ `models.py`の変更なし / No modifications to `models.py`
- ❌ データベーススキーマ変更なし / No database schema changes  
- ❌ 新しいテーブル・カラムの追加なし / No new tables or columns
- ✅ フロントエンドのみの実装 / Frontend-only implementation
- ✅ セミナー機能との完全分離 / Complete separation from seminar functionality

## 🔧 管理者向け設定方法 / Administrator Configuration

### 方法1: 手動設定 / Manual Configuration
`templates/lunch_order_form.html`内の`menuImages`オブジェクトを編集：

```javascript
const menuImages = {
    1: '/static/images/katsudon.jpg',        // カツ丼
    2: '/static/images/oyakodon.jpg',        // 親子丼
    // メニューID: 画像URL の形式で追加
};
```

### 方法2: CSVインポートツール使用 / CSV Import Tool Usage
```bash
cd /tmp
python3 menu_image_csv_importer.py
# オプション1を選択してサンプルCSVを生成
# Edit the CSV file with your image URLs
# オプション2を選択してJavaScript設定を生成
```

## 📁 ファイル構成 / File Structure

### 変更されたファイル / Modified Files
- `templates/lunch_order_form.html` - メインの注文フォーム / Main order form

### 新規作成ファイル / New Files
- `static/images/README.md` - 画像ディレクトリの説明 / Images directory documentation
- `/tmp/menu_image_csv_importer.py` - CSVインポートツール / CSV import tool

### 推奨ディレクトリ / Recommended Directory
- `static/images/` - メニュー画像の保存場所 / Menu images storage location

## 🎨 UI/UX機能 / UI/UX Features

- **レスポンシブデザイン / Responsive Design**: モバイル・デスクトップ対応
- **アクセシビリティ / Accessibility**: キーボード操作対応（ESCキー）
- **エラーハンドリング / Error Handling**: 画像読み込み失敗時の代替メッセージ
- **ユーザビリティ / Usability**: 直感的な操作（クリックで開く・閉じる）

## 🔄 今後の拡張性 / Future Extensibility

### 画像追加の手順 / Steps to Add Images
1. 画像ファイルを`static/images/`に配置 / Place image files in `static/images/`
2. `menuImages`オブジェクトに新しいエントリを追加 / Add new entries to `menuImages` object
3. または CSVツールを使用して一括更新 / Or use CSV tool for bulk updates

### 対応画像形式 / Supported Image Formats
- JPG, PNG, GIF, WebP
- 推奨サイズ: 300x200px / Recommended size: 300x200px
- 最大サイズ制限なし（CSS で自動リサイズ）/ No max size limit (auto-resized by CSS)

## ⚡ パフォーマンス考慮 / Performance Considerations

- **遅延読み込み / Lazy Loading**: 画像はポップアップ表示時のみ読み込み
- **キャッシュ対応 / Cache Support**: ブラウザキャッシュを活用
- **軽量実装 / Lightweight**: 外部ライブラリ不使用

## 🧪 テスト済み機能 / Tested Features

- ✅ ポップアップ表示・非表示 / Popup show/hide
- ✅ ESCキー動作 / ESC key functionality  
- ✅ 外部クリック閉じる / Click outside to close
- ✅ 画像読み込みエラー処理 / Image load error handling
- ✅ レスポンシブ表示 / Responsive display
- ✅ データベース制約準拠 / Database constraints compliance

---

## 🚀 使用開始 / Getting Started

1. メニュー画像を`static/images/`ディレクトリに配置
2. 必要に応じて`menuImages`設定を更新
3. フォームにアクセスして📷ボタンをテスト

Ready to use! Place your menu images in `static/images/` directory and update the `menuImages` configuration as needed.