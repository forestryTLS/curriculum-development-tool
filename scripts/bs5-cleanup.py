"""One-shot Bootstrap 4 -> 5 cleanup for blade templates.

Run from repo root:
    python scripts/bs5-cleanup.py

Transforms applied to every .blade.php under laravel/resources/views/:
  1. class="close" or class='close' (and combos like "close delete-element")
     -> class="btn-close"
  2. Inside <button class="btn-close" ...>...</button> buttons, strip the
     legacy inner content (<span aria-hidden="true">&times;</span> or a bare
     &times; / x character). BS5 .btn-close uses a CSS background image.
  3. .form-group -> .mb-3
  4. .form-row -> .row g-3
  5. .float-left/.float-right -> .float-start/.float-end
  6. .text-left/.text-right -> .text-start/.text-end
  7. .ml-/.mr-/.pl-/.pr-{n} -> .ms-/.me-/.ps-/.pe-{n}
  8. .badge-{color} -> .badge bg-{color}
  9. .custom-control / .custom-checkbox / .custom-switch / .custom-radio
     -> .form-check / .form-switch (best-effort token swap)

Idempotent: re-running produces no further changes.
"""

import re
from pathlib import Path

VIEWS = Path("laravel/resources/views")

# class="close" -> class="btn-close" (handles single/double quotes and extra tokens)
CLOSE_CLASS = re.compile(r'class=(["\'])close\b')

# Inner span/times in btn-close buttons (multi-line)
INNER_TIMES = re.compile(
    r'(<button\b[^>]*\bclass=(["\'])[^"\']*\bbtn-close\b[^"\']*\2[^>]*>)'
    r'\s*(?:<span\s+aria-hidden=(["\'])true\3>\s*(?:&times;|×|x)\s*</span>\s*'
    r'|&times;|×)?\s*'
    r'(</button>)',
    re.IGNORECASE | re.DOTALL,
)

# Bootstrap 5 BS-color contextual badge migration: .badge-primary -> .badge bg-primary
BADGE_COLORS = ("primary", "secondary", "success", "danger", "warning", "info",
                "light", "dark")
BADGE_RE = re.compile(
    r'\bbadge-(' + "|".join(BADGE_COLORS) + r')\b'
)

# Custom form controls -> form-check/form-switch
CUSTOM_FORM = [
    (re.compile(r'\bcustom-switch\b'), 'form-switch'),
    (re.compile(r'\bcustom-control-input\b'), 'form-check-input'),
    (re.compile(r'\bcustom-control-label\b'), 'form-check-label'),
    (re.compile(r'\bcustom-checkbox\b'), 'form-check'),
    (re.compile(r'\bcustom-radio\b'), 'form-check'),
    (re.compile(r'\bcustom-control\b'), 'form-check'),
]

# Spacing utilities (with optional responsive breakpoint)
SPACING_RE = re.compile(r'\b(m|p)(l|r)(?:-(sm|md|lg|xl|xxl))?-(n?\d+|auto)\b')
SPACING_MAP = {'l': 's', 'r': 'e'}

# Responsive float/text directionality
RESPONSIVE_LR = re.compile(
    r'\b(float|text)-(sm|md|lg|xl|xxl)-(left|right)\b'
)
LR_MAP = {'left': 'start', 'right': 'end'}

# Simple class renames (one-to-one, no responsive variant)
SIMPLE_RENAMES = [
    (re.compile(r'\bform-group\b'), 'mb-3'),
    (re.compile(r'\bform-row\b'), 'row g-3'),
    (re.compile(r'\bfloat-left\b'), 'float-start'),
    (re.compile(r'\bfloat-right\b'), 'float-end'),
    (re.compile(r'\btext-left\b'), 'text-start'),
    (re.compile(r'\btext-right\b'), 'text-end'),
]


def transform(src: str) -> str:
    # 1. class="close" -> class="btn-close"
    src = CLOSE_CLASS.sub(r'class=\1btn-close', src)
    # 2. Empty out btn-close button bodies
    src = INNER_TIMES.sub(r'\1\4', src)
    # 3-7. Simple renames
    for pattern, replacement in SIMPLE_RENAMES:
        src = pattern.sub(replacement, src)
    # 7. Spacing utilities (with optional responsive breakpoint)
    src = SPACING_RE.sub(
        lambda m: (
            f"{m.group(1)}{SPACING_MAP[m.group(2)]}"
            + (f"-{m.group(3)}" if m.group(3) else "")
            + f"-{m.group(4)}"
        ),
        src,
    )
    # 7b. Responsive float/text directionality
    src = RESPONSIVE_LR.sub(
        lambda m: f"{m.group(1)}-{m.group(2)}-{LR_MAP[m.group(3)]}",
        src,
    )
    # 8. Badge colors
    src = BADGE_RE.sub(r'badge bg-\1', src)
    # 9. Custom form controls
    for pattern, replacement in CUSTOM_FORM:
        src = pattern.sub(replacement, src)
    return src


def main():
    changed = 0
    total = 0
    for path in VIEWS.rglob("*.blade.php"):
        total += 1
        original = path.read_text(encoding="utf-8")
        updated = transform(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"updated: {path.as_posix()}")
    print(f"\nScanned {total} files, modified {changed}.")


if __name__ == "__main__":
    main()
