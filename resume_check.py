#!/usr/bin/env python3
"""Сверка резюме с текстом вакансии по ключевым словам (русский язык, без зависимостей).

Примеры:
    python resume_check.py resume.txt vacancy.txt
    python resume_check.py skills povara resume.txt
    python resume_check.py list
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

DATA = Path(__file__).parent / "data" / "skills_by_profession.json"

STOPWORDS = set("""
и в во не что он на я с со как а то все она так его но да ты к у же вы за бы по только ее мне было вот от меня еще нет о из ему теперь когда даже ну вдруг ли если уже или ни быть был него до вас нибудь опять уж вам ведь там потом себя ничего ей может они тут где есть надо ней для мы тебя их чем была сам чтоб без будто чего раз тоже себе под будет ж тогда кто этот того потому этого какой совсем ним здесь этом один почти мой тем чтобы нее сейчас были куда зачем всех никогда можно при наконец два об другой хоть после над больше тот через эти нас про всего них какая много разве три эту моя впрочем хорошо свою этой перед иногда лучше чуть том нельзя такой им более всегда конечно всю между
требования обязанности условия вакансия компания работа опыт знание умение навыки готовы ищем предлагаем график оплата зарплата
""".split())

TOKEN = re.compile(r"[a-zа-яё0-9+#.]+", re.IGNORECASE)


def stem(word):
    """Грубая основа: убираем гласную в конце и оставляем первые 4 буквы."""
    w = word.lower().replace("ё", "е").strip(".")
    if len(w) > 3 and w[-1] in "аяуюыиеоьй":
        w = w[:-1]
    return w[:4]


def keywords(text, min_len=3):
    """Ключевые слова текста: основа -> частота, без стоп-слов и коротких слов."""
    counts = Counter()
    for tok in TOKEN.findall(text):
        t = tok.lower().replace("ё", "е").strip(".")
        if len(t) < min_len or t in STOPWORDS or t.isdigit():
            continue
        counts[stem(t)] += 1
    return counts


def compare(resume, vacancy, top=25):
    """Вернуть охват ключевых слов вакансии резюме, найденные и отсутствующие слова."""
    vac = keywords(vacancy)
    res = keywords(resume)
    ranked = [w for w, _ in vac.most_common(top)]
    found = [w for w in ranked if w in res]
    missing = [w for w in ranked if w not in res]
    coverage = round(100 * len(found) / len(ranked)) if ranked else 0
    return {"coverage": coverage, "found": found, "missing": missing}


def load_professions():
    """Справочник навыков по профессиям (slug -> запись)."""
    with open(DATA, encoding="utf-8") as f:
        return {p["slug"]: p for p in json.load(f)}


def skills_gap(slug, resume):
    """Какие типовые навыки профессии уже есть в тексте резюме, а каких нет."""
    prof = load_professions().get(slug)
    if prof is None:
        raise KeyError(slug)
    res = set(keywords(resume, min_len=2))
    found, missing = [], []
    for skill in prof["skills"]:
        main = re.sub(r"\(.*?\)", "", skill)
        stems = set(keywords(main, min_len=2))
        (found if stems and stems <= res else missing).append(skill)
    return {"profession": prof["profession_genitive"], "found": found, "missing": missing,
            "url": prof["url"]}


def main(argv):
    if len(argv) == 2 and argv[1] == "list":
        for slug, p in sorted(load_professions().items()):
            print(f"{slug}\t{p['profession_genitive']}")
        return 0
    if len(argv) == 4 and argv[1] == "skills":
        with open(argv[3], encoding="utf-8") as f:
            r = skills_gap(argv[2], f.read())
        print(f"Типовые навыки: {r['profession']}")
        print("Есть в резюме:", ", ".join(r["found"]) or "-")
        print("Нет в резюме:", ", ".join(r["missing"]) or "-")
        print("Подробнее:", r["url"])
        return 0
    if len(argv) != 3:
        print(__doc__)
        return 1
    with open(argv[1], encoding="utf-8") as f:
        resume = f.read()
    with open(argv[2], encoding="utf-8") as f:
        vacancy = f.read()
    r = compare(resume, vacancy)
    print(f"Охват ключевых слов вакансии: {r['coverage']}%")
    print("Есть в резюме:", ", ".join(r["found"]) or "-")
    print("Нет в резюме:", ", ".join(r["missing"]) or "-")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
