#!/usr/bin/env python3
"""Vá file HTML để chạy được trên Safari/WKWebView của iOS 12 (iPhone 6).
Dùng: python3 make_ios12.py www-modern/index.html www-ios12/index.html
"""
import re, sys

FLEX = {"flex", "inline-flex", "-webkit-flex", "-webkit-inline-flex"}
# rule chỉ có gap, display khai báo ở rule khác (đã kiểm tra thủ công trong file gốc)
UNKNOWN_FLEX = {".step": "column", "#s1": "column", "#tipsBar .lights": "row", ".tip.hasvis": "reset-left"}
log = {"inset": 0, "dvh": 0, "clamp": 0, "gap": 0, "focus": 0, "prefix": 0, "inline": 0, "gap_left": []}


def skip_str(s, i):
    q = s[i]; i += 1
    while i < len(s) and s[i] != q:
        i += 2 if s[i] == "\\" else 1
    return i + 1


def split_top(s, sep):
    out, depth, cur, i = [], 0, [], 0
    while i < len(s):
        c = s[i]
        if c in "\"'":
            j = skip_str(s, i); cur.append(s[i:j]); i = j; continue
        if c in "([": depth += 1
        elif c in ")]": depth -= 1
        if c == sep and depth == 0:
            out.append("".join(cur)); cur = []
        else:
            cur.append(c)
        i += 1
    out.append("".join(cur))
    return out


def find_end(css, i):
    """css[i] == '{'  -> index of the matching '}'"""
    depth = 0
    while i < len(css):
        c = css[i]
        if c in "\"'": i = skip_str(css, i); continue
        if css.startswith("/*", i): i = css.index("*/", i) + 2; continue
        if c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0: return i
        i += 1
    raise ValueError("unbalanced braces")


def parse(css):
    items, i, n = [], 0, len(css)
    while i < n:
        if css[i].isspace(): i += 1; continue
        if css.startswith("/*", i):
            j = css.index("*/", i) + 2; items.append(("raw", css[i:j])); i = j; continue
        j, par = i, 0
        while j < n:
            c = css[j]
            if c in "\"'": j = skip_str(css, j); continue
            if c == "(": par += 1
            elif c == ")": par -= 1
            elif par == 0 and c in "{;": break
            j += 1
        if j >= n or css[j] == ";":
            items.append(("raw", css[i:j + 1])); i = j + 1; continue
        e = find_end(css, j)
        items.append(("block", css[i:j].strip(), css[j + 1:e])); i = e + 1
    return items


def decl_split(body):
    return [d.strip() for d in split_top(body, ";") if d.strip()]


def prop_val(d):
    p, _, v = d.partition(":")
    return p.strip().lower(), v.strip()


def fix_decls(decls):
    out = []
    for d in decls:
        p, v = prop_val(d)
        # inset (Safari 14.1)
        if p == "inset" and len(v.split()) == 1:
            out += [f"top:{v}", f"right:{v}", f"bottom:{v}", f"left:{v}"]; log["inset"] += 1; continue
        if p == "margin-inline" and len(v.split()) == 1:
            out += [f"margin-left:{v}", f"margin-right:{v}"]; log["inline"] += 1; continue
        # clamp (Safari 13.1)
        if "clamp(" in v:
            nv = re.sub(r"clamp\(([^,()]+),([^,()]+),([^,()]+)\)", r"min(\3,max(\1,\2))", v)
            if nv != v: log["clamp"] += 1; d = f"{p}:{nv}"; v = nv
        # dvh (Safari 15.4): thêm bản vh dự phòng đứng trước
        if "dvh" in v:
            out.append(f"{p}:{v.replace('dvh', 'vh')}"); log["dvh"] += 1
        out.append(d)
    # tiền tố -webkit- còn thiếu
    props = {prop_val(d)[0] for d in out}
    extra = []
    for d in out:
        p, v = prop_val(d)
        if p in ("backdrop-filter", "user-select", "mask", "mask-image", "mask-size",
                 "mask-repeat", "mask-position") and f"-webkit-{p}" not in props:
            extra.append(f"-webkit-{p}:{v}"); log["prefix"] += 1; props.add(f"-webkit-{p}")
    return extra + out


def emit_rule(sel, body, extras):
    sels = [s.strip() for s in split_top(sel, ",")]
    keep = [s for s in sels if ":focus-visible" not in s]
    if len(keep) != len(sels): log["focus"] += len(sels) - len(keep)
    if not keep: return ""
    decls = fix_decls(decl_split(body))
    props = {prop_val(d)[0]: prop_val(d)[1] for d in decls}
    display = props.get("display", "").lower()
    new = []
    for d in decls:
        p, v = prop_val(d)
        if p == "gap":
            if display in FLEX:
                parts = v.split(); col = parts[-1]
                direction = props.get("flex-direction", "row").lower()
                if direction.startswith("column"):
                    side = "margin-top"; val = parts[0]
                elif direction == "row-reverse":
                    side = "margin-right"; val = col
                else:
                    side = "margin-left"; val = col
                for s in keep:
                    if not re.search(r"::?[\w-]+$", s):
                        extras.append(f"{s}>*+*{{{side}:{val}}}")
                log["gap"] += 1; continue
            elif keep[0] in UNKNOWN_FLEX:
                kind = UNKNOWN_FLEX[keep[0]]
                side = {"column": "margin-top", "row": "margin-left", "reset-left": "margin-left"}[kind]
                val = "0" if kind == "reset-left" else v.split()[-1]
                for s_ in keep: extras.append(f"{s_}>*+*{{{side}:{val}}}")
                log["gap"] += 1; continue
            else:
                log["gap_left"].append((keep[0][:60], v, display or "(không rõ display)"))
        new.append(d)
    return f"{','.join(keep)}{{{';'.join(new)}}}"


def process(css):
    out = []
    for it in parse(css):
        if it[0] == "raw": out.append(it[1]); continue
        _, pre, body = it
        low = pre.lower()
        if low.startswith(("@media", "@supports")):
            out.append(f"{pre}{{{process(body)}}}")
        elif low.startswith("@"):
            out.append(f"{pre}{{{body}}}")
        else:
            extras = []
            r = emit_rule(pre, body, extras)
            if r: out.append(r)
            out += extras
    return "\n".join(out)


def patch_js(js):
    js = re.sub(r"([A-Za-z_]\w*)\.addEventListener&&\1\.addEventListener\(\"change\",(\(\)=>[A-Za-z_]\w*\(\))\);",
                r'(\1.addEventListener?\1.addEventListener("change",\2):\1.addListener&&\1.addListener(\2));', js)
    return js


src, dst = sys.argv[1], sys.argv[2]
html = open(src, encoding="utf-8").read()
html = re.sub(r"(<style[^>]*>)(.*?)(</style>)", lambda m: m.group(1) + process(m.group(2)) + m.group(3), html, flags=re.S)
html = re.sub(r"(<script(?![^>]*\bsrc=)[^>]*>)(.*?)(</script>)", lambda m: m.group(1) + patch_js(m.group(2)) + m.group(3), html, flags=re.S)
open(dst, "w", encoding="utf-8").write(html)
print({k: v for k, v in log.items() if k != "gap_left"})
print("gap còn lại (không phải flex/không rõ):", len(log["gap_left"]))
for g in log["gap_left"]: print("  ", g)
