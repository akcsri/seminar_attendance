# 貢献ガイドライン / Contributing Guidelines

## 🚫 データベース変更制限について / Database Change Restrictions

### 📌 重要なポリシー / Important Policy

**このプロジェクトでは、データベース構造の変更は一切許可されていません。**  
**Database structure changes are strictly prohibited in this project.**

### ❌ 禁止されている変更 / Prohibited Changes

以下の変更は絶対に行わないでください：
The following changes must never be made:

1. **テーブル構造の変更 / Table Structure Changes**
   - カラムの追加・削除 / Adding or removing columns
   - データ型の変更 / Changing data types
   - インデックスの変更 / Modifying indexes
   - 制約の追加・削除 / Adding or removing constraints

2. **モデル定義の変更 / Model Definition Changes**
   - `models.py` ファイルの変更 / Changes to `models.py` file
   - SQLAlchemy モデルクラスの変更 / Changes to SQLAlchemy model classes
   - リレーションシップの変更 / Relationship modifications

3. **マイグレーションスクリプト / Migration Scripts**
   - Alembic などのマイグレーションツールの使用 / Using migration tools like Alembic
   - データベーススキーマ変更スクリプトの追加 / Adding database schema change scripts

### ✅ 許可されている変更 / Allowed Changes

以下の変更は許可されています：
The following changes are allowed:

1. **ビジネスロジックの追加・修正 / Business Logic Changes**
   - 既存テーブルを使用した新機能の実装 / Implementing new features using existing tables
   - データ処理ロジックの改善 / Improving data processing logic
   - バリデーションの追加 / Adding validation

2. **UI/UX の改善 / UI/UX Improvements**
   - テンプレートファイルの修正 / Modifying template files
   - CSS/JavaScript の変更 / CSS/JavaScript changes
   - レスポンシブデザインの改善 / Responsive design improvements

3. **メール機能の改善 / Email Feature Improvements**
   - メール送信ロジックの修正 / Email sending logic modifications
   - メールテンプレートの変更 / Email template changes
   - 出欠処理の改善 / Attendance processing improvements

### 📊 現在のデータベース構造 / Current Database Structure

現在のデータベース構造は以下の通りです：
The current database structure is as follows:

#### Recipient テーブル
```python
class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    affiliation = db.Column(db.String(100))
    phone = db.Column(db.String(20))
```

#### Seminar テーブル
```python
class Seminar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    date = db.Column(db.DateTime)
    venue = db.Column(db.String(200))
    speaker = db.Column(db.String(100))
    topic = db.Column(db.String(200))
    contact = db.Column(db.String(100))
```

#### Attendance テーブル
```python
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id'))
    seminar_id = db.Column(db.Integer, db.ForeignKey('seminar.id'))
    status = db.Column(db.String(20))
    comment = db.Column(db.String(500))
    recipient = relationship("Recipient", backref="attendances")
```

### 🔄 開発の進め方 / Development Approach

新機能を実装する際は、以下の手順に従ってください：
When implementing new features, follow these steps:

1. **要件分析 / Requirements Analysis**
   - 既存のデータベース構造で実現可能か確認 / Verify if achievable with existing database structure
   - 必要なデータが既存テーブルから取得可能か検討 / Consider if required data can be obtained from existing tables

2. **設計 / Design**
   - 既存テーブルを活用した設計を行う / Design using existing tables
   - データの加工や結合で要件を満たす方法を検討 / Consider data processing or joins to meet requirements

3. **実装 / Implementation**
   - データベース構造を変更せずに実装 / Implement without changing database structure
   - 必要に応じてビューロジックでデータを加工 / Process data in view logic if necessary

### 🔍 プルリクエスト時のチェックポイント / Pull Request Checklist

プルリクエストを作成する前に、以下を確認してください：
Before creating a pull request, verify the following:

- [ ] `models.py` ファイルに変更がないことを確認 / Confirm no changes to `models.py` file
- [ ] 新しいマイグレーションファイルが追加されていないことを確認 / Confirm no new migration files added
- [ ] データベーススキーマに影響する変更がないことを確認 / Confirm no changes affecting database schema
- [ ] 既存のテーブル構造で要件を満たしていることを確認 / Confirm requirements are met with existing table structure

### 📞 質問がある場合 / If You Have Questions

データベース関連の実装で不明な点がある場合は、プルリクエストを作成する前にイシューで相談してください。
If you have questions about database-related implementation, please consult via an issue before creating a pull request.

### 🙏 ご協力のお願い / Request for Cooperation

この制限により、システムの安定性と既存データの整合性を保つことができます。ご理解とご協力をお願いいたします。
These restrictions help maintain system stability and existing data consistency. We appreciate your understanding and cooperation.