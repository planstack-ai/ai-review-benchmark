#!/usr/bin/env python3
"""Generate test cases from patterns.yaml definitions.

Usage:
    python scripts/generator.py --pattern CALC_001
    python scripts/generator.py --category calculation
    python scripts/generator.py --all
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any

CASES_DIR = Path(__file__).parent.parent / "cases" / "rails"

# Category mappings
CATEGORY_PREFIXES = {
    "calculation": "CALC",
    "inventory": "STOCK",
    "state": "STATE",
    "authorization": "AUTH",
    "time": "TIME",
    "notification": "NOTIFY",
    "external": "EXT",
    "performance": "PERF",
    "data": "DATA",
    "rails": "RAILS",
    "false_positive": "FP",
}

SPEC_ALIGNMENT_CATEGORIES = [
    "calculation",
    "inventory",
    "state",
    "authorization",
    "time",
    "notification",
]


def parse_patterns_yaml(content: str) -> list[dict[str, Any]]:
    """Parse patterns.yaml without external YAML library."""
    patterns: list[dict[str, Any]] = []
    current: dict[str, Any] = {}

    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            if current:
                patterns.append(current)
                current = {}
            continue

        if line.startswith("- id:"):
            if current:
                patterns.append(current)
            current = {"id": line.split(":", 1)[1].strip()}
        elif line.startswith("  ") and ":" in line and current:
            key, value = line.strip().split(":", 1)
            value = value.strip()
            if value == "null":
                value = None
            elif value.startswith("[") and value.endswith("]"):
                value = [v.strip().strip('"') for v in value[1:-1].split(",") if v.strip()]
            elif value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            current[key] = value

    if current:
        patterns.append(current)

    return patterns


def generate_plan_md(pattern: dict[str, Any]) -> str:
    """Generate plan.md content from pattern definition."""
    name = pattern.get("name", "unknown").replace("_", " ").title()
    plan = pattern.get("plan", "")
    correct = pattern.get("correct", "")
    category = pattern.get("category", "")

    return f"""# {name}

## 概要

ECサイトの注文処理における機能実装。

## 要件

1. {plan}

## 使用すべき既存実装

- 既存のモデルメソッド・スコープを活用すること
- context.md に記載の実装を参照

## 注意事項

- 正しい実装パターン: `{correct}`
- 仕様通りに実装すること
"""


def generate_context_md(pattern: dict[str, Any]) -> str:
    """Generate context.md content from pattern definition."""
    category = pattern.get("category", "")
    correct = pattern.get("correct", "")

    schemas = {
        "calculation": """# orders table
# - id: bigint
# - user_id: bigint (foreign key)
# - subtotal: decimal(10,2)
# - discount_amount: decimal(10,2)
# - tax_amount: decimal(10,2)
# - total: decimal(10,2)
# - status: integer (enum)
# - created_at: datetime""",
        "inventory": """# products table
# - id: bigint
# - name: string
# - stock: integer
# - reserved_stock: integer
# - price: decimal(10,2)

# order_items table
# - id: bigint
# - order_id: bigint
# - product_id: bigint
# - quantity: integer""",
        "state": """# orders table
# - id: bigint
# - status: integer (enum: pending, confirmed, shipped, delivered, canceled)
# - payment_status: integer (enum: unpaid, paid, refunded)
# - shipped_at: datetime
# - delivered_at: datetime
# - canceled_at: datetime""",
        "authorization": """# users table
# - id: bigint
# - email: string
# - role: integer (enum: user, admin)
# - membership_status: string (active, inactive)

# orders table
# - id: bigint
# - user_id: bigint (foreign key)""",
        "time": """# campaigns table
# - id: bigint
# - name: string
# - starts_at: datetime
# - ends_at: datetime
# - timezone: string

# coupons table
# - id: bigint
# - code: string
# - expires_at: datetime""",
        "notification": """# notifications table
# - id: bigint
# - user_id: bigint
# - notifiable_type: string
# - notifiable_id: bigint
# - sent_at: datetime
# - email_sent: boolean""",
        "external": """# payments table
# - id: bigint
# - order_id: bigint
# - external_id: string
# - amount: decimal(10,2)
# - status: string
# - idempotency_key: string

# webhook_logs table
# - id: bigint
# - event_id: string (unique)
# - processed_at: datetime""",
        "performance": """# orders table (数百万レコード)
# - id: bigint
# - user_id: bigint (indexed)
# - status: integer
# - created_at: datetime (indexed)

# order_items table
# - id: bigint
# - order_id: bigint (indexed)
# - product_id: bigint""",
        "data": """# users table
# - id: bigint
# - email: string (unique index)
# - deleted_at: datetime (soft delete)
# - lock_version: integer (optimistic locking)

# products table
# - id: bigint
# - name: string
# - price: decimal(10,2)""",
        "rails": """# orders table
# - id: bigint
# - user_id: bigint
# - status: integer (enum)
# - total: decimal(10,2)
# - created_at: datetime""",
        "false_positive": """# orders table
# - id: bigint
# - user_id: bigint
# - status: integer (enum)
# - total: decimal(10,2)""",
    }

    models = {
        "calculation": """class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy

  TAX_RATE = 0.10  # 10%

  def apply_discount(rate)
    # rate: 支払い率（0.9 = 10%割引）
    self.total = subtotal * rate
  end

  def calculate_tax
    self.tax_amount = subtotal * TAX_RATE
  end
end""",
        "inventory": """class Product < ApplicationRecord
  has_many :order_items

  scope :in_stock, -> { where('stock > reserved_stock') }

  def available_stock
    stock - reserved_stock
  end

  def reserve!(quantity)
    with_lock do
      raise InsufficientStock if available_stock < quantity
      increment!(:reserved_stock, quantity)
    end
  end
end""",
        "state": """class Order < ApplicationRecord
  enum status: {
    pending: 0,
    confirmed: 1,
    shipped: 2,
    delivered: 3,
    canceled: 4
  }

  CANCELLABLE_STATUSES = %w[pending confirmed].freeze

  def can_cancel?
    CANCELLABLE_STATUSES.include?(status)
  end

  def cancel!
    raise CannotCancel unless can_cancel?
    update!(status: :canceled, canceled_at: Time.current)
  end
end""",
        "authorization": """class User < ApplicationRecord
  has_many :orders

  enum role: { user: 0, admin: 1 }

  def admin?
    role == 'admin'
  end

  def member?
    membership_status == 'active'
  end
end

class ApplicationController < ActionController::Base
  def current_user
    @current_user ||= User.find(session[:user_id])
  end
end""",
        "time": """class Campaign < ApplicationRecord
  scope :active, -> {
    where('starts_at <= ? AND ends_at >= ?', Time.current, Time.current)
  }

  def active?
    starts_at <= Time.current && ends_at >= Time.current
  end
end

class Coupon < ApplicationRecord
  def expired?
    expires_at < Time.current
  end

  def valid_until?(date)
    expires_at >= date.end_of_day
  end
end""",
        "notification": """class OrderMailer < ApplicationMailer
  def confirmation(order)
    @order = order
    @user = order.user
    mail(to: @user.email, subject: '注文確認')
  end
end

class NotificationService
  def self.send_once(user, notifiable)
    return if already_sent?(user, notifiable)
    # send notification
    mark_sent!(user, notifiable)
  end
end""",
        "external": """class PaymentGateway
  class TimeoutError < StandardError; end

  def self.charge(amount, idempotency_key:)
    # External payment API call
    response = HTTPClient.post('/charge', amount: amount, key: idempotency_key)
    response.success? or raise PaymentError
  end
end

class WebhookProcessor
  def self.process(event_id, &block)
    return if WebhookLog.exists?(event_id: event_id)
    yield
    WebhookLog.create!(event_id: event_id, processed_at: Time.current)
  end
end""",
        "performance": """class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items

  scope :recent, -> { where('created_at > ?', 30.days.ago) }
  scope :with_items, -> { includes(:order_items) }
  scope :with_user, -> { includes(:user) }
end

# find_each でバッチ処理すること
# includes で N+1 を防ぐこと""",
        "data": """class User < ApplicationRecord
  default_scope { where(deleted_at: nil) }

  def soft_delete!
    update!(deleted_at: Time.current)
  end
end

class Product < ApplicationRecord
  # 注文時点の商品情報はスナップショットとして保存すること
end""",
        "rails": """class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy

  enum status: { pending: 0, confirmed: 1, shipped: 2 }

  scope :active, -> { where.not(status: :canceled) }
  scope :recent, -> { where('created_at > ?', 7.days.ago) }

  after_commit :notify_user, on: :create

  private

  def notify_user
    OrderMailer.confirmation(self).deliver_later
  end
end""",
        "false_positive": """class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy

  enum status: { pending: 0, confirmed: 1, shipped: 2, delivered: 3 }

  validates :total, numericality: { greater_than_or_equal_to: 0 }

  scope :active, -> { where.not(status: :canceled) }
end""",
    }

    schema = schemas.get(category, schemas["calculation"])
    model = models.get(category, models["calculation"])

    return f"""# 既存コードベース

## スキーマ

```ruby
{schema}
```

## モデル・サービス

```ruby
{model}
```
"""


def generate_impl_rb(pattern: dict[str, Any]) -> str:
    """Generate impl.rb content from pattern definition."""
    name = pattern.get("name", "unknown")
    incorrect = pattern.get("incorrect", "")
    correct = pattern.get("correct", "")
    bug_desc = pattern.get("bug_description", "")
    category = pattern.get("category", "")

    class_name = "".join(word.title() for word in name.split("_")) + "Service"

    if category == "false_positive":
        return f"""# frozen_string_literal: true

class {class_name}
  def initialize(order)
    @order = order
  end

  def execute
    # 正しい実装
    {correct if correct else "process_order"}
  end

  private

  def process_order
    # 実装
  end
end
"""
    else:
        return f"""# frozen_string_literal: true

class {class_name}
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: {bug_desc}
    {incorrect if incorrect else "buggy_implementation"}
  end

  private

  def buggy_implementation
    # 実装
  end
end
"""


def generate_meta_json(pattern: dict[str, Any]) -> dict[str, Any]:
    """Generate meta.json content from pattern definition."""
    category = pattern.get("category", "")
    is_fp = category == "false_positive"

    axis = None
    if not is_fp:
        axis = "spec_alignment" if category in SPEC_ALIGNMENT_CATEGORIES else "implicit_knowledge"

    return {
        "case_id": pattern.get("id", ""),
        "category": category,
        "axis": axis,
        "name": pattern.get("name", ""),
        "difficulty": pattern.get("difficulty", "medium"),
        "expected_detection": not is_fp,
        "bug_description": pattern.get("bug_description") if not is_fp else None,
        "bug_location": "impl.rb:10" if not is_fp else None,
        "bug_anchor": pattern.get("incorrect") if not is_fp else None,
        "correct_implementation": pattern.get("correct"),
        "severity": pattern.get("severity") if not is_fp else None,
        "tags": pattern.get("tags", []),
        "notes": pattern.get("misleading_points", ""),
    }


def generate_case(pattern: dict[str, Any], output_dir: Path) -> Path:
    """Generate a complete test case from a pattern definition."""
    case_id = pattern.get("id", "UNKNOWN")
    case_dir = output_dir / case_id

    case_dir.mkdir(parents=True, exist_ok=True)

    (case_dir / "plan.md").write_text(generate_plan_md(pattern), encoding="utf-8")
    (case_dir / "context.md").write_text(generate_context_md(pattern), encoding="utf-8")
    (case_dir / "impl.rb").write_text(generate_impl_rb(pattern), encoding="utf-8")

    meta = generate_meta_json(pattern)
    with open(case_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return case_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate test cases from patterns.yaml")
    parser.add_argument("--pattern", help="Generate specific pattern (e.g., CALC_001)")
    parser.add_argument("--category", help="Generate all patterns in category")
    parser.add_argument("--all", action="store_true", help="Generate all 95 patterns")
    parser.add_argument(
        "--output",
        default=str(CASES_DIR),
        help="Output directory (default: cases/rails)",
    )
    args = parser.parse_args()

    patterns_file = Path(__file__).parent.parent / "patterns.yaml"
    with open(patterns_file, encoding="utf-8") as f:
        patterns = parse_patterns_yaml(f.read())

    output_dir = Path(args.output)
    generated = 0

    if args.pattern:
        pattern = next((p for p in patterns if p.get("id") == args.pattern), None)
        if pattern:
            case_dir = generate_case(pattern, output_dir)
            print(f"Generated: {case_dir}")
            generated = 1
        else:
            print(f"Pattern not found: {args.pattern}")
    elif args.category:
        category_patterns = [p for p in patterns if p.get("category") == args.category]
        for pattern in category_patterns:
            case_dir = generate_case(pattern, output_dir)
            print(f"Generated: {case_dir}")
            generated += 1
        print(f"\nGenerated {generated} cases for category: {args.category}")
    elif args.all:
        for pattern in patterns:
            case_dir = generate_case(pattern, output_dir)
            print(f"Generated: {case_dir}")
            generated += 1
        print(f"\nGenerated {generated} cases total")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
