"""Run cringe-filter's own rewrite pipeline with a local llama-server model.

Usage: python bench.py <label> <draft names...>
Expects llama-server on localhost:8080. Writes results/<label>.jsonl and
out/<label>/<draft>.md.
"""
import json, os, re, sys, time, urllib.request

from cringe_filter.rewrite import rewrite
from cringe_filter.lint import lint_text
from cringe_filter.score import score_text

URL = "http://127.0.0.1:8080/v1/chat/completions"
STOP = set("""a an the and or but if then so of to in on at by for with from as is are was were be been
being it its this that these those there here i we you he she they me us our your their my his her them
not no do does did done have has had can could should would will may might must shall just also than
too very into out up down over under about after before again all any each few more most other some such
only own same both what which who whom when where why how""".split())


def content_words(t):
    return {w for w in re.findall(r"[a-z][a-z'-]{2,}", t.lower()) if w not in STOP}


class Block:
    type = "text"

    def __init__(self, t):
        self.text = t


class Msg:
    stop_reason = "end_turn"

    def __init__(self, t):
        self.content = [Block(t)]


class Stream:
    def __init__(self, t):
        self.t = t

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get_final_message(self):
        return Msg(self.t)


class Messages:
    def __init__(self, extra, cap):
        self.calls = []
        self.extra = extra
        self.cap = cap

    def stream(self, **kw):
        msgs = [{"role": "system", "content": kw["system"]}] + kw["messages"]
        body = {"messages": msgs, "temperature": 0.7, "top_p": 0.9, "seed": 1,
                "max_tokens": self.cap, **self.extra}
        req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=1800) as r:
            out = json.loads(r.read())
        msg = out["choices"][0]["message"]
        text = msg.get("content") or ""
        text = re.sub(r"(?s)<think>.*?</think>", "", text).strip()
        tm = out.get("timings", {})
        self.calls.append({"secs": round(time.time() - t0, 1),
                           "prompt_n": tm.get("prompt_n"),
                           "prompt_tps": round(tm.get("prompt_per_second") or 0, 1),
                           "gen_n": tm.get("predicted_n"),
                           "gen_tps": round(tm.get("predicted_per_second") or 0, 1),
                           "reasoning_chars": len(msg.get("reasoning_content") or ""),
                           "finish": out["choices"][0].get("finish_reason")})
        return Stream(text)


class Client:
    def __init__(self, extra, cap):
        self.messages = Messages(extra, cap)


def sev(findings):
    c = {"error": 0, "warn": 0, "info": 0}
    for f in findings:
        c[f["severity"]] = c.get(f["severity"], 0) + 1
    return c


def main():
    label, drafts = sys.argv[1], sys.argv[2:]
    extra = json.loads(os.environ.get("EXTRA", "{}"))
    os.makedirs(f"out/{label}", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    for d in drafts:
        src = open(f"drafts/{d}.md").read()
        # Cap the reply near the draft's own length, so a model that loops
        # stops instead of running for minutes.
        cap = min(3000, int(len(src.split()) * 2.2) + 200)
        if "reasoning_effort" in json.dumps(extra):
            cap += 1500  # room for gpt-oss's reasoning, which cannot be switched off
        client = Client(extra, cap)
        t0 = time.time()
        r = rewrite(src, "github", model=label, client=client)
        secs = round(time.time() - t0, 1)
        out = r["text"]
        open(f"out/{label}/{d}.md", "w").write(out + "\n")
        cw_src, cw_out = content_words(src), content_words(out)
        row = {
            "model": label, "draft": d, "secs": secs, "passes": r["passes"],
            "words_in": len(src.split()), "words_out": len(out.split()),
            "lint_in": sev(lint_text(src, "github")), "lint_out": sev(r["findings"]),
            "score_in": r["score_before"]["log_odds"], "score_out": r["score_after"]["log_odds"],
            "delta_in": r["score_before"].get("delta", {}).get("closer_to"),
            "delta_out": r["score_after"].get("delta", {}).get("closer_to"),
            "immutables": r["preservation"]["n_immutables"],
            "missing": r["preservation"]["n_missing"],
            "missing_detail": r["preservation"]["missing"],
            "content_recall": round(len(cw_src & cw_out) / max(1, len(cw_src)), 3),
            "calls": client.messages.calls,
        }
        with open(f"results/{label}.jsonl", "a") as fh:
            fh.write(json.dumps(row) + "\n")
        print(json.dumps({k: row[k] for k in ("draft", "secs", "passes", "words_in", "words_out",
                                              "lint_out", "score_in", "score_out", "missing",
                                              "content_recall")}), flush=True)


if __name__ == "__main__":
    main()
