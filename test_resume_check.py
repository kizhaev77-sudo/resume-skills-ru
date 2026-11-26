import json
from pathlib import Path

import resume_check as rc

VACANCY = "Менеджер по продажам. Требуется опыт холодных звонков, работа в amoCRM, ведение переговоров, Excel."
RESUME = "Менеджер по продажам: холодные звонки, переговоры, ведение клиентской базы в amoCRM."


def test_keywords_skip_stopwords():
    kw = rc.keywords("Мы ищем менеджера для работы с клиентами")
    assert "мене" in kw
    assert "для" not in kw


def test_compare_finds_and_misses():
    r = rc.compare(RESUME, VACANCY)
    assert "amoc" in r["found"]
    assert "exce" in r["missing"]
    assert 0 < r["coverage"] < 100


def test_empty_vacancy():
    assert rc.compare("текст", "")["coverage"] == 0


def test_dataset_shape():
    data = json.load(open(Path(__file__).parent / "data" / "skills_by_profession.json", encoding="utf-8"))
    assert len(data) == 94
    assert all(14 <= len(p["skills"]) <= 20 for p in data)


def test_skills_gap():
    r = rc.skills_gap("povara", "Повар горячего цеха, работаю по технологическим картам, знаю ХАССП, iiko.")
    assert "ХАССП" in r["found"]
    assert "iiko" in r["found"]
    assert "Фудкост" in r["missing"]
