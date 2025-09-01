# 🚫 データベース変更制限ポリシー / Database Change Restriction Policy

## ⚠️ 重要な警告 / IMPORTANT WARNING

**このプロジェクトでは、データベース構造の変更は絶対に禁止されています。**
**Database structure changes are absolutely prohibited in this project.**

## 🔒 制限対象 / Restricted Areas

### 絶対に変更してはいけないファイル / Files That Must NEVER Be Modified:
- ❌ `models.py` - データベースモデル定義 / Database model definitions
- ❌ マイグレーションファイル / Migration files (if any)
- ❌ データベーススキーマ関連スクリプト / Database schema-related scripts

### 禁止されている操作 / Prohibited Operations:
- ❌ テーブルの追加・削除 / Adding or removing tables
- ❌ カラムの追加・削除・変更 / Adding, removing, or modifying columns
- ❌ インデックスの変更 / Modifying indexes
- ❌ 外部キー制約の変更 / Changing foreign key constraints
- ❌ データ型の変更 / Changing data types

## 🎯 開発指針 / Development Guidelines

新機能を実装する際は、必ず以下の原則に従ってください：
When implementing new features, always follow these principles:

1. **既存構造の活用 / Use Existing Structure**
   - 現在の3つのテーブル（Recipient, Seminar, Attendance）で実現可能な方法を考える
   - Think of ways to achieve goals with the current 3 tables

2. **データ加工でカバー / Cover with Data Processing**
   - 必要な情報は既存データの結合・加工で取得する
   - Obtain required information by joining and processing existing data

3. **ビューレイヤーでの対応 / Handle in View Layer**
   - 表示用の複雑なデータはテンプレートやビューで加工する
   - Process complex display data in templates or views

## 📝 現在のデータベース構造 / Current Database Structure

### 確定済みの構造（変更不可）/ Finalized Structure (Immutable):

```python
# Recipient テーブル - 参加者情報
class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    affiliation = db.Column(db.String(100))
    phone = db.Column(db.String(20))

# Seminar テーブル - セミナー情報  
class Seminar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    date = db.Column(db.DateTime)
    venue = db.Column(db.String(200))
    speaker = db.Column(db.String(100))
    topic = db.Column(db.String(200))
    contact = db.Column(db.String(100))

# Attendance テーブル - 出欠情報
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id'))
    seminar_id = db.Column(db.Integer, db.ForeignKey('seminar.id'))
    status = db.Column(db.String(20))
    comment = db.Column(db.String(500))
    recipient = relationship("Recipient", backref="attendances")
```

## 🤝 協力のお願い / Request for Cooperation

この制限により、以下のメリットが得られます：
These restrictions provide the following benefits:

- ✅ システム安定性の維持 / Maintaining system stability
- ✅ 既存データの整合性保証 / Ensuring existing data consistency  
- ✅ 運用リスクの最小化 / Minimizing operational risks
- ✅ 予期しない障害の防止 / Preventing unexpected failures

ご理解とご協力をお願いいたします。
We appreciate your understanding and cooperation.

---

📚 詳細なガイドラインは [CONTRIBUTING.md](CONTRIBUTING.md) をご確認ください。
For detailed guidelines, please see [CONTRIBUTING.md](CONTRIBUTING.md).