"""
Standalone rule-based rewrite engine for Chinese academic text AIGC reduction.
Applies vocabulary substitution, sentence expansion, and structural loosening
without requiring external LLM API calls. Works as a local-only engine.
"""
import re
from typing import List, Tuple

# === Round 1: Vocabulary substitution table ===
VERB_REPLACEMENTS = [
    ("使用", "运用"), ("采用", "选用"), ("利用", "借助"),
    ("通过", "依靠"), ("实现", "得以实现"),
]

CONJ_REPLACEMENTS = [
    ("和", "以及"), ("及", "以及"), ("与", "以及"),
    ("并", "并且"), ("其", "它"),
]

NOUN_REPLACEMENTS = [
    ("特点", "特性"), ("符合", "契合"), ("适合", "适宜"),
    ("原因", "缘由"), ("极大", "极大程度"),
]

# === Round 2: AI template phrase removal ===
AI_CLICHES = [
    r"随着.{1,20}的(不断)?发展",
    r"展现出了?(广阔|巨大)的",
    r"起到了?(重要|关键)的作用",
    r"具有.{1,10}的(参考)?价值",
    r"本文(设计|提出|实现)了",
    r"实验(结果|表明|证明)",
    r"总而言之",
    r"综上所述",
]

HELPER_WORDS = ["了", "的", "所", "会", "可以", "这个", "方面", "当中"]
SENTENCE_STARTERS = ["那么", "这样", "同时", "另外", "此外"]


def apply_round1(text: str) -> str:
    """Apply Round 1: redundancy + vocabulary substitution + sentence loosening."""
    result = text

    # 1. Vocabulary replacements (only first occurrence per paragraph to avoid over-replacement)
    for old, new in VERB_REPLACEMENTS + CONJ_REPLACEMENTS + NOUN_REPLACEMENTS:
        if old in result:
            result = result.replace(old, new, 1)

    # 2. Insert helper words at natural break points
    sentences = re.split(r"([。！？；])", result)
    new_sentences = []
    for i, seg in enumerate(sentences):
        if i % 2 == 0 and len(seg) > 20:  # content sentences
            import random
            if random.random() < 0.3:  # ~30% chance to add helper
                helper = random.choice(HELPER_WORDS)
                if helper in ["了", "的", "所"]:
                    seg = seg[:len(seg)//2] + helper + seg[len(seg)//2:]
        new_sentences.append(seg)

    return "".join(new_sentences)


def apply_round2(text: str) -> str:
    """Apply Round 2: remove AI cliches, loosen logic connectors."""
    result = text

    # 1. Replace AI template phrases
    for pattern in AI_CLICHES:
        result = re.sub(pattern, "", result)

    # 2. Loosen conditional structures
    result = result.replace("若", "要是")
    result = result.replace("则", "那就")

    # 3. Remove stacked transition words
    result = re.sub(r"(此外|另外|同时)\s*(此外|另外|同时)", r"\1", result)

    return result


def rewrite_chinese(text: str, round_num: int = 1) -> str:
    """
    Main entry point. Apply specified round of Chinese AIGC reduction.
    round_num: 1 for redundancy+vocabulary, 2 for AI-cliche removal
    """
    if round_num == 1:
        return apply_round1(text)
    elif round_num == 2:
        return apply_round2(text)
    return text


def batch_rewrite(paragraphs: List[Tuple[int, str]], round_num: int = 1) -> dict:
    """
    Batch rewrite multiple paragraphs. Returns mapping dict {index: rewritten_text}.
    """
    mapping = {}
    for idx, text in paragraphs:
        mapping[str(idx)] = rewrite_chinese(text, round_num)
    return mapping


if __name__ == "__main__":
    # Quick test
    test_text = "随着人工智能技术的不断发展，手势识别展现出了广阔的应用前景。本文设计了一种基于深度学习的手势识别系统，具有重要的参考价值。"
    print("原始:", test_text)
    print("第一轮:", rewrite_chinese(test_text, 1))
    print("第二轮:", rewrite_chinese(rewrite_chinese(test_text, 1), 2))
