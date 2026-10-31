"""Index of a Java test codebase built with tree-sitter: classes, fields, methods, call sites."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import tree_sitter_java as tsj
from tree_sitter import Language, Node, Parser

PARSER = Parser(Language(tsj.language()))

STEP_ANNOTATIONS = {"Given", "When", "Then", "And", "But"}
HOOK_ANNOTATIONS = {"Before", "After", "BeforeStep", "AfterStep", "BeforeAll", "AfterAll"}
BY_FACTORIES = {"xpath", "id", "cssSelector", "name", "className", "linkText", "partialLinkText", "tagName"}
LITERAL_TYPES = {"string_literal": {"String", "CharSequence", "Object"},
                 "decimal_integer_literal": {"int", "Integer", "long", "Long", "double", "Object"},
                 "true": {"boolean", "Boolean"}, "false": {"boolean", "Boolean"}}


def text(node: Node | None) -> str:
    return node.text.decode("utf-8", errors="replace") if node is not None else ""


def unescape(java_string_body: str) -> str:
    return re.sub(r"\\(.)", r"\1", java_string_body)


def string_value(node: Node) -> str:
    return unescape(text(node)[1:-1])


def walk(node: Node):
    yield node
    for child in node.children:
        yield from walk(child)


@dataclass
class Call:
    name: str
    receiver: Node | None
    args: list[Node]
    node: Node
    line: int


@dataclass
class FieldInfo:
    cls: "JavaClass"
    name: str
    type: str
    value: Node | None
    is_static: bool
    line: int

    @property
    def locator(self) -> str | None:
        v = self.value
        if v is not None and v.type == "method_invocation" and text(v.child_by_field_name("object")) == "By":
            how = text(v.child_by_field_name("name"))
            args = v.child_by_field_name("arguments").named_children
            if how in BY_FACTORIES and args and args[0].type == "string_literal":
                return f"{how}: {string_value(args[0])}"
        return None


@dataclass
class Method:
    cls: "JavaClass"
    name: str
    params: list[tuple[str, str]]          # (type, name)
    varargs: bool
    return_type: str
    annotations: list[tuple[str, str | None]]
    body: Node | None
    line: int
    calls: list[Call] = field(default_factory=list)
    local_types: dict[str, str] = field(default_factory=dict)
    identifiers: set[str] = field(default_factory=set)
    statement_count: int = 0
    commented_code: list[str] = field(default_factory=list)

    @property
    def qualname(self) -> str:
        return f"{self.cls.fqcn}#{self.name}/{len(self.params)}@{self.line}"

    @property
    def short(self) -> str:
        return f"{self.cls.name}.{self.name}"

    @property
    def location(self) -> str:
        return f"{self.cls.rel_path}:{self.line}"

    def annotation(self, names: set[str]) -> tuple[str, str | None] | None:
        return next((a for a in self.annotations if a[0] in names), None)


@dataclass
class JavaClass:
    name: str
    package: str
    superclass: str | None
    path: Path
    rel_path: str
    imports: list[str]
    static_imports: list[str]
    fields: dict[str, FieldInfo] = field(default_factory=dict)
    methods: list[Method] = field(default_factory=list)

    @property
    def fqcn(self) -> str:
        return f"{self.package}.{self.name}" if self.package else self.name


def _annotations(modifiers: Node | None) -> list[tuple[str, str | None]]:
    out = []
    if modifiers is None:
        return out
    for child in modifiers.named_children:
        if child.type in ("marker_annotation", "annotation"):
            name = text(child.child_by_field_name("name")).split(".")[-1]
            value = next((string_value(n) for n in walk(child) if n.type == "string_literal"), None)
            out.append((name, value))
    return out


def _is_static(modifiers: Node | None) -> bool:
    return modifiers is not None and any(c.type == "static" for c in modifiers.children)


def _modifiers(node: Node) -> Node | None:
    return next((c for c in node.children if c.type == "modifiers"), None)


def _analyse_body(method: Method) -> None:
    body = method.body
    if body is None:
        return
    method.statement_count = sum(1 for c in body.named_children if not c.type.endswith("comment"))
    for node in walk(body):
        if node.type == "method_invocation":
            method.calls.append(Call(
                name=text(node.child_by_field_name("name")),
                receiver=node.child_by_field_name("object"),
                args=list(node.child_by_field_name("arguments").named_children),
                node=node,
                line=node.start_point[0] + 1,
            ))
        elif node.type == "local_variable_declaration":
            vtype = text(node.child_by_field_name("type"))
            for decl in node.children_by_field_name("declarator"):
                method.local_types[text(decl.child_by_field_name("name"))] = vtype
        elif node.type == "identifier":
            method.identifiers.add(text(node))
        elif node.type in ("line_comment", "block_comment"):
            c = text(node).lstrip("/*").strip()
            if "(" in c and (c.endswith(";") or c.endswith(")")):
                method.commented_code.append(c)


class JavaIndex:
    def __init__(self, root: Path):
        self.root = root
        self.classes: dict[str, JavaClass] = {}            # by fully qualified name
        self.by_simple: dict[str, list[JavaClass]] = {}
        self.methods_by_name: dict[str, list[Method]] = {}
        self.fields_by_name: dict[str, list[FieldInfo]] = {}
        for path in sorted(root.rglob("*.java")):
            if ".git" not in path.parts:
                self._index_file(path)

    # ---- indexing -------------------------------------------------------
    def _index_file(self, path: Path) -> None:
        tree = PARSER.parse(path.read_bytes())
        package, imports, static_imports = "", [], []
        for node in tree.root_node.named_children:
            if node.type == "package_declaration":
                package = text(node).removeprefix("package").removesuffix(";").strip()
            elif node.type == "import_declaration":
                name = text(node).removeprefix("import").removesuffix(";").strip()
                if name.startswith("static "):
                    static_imports.append(name.removeprefix("static ").strip())
                else:
                    imports.append(name)
        for node in walk(tree.root_node):
            if node.type in ("class_declaration", "enum_declaration"):
                self._index_class(node, path, package, imports, static_imports)

    def _index_class(self, node: Node, path: Path, package, imports, static_imports) -> None:
        sup = node.child_by_field_name("superclass")
        sup_name = text(sup.named_children[0]).split("<")[0] if sup is not None and sup.named_children else None
        cls = JavaClass(text(node.child_by_field_name("name")), package, sup_name, path,
                        str(path.relative_to(self.root)), imports, static_imports)
        self.classes[cls.fqcn] = cls
        self.by_simple.setdefault(cls.name, []).append(cls)
        body = node.child_by_field_name("body")
        for member in body.named_children if body is not None else []:
            mods = _modifiers(member)
            if member.type == "field_declaration":
                ftype = text(member.child_by_field_name("type"))
                for decl in member.children_by_field_name("declarator"):
                    f = FieldInfo(cls, text(decl.child_by_field_name("name")), ftype,
                                  decl.child_by_field_name("value"), _is_static(mods), member.start_point[0] + 1)
                    cls.fields[f.name] = f
                    self.fields_by_name.setdefault(f.name, []).append(f)
            elif member.type in ("method_declaration", "constructor_declaration"):
                params, varargs = [], False
                for p in member.child_by_field_name("parameters").named_children:
                    if p.type == "formal_parameter":
                        params.append((text(p.child_by_field_name("type")), text(p.child_by_field_name("name"))))
                    elif p.type == "spread_parameter":
                        varargs = True
                        params.append(("...", text(p.named_children[-1])))
                m = Method(cls, text(member.child_by_field_name("name")), params, varargs,
                           text(member.child_by_field_name("type")) or cls.name, _annotations(mods),
                           member.child_by_field_name("body"), member.start_point[0] + 1)
                _analyse_body(m)
                cls.methods.append(m)
                self.methods_by_name.setdefault(m.name, []).append(m)

    # ---- queries --------------------------------------------------------
    def lookup_class(self, simple: str | None, from_cls: JavaClass) -> JavaClass | None:
        """Resolve a simple type name the way javac would: same package, explicit import, wildcard import."""
        if not simple:
            return None
        simple = simple.split("<")[0].split(".")[-1]
        cands = self.by_simple.get(simple, [])
        if len(cands) <= 1:
            return cands[0] if cands else None
        for c in cands:
            if c.package == from_cls.package or c.fqcn in from_cls.imports \
                    or f"{c.package}.*" in from_cls.imports:
                return c
        return cands[0]

    def ancestors(self, cls: JavaClass | None) -> list[JavaClass]:
        chain = []
        while cls is not None and cls not in chain:
            chain.append(cls)
            cls = self.lookup_class(cls.superclass, cls)
        return chain

    def all_methods(self):
        for cls in self.classes.values():
            yield from cls.methods

    def field_in_chain(self, cls: JavaClass | None, name: str) -> FieldInfo | None:
        return next((c.fields[name] for c in self.ancestors(cls) if name in c.fields), None)

    def type_of(self, node: Node | None, ctx: Method) -> JavaClass | str | None:
        """Best-effort static type of an expression: a project class, a library type name, or None."""
        if node is None:
            return None
        name = None
        if node.type == "identifier":
            ident = text(node)
            if ident in ctx.local_types:
                name = ctx.local_types[ident]
            elif (f := self.field_in_chain(ctx.cls, ident)) is not None:
                name = f.type
            else:
                name = next((t for t, p in ctx.params if p == ident), None) or ident
        elif node.type == "this":
            return ctx.cls
        elif node.type == "method_invocation":
            targets = self.resolve(Call(text(node.child_by_field_name("name")), node.child_by_field_name("object"),
                                        list(node.child_by_field_name("arguments").named_children), node, 0), ctx)
            if len(targets) == 1:
                return self.lookup_class(targets[0].return_type, targets[0].cls) or targets[0].return_type
            return None
        elif node.type == "object_creation_expression":
            name = text(node.child_by_field_name("type"))
        if name is None:
            return None
        return self.lookup_class(name, ctx.cls) or name

    def _arity_ok(self, m: Method, n: int) -> bool:
        return len(m.params) == n or (m.varargs and n >= len(m.params) - 1)

    def _best_overloads(self, cands: list[Method], call: Call) -> list[Method]:
        if len(cands) <= 1:
            return cands

        def score(m: Method) -> int:
            s = 0
            for (ptype, _), arg in zip(m.params, call.args):
                allowed = LITERAL_TYPES.get(arg.type)
                if allowed is not None:
                    s += 1 if ptype in allowed else -5
            return s
        best = max(score(m) for m in cands)
        return [m for m in cands if score(m) == best]

    def resolve(self, call: Call, ctx: Method) -> list[Method]:
        cands = [m for m in self.methods_by_name.get(call.name, []) if self._arity_ok(m, len(call.args))]
        if not cands:
            return []
        if call.receiver is None:
            scope = self.ancestors(ctx.cls)
            scoped = [m for m in cands if m.cls in scope]
            if not scoped:
                owners = set()
                for imp in ctx.cls.static_imports:
                    owner_fqcn, member = imp.rsplit(".", 1)
                    if member in ("*", call.name) and owner_fqcn in self.classes:
                        owners |= set(id(c) for c in self.ancestors(self.classes[owner_fqcn]))
                scoped = [m for m in cands if id(m.cls) in owners]
            return self._best_overloads(scoped, call)
        rtype = self.type_of(call.receiver, ctx)
        if isinstance(rtype, JavaClass):
            scope = self.ancestors(rtype)
            return self._best_overloads([m for m in cands if m.cls in scope], call)
        if isinstance(rtype, str):
            return []   # receiver is a library type (String, WebDriver, Hashtable, ...)
        return self._best_overloads(cands, call)

    def describe_value(self, node: Node, ctx: Method) -> tuple[str, str | None]:
        """Return (source text, resolved meaning) for an argument expression."""
        src = text(node)
        f = None
        if node.type == "identifier":
            f = self.field_in_chain(ctx.cls, src)
        elif node.type == "field_access":
            name = text(node.child_by_field_name("field"))
            owner = self.type_of(node.child_by_field_name("object"), ctx)
            f = self.field_in_chain(owner, name) if isinstance(owner, JavaClass) else None
            if f is None and len(self.fields_by_name.get(name, [])) == 1:
                f = self.fields_by_name[name][0]
        elif node.type == "method_invocation" and text(node.child_by_field_name("object")) == "By":
            args = node.child_by_field_name("arguments").named_children
            if args and args[0].type == "string_literal":
                return src, f"{text(node.child_by_field_name('name'))}: {string_value(args[0])}"
        if f is not None:
            return src, f.locator or (text(f.value) if f.value is not None else None)
        # e.g. driver.findElement(heading).isDisplayed(): name the locators the expression reads
        locators = [fld.locator for n in walk(node) if n.type == "identifier"
                    and (fld := self.field_in_chain(ctx.cls, text(n))) is not None and fld.locator]
        return src, "; ".join(dict.fromkeys(locators)) or None
