"""Trace Gherkin steps through step definitions and page objects, and judge what they verify."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .gherkin import Feature, Scenario, Step
from .java_index import HOOK_ANNOTATIONS, STEP_ANNOTATIONS, Call, JavaIndex, Method, text, unescape, walk

ASSERT_CLASSES = {"Assert", "Assertions", "AssertJUnit", "Assume"}
SOFT_TYPES = {"SoftAssert", "SoftAssertions"}
SOFTENING_ARGS = re.compile(r"CONTINUE_ON_FAILURE|OPTIONAL|SOFT", re.I)
SYNC_NAME = re.compile(r"(wait|sleep|smartWait|pause)", re.I)
MESSAGE_PARAM = re.compile(r"^(message|msg|reason|description|errorMessage)$", re.I)
ACTION_CALLS = {"click", "sendKeys", "submit", "clear", "selectByVisibleText", "selectByValue",
                "selectByIndex", "doubleClick", "contextClick", "moveToElement", "perform"}
SYNONYMS = {"error": {"validation", "alert", "invalid", "warning", "msg"},
            "redirect": {"url", "current"}, "title": {"heading"}, "login": {"sign", "signin"},
            "logged": {"sign", "signin", "login"}, "item": {"product", "count"}}
COMMENTED_STEPDEF =re.compile(r'^\s*//\s*@(Given|When|Then|And|But)\s*\(\s*"(.*)"\s*\)')
VERIFY_WORDS = {"verify", "assert", "check", "expect", "fail"}
ACTION_WORDS = {"navigate", "open", "go", "click", "enter", "type", "select", "submit", "login", "log", "fill"}
STOPWORDS = {"the", "a", "an", "to", "is", "are", "be", "user", "page", "this", "that", "with", "and", "or", "of",
             "on", "in", "for", "can", "will", "should", "i", "it", "its", "has", "have", "my", "me", "not", "no",
             "cannot", "string", "int", "word", "float", "displays", "display", "displayed", "see", "sees"}


# ---- facts gathered by walking the call graph ------------------------------
@dataclass(frozen=True)
class Assertion:
    kind: str          # hard | soft | logged-only | collect
    call: str
    location: str
    via: tuple[str, ...]

    @property
    def is_sync(self) -> bool:
        """Timeouts inside wait/sleep helpers guard synchronisation; they do not verify intent."""
        return any(SYNC_NAME.match(q.split("#")[1]) for q in self.via if "#" in q)


def is_check(a: Assertion) -> bool:
    return a.kind == "hard" and not a.is_sync


@dataclass
class Reach:
    assertions: list[Assertion] = field(default_factory=list)
    actions: set[str] = field(default_factory=set)
    methods: set[str] = field(default_factory=set)


@dataclass
class Finding:
    severity: str      # high | medium | low | info
    code: str
    title: str
    detail: list[str]
    location: str
    scenario: str | None = None
    occurrences: list[str] = field(default_factory=list)   # every scenario the same problem affects


@dataclass
class StepTrace:
    step: Step
    stepdef: Method | None
    candidates: list[Method]
    reach: Reach
    checks: list[str]                 # plain-language description of what is checked
    check_tokens: set[str]
    uses_step_param: bool


def library_message_arity(name: str) -> int:
    """Argument count of an assertion-library call *without* a trailing message (TestNG style)."""
    if name == "fail":
        return 0
    if re.match(r"assert(Not)?(Equals|Same)|assertThat", name):
        return 2
    return 1


def split_words(s: str) -> list[str]:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s)
    return [w for w in re.split(r"[^A-Za-z0-9]+", s.lower()) if w]


def stem(w: str) -> str:
    for suffix in ("ing", "ed", "es", "s"):
        if w.endswith(suffix) and len(w) - len(suffix) >= 4:
            return w[: -len(suffix)]
    return w


def content_tokens(s: str) -> set[str]:
    return {stem(w) for w in split_words(s) if w not in STOPWORDS and len(w) > 2}


def cucumber_regex(expr: str) -> re.Pattern:
    if expr.startswith("^") or expr.endswith("$"):
        return re.compile(expr)
    out, i = "", 0
    for m in re.finditer(r"\{(\w*)\}|\(([^)]*)\)|([^{(]+)", expr):
        if m.group(1) is not None or m.group(0) == "{}":
            out += {"string": r'("[^"]*"|\'[^\']*\')', "int": r"(-?\d+)", "float": r"(-?[\d.]+)",
                    "word": r"(\S+)"}.get(m.group(1), r"(.*)")
        elif m.group(2) is not None:
            out += f"(?:{re.escape(m.group(2))})?"
        else:
            parts = re.split(r"(\S+/\S+)", m.group(3))
            for p in parts:
                out += f"(?:{'|'.join(map(re.escape, p.split('/')))})" if "/" in p and " " not in p else re.escape(p)
    return re.compile(f"^{out}$")


class Analyzer:
    def __init__(self, index: JavaIndex, features: list[Feature]):
        self.index = index
        self.features = features
        self.stepdefs = [m for m in index.all_methods() if m.annotation(STEP_ANNOTATIONS)]
        self.hooks = [m for m in index.all_methods() if m.annotation(HOOK_ANNOTATIONS)]
        self._patterns = [(cucumber_regex(m.annotation(STEP_ANNOTATIONS)[1] or ""), m) for m in self.stepdefs]
        self.commented_stepdefs = [
            (cucumber_regex(unescape(m.group(2))), f"{p.relative_to(index.root)}:{n}")
            for p in sorted(index.root.rglob("*.java")) if ".git" not in p.parts
            for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
            if (m := COMMENTED_STEPDEF.match(line))]
        self._memo: dict[int, Reach] = {}
        self.by_qualname = {m.qualname: m for m in index.all_methods()}
        self.findings: list[Finding] = []
        self.used_stepdefs: set[int] = set()
        self.reached_methods: set[str] = set()

    # ---- call graph ---------------------------------------------------------
    def _direct_assertion(self, call: Call, ctx: Method) -> str | None:
        recv = text(call.receiver) if call.receiver is not None else None
        if recv:
            if recv.split(".")[-1] in ASSERT_CLASSES:
                return "hard"
            rtype = ctx.local_types.get(recv) or getattr(self.index.field_in_chain(ctx.cls, recv), "type", None)
            if rtype in SOFT_TYPES:
                return "collect" if call.name == "assertAll" else "soft"
            if call.name == "assertThat" and recv in ("Assertions", "MatcherAssert"):
                return "hard"
            return None
        if call.name.startswith("assert") or call.name in ("fail", "assertThat"):
            if not self.index.resolve(call, ctx):
                return "hard"   # static import from an assertion library
        return None

    def reach(self, method: Method, _stack: frozenset = frozenset()) -> Reach:
        key = id(method)
        if key in self._memo:
            return self._memo[key]
        if key in _stack:
            return Reach()
        r = Reach(methods={method.qualname})
        for node in walk(method.body) if method.body is not None else []:
            if node.type == "throw_statement" and "AssertionError" in text(node):
                r.assertions.append(Assertion("hard", text(node)[:80], f"{method.location}", (method.qualname,)))
        for call in method.calls:
            kind = self._direct_assertion(call, method)
            if kind:
                r.assertions.append(Assertion(kind, text(call.node)[:120], f"{method.cls.rel_path}:{call.line}",
                                              (method.qualname,)))
                continue
            # driver.get(url) / navigate().to(url) navigate; ThreadLocal driver.get() does not.
            if call.name in ACTION_CALLS or (call.name in ("get", "to") and len(call.args) == 1
                                             and call.receiver is not None
                                             and re.search(r"driver|navigate", text(call.receiver), re.I)):
                r.actions.add(call.name)
            softened = any(SOFTENING_ARGS.search(text(a)) for a in call.args)
            for target in self.index.resolve(call, method):
                sub = self.reach(target, _stack | {key})
                r.methods |= sub.methods
                r.actions |= sub.actions
                for a in sub.assertions:
                    k = a.kind
                    if softened and k == "hard":
                        k = "logged-only" if "OPTIONAL" in "".join(text(x) for x in call.args) else "soft"
                    r.assertions.append(Assertion(k, a.call, a.location, (method.qualname,) + a.via))
        self._memo[key] = r
        return r

    def _reaches_assertion(self, call: Call, ctx: Method) -> bool:
        if SYNC_NAME.match(call.name):
            return False
        if self._direct_assertion(call, ctx) in ("hard", "soft"):
            return True
        return any(a.kind in ("hard", "soft") and not a.is_sync
                   for t in self.index.resolve(call, ctx) for a in self.reach(t).assertions)

    def describe_checks(self, method: Method, depth: int = 0) -> tuple[list[str], set[str], bool]:
        """Describe, in plain terms, the calls in `method` that lead to an assertion."""
        lines, tokens, uses_param = [], set(), False
        params = {p for _, p in method.params}
        for call in method.calls:
            if not self._reaches_assertion(call, method):
                continue
            targets = self.index.resolve(call, method)
            if not call.args and targets and depth < 3:
                sub_lines, sub_tokens, sub_param = self.describe_checks(targets[0], depth + 1)
                lines += [f"{call.name}() → {s}" for s in sub_lines]
                tokens |= sub_tokens
                continue
            target_params = [p for _, p in targets[0].params] if targets else []
            parts = []
            for i, arg in enumerate(call.args):
                pname = target_params[i] if i < len(target_params) else ""
                src, meaning = self.index.describe_value(arg, method)
                if MESSAGE_PARAM.match(pname) or (not targets and i == len(call.args) - 1
                                                  and arg.type == "string_literal"
                                                  and len(call.args) > library_message_arity(call.name)):
                    continue    # failure messages say what the author meant, not what is checked
                if arg.type == "identifier" and src in params:
                    uses_param = True
                    parts.append(f"the step's `{src}` value")
                    continue
                parts.append(f"`{src}`" + (f" ({meaning})" if meaning else ""))
                tokens |= content_tokens(src) | content_tokens(meaning or "")
            tokens |= content_tokens(call.name)
            if not parts and call.name == "fail":
                continue    # a bare fail("message") checks nothing by itself
            lines.append(f"{' '.join(split_words(call.name))}: " + (", ".join(parts) or "(no arguments)"))
        return lines, tokens, uses_param

    # ---- step matching -------------------------------------------------------
    def match(self, step: Step, scenario: Scenario) -> list[Method]:
        candidates = [step.text]
        if scenario.examples:
            row = scenario.examples[0]
            candidates.append(re.sub(r"<([^>]+)>", lambda m: row.get(m.group(1), m.group(0)), step.text))
        return [m for pat, m in self._patterns if any(pat.match(t) for t in candidates)]

    def trace(self, step: Step, scenario: Scenario) -> StepTrace:
        matches = self.match(step, scenario)
        stepdef = matches[0] if len(matches) == 1 else None
        if stepdef is None:
            return StepTrace(step, None, matches, Reach(), [], set(), False)
        self.used_stepdefs.add(id(stepdef))
        r = self.reach(stepdef)
        self.reached_methods |= r.methods
        checks, tokens, uses_param = self.describe_checks(stepdef)
        return StepTrace(step, stepdef, matches, r, checks, tokens, uses_param)

    # ---- judgement -----------------------------------------------------------
    def run(self) -> list[Finding]:
        seen_steps: set[tuple] = set()
        for feature in self.features:
            for scenario in feature.scenarios:
                traces = [self.trace(s, scenario) for s in feature.background + scenario.steps]
                self._judge_scenario(feature, scenario, traces, seen_steps)
        for hook in self.hooks:
            self.reached_methods |= self.reach(hook).methods
        self._suite_checks()
        self._runner_checks()
        order ={"high": 0, "medium": 1, "low": 2, "info": 3}
        self.findings.sort(key=lambda f: order[f.severity])
        return self.findings

    def _add(self, *args, **kw):
        new = Finding(*args, **kw)
        rank = {"high": 0, "medium": 1, "low": 2, "info": 3}
        for f in self.findings:
            # Same problem in the same step definition, or the same step text, is one finding.
            same_code_site = f.code == new.code and f.location == new.location and ".java:" in f.location
            if same_code_site or (f.code, f.title) == (new.code, new.title):
                if new.scenario and new.scenario not in f.occurrences:
                    f.occurrences.append(new.scenario)
                if rank[new.severity] < rank[f.severity]:
                    f.severity = new.severity
                return
        if new.scenario:
            new.occurrences.append(new.scenario)
        self.findings.append(new)

    def _judge_scenario(self, feature: Feature, scenario: Scenario, traces: list[StepTrace], seen: set) -> None:
        sc_name = f"{feature.name} › {scenario.name}"

        def hard(t: StepTrace) -> list[Assertion]:
            return [a for a in t.reach.assertions if is_check(a)]

        if traces and all(t.stepdef for t in traces) and not any(hard(t) for t in traces):
            thens = [t.step.text for t in traces if t.step.effective == "Then"]
            self._add("high", "SCENARIO_VERIFIES_NOTHING", f'Scenario "{scenario.name}" verifies nothing', [
                f"None of its {len(traces)} steps contains a check that can fail. It passes as long as "
                "nothing crashes.",
                (f"It still reads as if it verifies {len(thens)} outcome(s): "
                 + "; ".join(f'"{x}"' for x in thens[:5]) + ("; …" if len(thens) > 5 else ""))
                if thens else "It has no `Then` steps at all."], f"{scenario.file.name}:{scenario.line}", sc_name)

        for t in traces:
            s, m = t.step, t.stepdef
            loc = f"{s.file.name}:{s.line}"
            if m is None:
                if not t.candidates:
                    disabled = next((where for pat, where in self.commented_stepdefs
                                     if pat.match(s.text)), None)
                    if disabled:
                        self._add("high", "UNDEFINED_STEP", f'"{s.text}" has no working step definition',
                                  [f"Its step definition exists but is commented out at `{disabled}`.",
                                   "Cucumber reports the step as undefined; with `strict = false` (the default "
                                   "before Cucumber 7) the scenario does not fail."], disabled, sc_name)
                    else:
                        self._add("high", "UNDEFINED_STEP", f'"{s.text}" has no step definition',
                                  ["Cucumber reports this step as undefined."], loc, sc_name)
                else:
                    self._add("medium", "AMBIGUOUS_STEP", f'"{s.text}" matches several step definitions',
                              [c.location for c in t.candidates], loc, sc_name)
                continue
            key = (s.text, m.location)
            first_time = key not in seen
            seen.add(key)

            # Step-level problems are reported once per distinct step.
            cols = re.findall(r"<([^>]+)>", s.text) if scenario.examples else []
            ignored_data = (f"The Examples column(s) {', '.join(f'`{c}`' for c in cols)} feed this step, but "
                            "nothing uses them. Changing the test data has no effect.") if cols else None
            if first_time and m.statement_count == 0:
                if m.commented_code:
                    self._add("medium", "DISABLED_STEP", f'"{s.text}" is switched off: its code is commented out',
                              [f"It does nothing when it runs. Commented-out code: `{m.commented_code[0]}`"]
                              + ([ignored_data] if ignored_data and m.params else []), m.location, sc_name)
                else:
                    self._add("low", "EMPTY_STEP", f'"{s.text}" does nothing',
                              ["The step definition is empty, so the scenario reads as if this happens "
                               "as a separate step, but nothing runs."]
                              + ([ignored_data] if ignored_data and m.params else []), m.location, sc_name)
            if first_time and m.statement_count:
                unused = [p for _, p in m.params if p not in m.identifiers]
                if unused:
                    self._add("medium", "IGNORED_PARAM",
                              f'"{s.text}" ignores the value it is given', [
                                  f"Parameter(s) {', '.join(f'`{p}`' for p in unused)} are never used, so changing "
                                  "this value in the feature file has no effect."]
                              + ([ignored_data] if ignored_data else []), m.location, sc_name)

            words = {w for w in split_words(s.text)}
            if (first_time and s.effective in ("Given", "When") and m.statement_count
                    and words & ACTION_WORDS and not t.reach.actions and hard(t)):
                self._add("low", "CHECK_ONLY_ACTION_STEP", f'"{s.text}" only checks, it does not act',
                          ["The wording describes an action, but the code performs no clicks, typing or "
                           "navigation. It only verifies: " + "; ".join(t.checks or ["(see code)"])],
                          m.location, sc_name)

            unconditional_fail = next((c for c in m.calls if c.name == "fail"
                                       and c.node.parent.type == "expression_statement"
                                       and c.node.parent.parent == m.body
                                       and self._direct_assertion(c, m) == "hard"), None)
            if first_time and unconditional_fail is not None:
                self._add("medium", "ALWAYS_FAILS", f'"{s.text}" always fails', [
                    f"`{text(unconditional_fail.node)}` runs every time (line {unconditional_fail.line}), so this "
                    "step can never pass and nothing after it runs.",
                    "A permanently red test teaches the team to ignore failures."], m.location, sc_name)

            if s.effective != "Then":
                continue
            elsewhere = [(o, c) for o in traces if o is not t and o.step.effective != "Then" and hard(o)
                         for c in o.checks if VERIFY_WORDS & set(split_words(c))]
            if not hard(t) and t.reach.actions:
                self._add("medium", "MISLABELLED_THEN",
                          f'"{s.text}" is written as a check but is an action', [
                              f"It performs actions ({', '.join(sorted(t.reach.actions))}) and nothing in it can "
                              "fail the test, but `Then` tells readers it verifies an outcome."],
                          m.location, sc_name)
                continue
            if not hard(t):
                soft = [a for a in t.reach.assertions if a.kind in ("soft", "logged-only")]
                detail = ["Nothing this step runs can make the test fail."]
                if soft:
                    detail.append(f"It only has {len(soft)} soft or logged-only check(s), which do not fail it here.")
                if elsewhere:
                    detail.append("The scenario is only protected by checks hidden in other steps: "
                                  + "; ".join(f'"{o.step.text}" → {c}' for o, c in elsewhere))
                self._add("medium" if elsewhere else "high", "HOLLOW_THEN",
                          f'"{s.text}" claims to verify something but checks nothing', detail, m.location, sc_name)
                continue
            intent = content_tokens(re.sub(r"\{\w*\}|<[^>]+>|\"[^\"]*\"", " ", s.text))
            # Word overlap is a stand-in for a semantic judgement (the MCP agent's LLM should make it).
            expanded = set().union(*({w} | SYNONYMS.get(w, set()) for w in intent)) if intent else set()
            if intent and not t.uses_step_param and not expanded & t.check_tokens:
                detail = ["What it actually checks: " + "; ".join(t.checks),
                          "None of that refers to: " + ", ".join(sorted(intent)) + "."]
                if elsewhere:
                    detail.append("The scenario's real check is hidden in another step: "
                                  + "; ".join(f'"{o.step.text}" → {c}' for o, c in elsewhere))
                else:
                    detail.append("It may be a reasonable stand-in check, but a reviewer should confirm it.")
                # Misleading wording plus a hidden real check is worse than a mere proxy check.
                self._add("medium" if elsewhere else "low", "INTENT_MISMATCH",
                          f'"{s.text}" checks something different from what it says', detail, m.location, sc_name)

    def _runner_checks(self) -> None:
        """Which feature files do the JUnit/TestNG Cucumber runners actually run, and how?"""
        root = self.index.root
        all_features = {f.file.resolve() for f in self.features}
        covered: set = set()
        runners = 0
        for cls in self.index.classes.values():
            src = cls.path.read_text(encoding="utf-8", errors="replace")
            m = re.search(rf"@CucumberOptions\s*\((.*?)\)\s*(?:public\s+)?(?:abstract\s+)?class\s+{cls.name}\b",
                          src, re.S)
            if not m:
                continue
            runners += 1
            opts = re.sub(r"//[^\n]*", "", m.group(1))
            where = f"{cls.rel_path}"
            fm = re.search(r"features\s*=\s*(\{[^}]*\}|\"[^\"]*\")", opts)
            paths = re.findall(r'"([^"]*)"', fm.group(1)) if fm else []
            for p in paths:
                p = p.removeprefix("classpath:")
                if Path(p).is_absolute():
                    self._add("high", "RUNNER_ABSOLUTE_PATH", f"Runner `{cls.name}` points to an absolute path",
                              [f"`features = \"{p}\"` exists only on the original author's machine. "
                               "Anywhere else (CI, a colleague's laptop) this runner finds no features."], where)
                    continue
                target = next((c for c in (root / p, root / "src/test/resources" / p) if c.exists()), None)
                if target is None:
                    self._add("high", "RUNNER_MISSING_PATH", f"Runner `{cls.name}` points to a path that "
                              "does not exist", [f"`features = \"{p}\"` is not in the repository."], where)
                    continue
                covered |= ({target.resolve()} if target.is_file() else
                            {f for f in all_features if target.resolve() in f.parents})
            if re.search(r"dryRun\s*=\s*true", opts):
                self._add("high", "RUNNER_DRY_RUN", f"Runner `{cls.name}` has `dryRun = true`",
                          ["Cucumber only checks that steps have definitions; no step is executed, so every "
                           "scenario it reports as passed was never run."], where)
            if re.search(r"strict\s*=\s*false", opts):
                self._add("medium", "RUNNER_NOT_STRICT", f"Runner `{cls.name}` has `strict = false`",
                          ["Undefined and pending steps do not fail the run, so unimplemented scenarios "
                           "can report as passed."], where)
        never = sorted(all_features - covered)
        if runners and never:
            self._add("high" if not covered else "medium", "FEATURES_NEVER_RUN",
                      f"{len(never)} of {len(all_features)} feature files are not run by any runner",
                      ["No `@CucumberOptions` runner includes them, so their scenarios never execute "
                       "(unless they are run some other way, e.g. a JUnit Platform suite or the IDE):"]
                      + [f"`{p.relative_to(root.resolve())}`" for p in never[:10]]
                      + ([f"…and {len(never) - 10} more"] if len(never) > 10 else []), "runners")

    def _suite_checks(self) -> None:
        idx = self.index
        # Unused step definitions.
        for m in self.stepdefs:
            if id(m) not in self.used_stepdefs:
                self._add("low", "UNUSED_STEP_DEFINITION", f'Step definition "{m.annotation(STEP_ANNOTATIONS)[1]}" '
                          "is never used by any feature", ["Dead code: no scenario runs it."], m.location)

        # Page objects that no scenario reaches.
        reached = [self.by_qualname[q] for q in self.reached_methods]
        reached_classes = {m.cls.fqcn for m in reached}
        referenced_fields = set().union(*(m.identifiers for m in reached)) if reached else set()
        for cls in idx.classes.values():
            locators = [f for f in cls.fields.values() if f.locator]
            if not locators or cls.fqcn in reached_classes:
                continue
            if any(f.name in referenced_fields and len(idx.fields_by_name[f.name]) == 1 for f in locators):
                continue
            verifies = [m.name for m in cls.methods if any(is_check(a) for a in self.reach(m).assertions)]
            self._add("medium", "ORPHAN_PAGE_OBJECT", f"Page object `{cls.name}` is never used by any scenario", [
                f"It defines {len(locators)} locator(s) and {len(cls.methods)} method(s)"
                + (f", including checks such as {', '.join(f'`{v}`' for v in verifies[:3])}" if verifies else "")
                + ". None of it runs, so this area of the app looks covered but isn't."], cls.rel_path)

        # Soft assertions: shared state and late collection.
        for cls in idx.classes.values():
            for f in cls.fields.values():
                if f.type not in SOFT_TYPES:
                    continue
                reassigned = any(re.search(rf"\b{f.name}\s*=\s*new\b", text(m.body)) for m in idx.all_methods()
                                 if m.body is not None)
                users = [m for m in idx.all_methods() for a in self.reach(m).assertions
                         if a.kind == "soft" and a.via[-1] in {x.qualname for x in cls.methods}]
                live = [m for m in users if m.qualname in self.reached_methods and m.cls is not cls]
                problems = []
                if f.is_static and not reassigned:
                    problems.append(f"`{cls.name}.{f.name}` is one static object shared by every scenario and "
                                    "never reset, so one soft failure would also fail every scenario after it "
                                    "(and mixes results across parallel threads).")
                for hook in self.hooks:
                    if hook.annotation({"After"}) is None or hook.body is None:
                        continue
                    collect = next((c for c in hook.calls if any(a.kind == "collect" for t in idx.resolve(c, hook)
                                                                 for a in self.reach(t).assertions)), None)
                    status = next((c for c in hook.calls if c.name in ("getStatus", "isFailed")), None)
                    if collect and status and status.line < collect.line:
                        problems.append(f"Soft failures are collected in `{hook.short}` (line {collect.line}) "
                                        f"after the scenario's status is read (line {status.line}), so reports "
                                        "built from that status count soft-failed scenarios as passed.")
                if problems:
                    callers = sorted({m.cls.name for m in users if m.cls is not cls})
                    state = ("Used by scenarios today." if live else
                             f"Latent: only used by {', '.join(f'`{c}`' for c in callers) or 'no code'}, "
                             "which no scenario runs yet.")
                    self._add("medium" if live else "low", "SOFT_ASSERT_RISK",
                              "Soft assertions can hide failures", problems + [state], f"{cls.rel_path}:{f.line}")

        # The same failure message used for different checks.
        by_msg: dict[str, set[str]] = {}
        for m in idx.all_methods():
            for call in m.calls:
                if self._direct_assertion(call, m) == "hard" and len(call.args) >= 2:
                    last = call.args[-1]
                    if last.type == "string_literal":
                        subject = text(call.args[0])
                        by_msg.setdefault(text(last), set()).add(f"{m.cls.rel_path}:{call.line} checks `{subject}`")
        for msg, uses in by_msg.items():
            subjects = {u.split(" checks ")[1] for u in uses}
            if len(subjects) > 1:
                self._add("low", "REUSED_FAILURE_MESSAGE", f"The failure message {msg} is used for different checks",
                          ["When one of them fails, the report points at the wrong problem:"] + sorted(uses),
                          sorted(uses)[0].split(" ")[0])
