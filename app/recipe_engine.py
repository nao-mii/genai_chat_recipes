import json, re
from typing import List, Dict, Any, Optional

def load_local_recipes(path: str = "data/recipes_sample.json") -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def matches_diet(recipe: Dict[str, Any], dietary: List[str]) -> bool:
    if not dietary:
        return True
    rset = set([d.lower() for d in recipe.get("dietary", [])])
    qset = set([d.lower() for d in dietary])
    # requisito: receita deve conter todas as restrições solicitadas
    return qset.issubset(rset)

def matches_time(recipe: Dict[str, Any], time_limit: Optional[int]) -> bool:
    if not time_limit:
        return True
    return recipe.get("time_minutes", 10**9) <= time_limit

def matches_pantry(recipe: Dict[str, Any], pantry: List[str]) -> int:
    """ Retorna score de interseção de ingredientes. """
    if not pantry:
        return 0
    r_ing = set([i.lower() for i in recipe.get("ingredients", [])])
    p_ing = set([i.lower() for i in pantry])
    return len(r_ing.intersection(p_ing))

def filter_candidates(recipes: List[Dict[str, Any]], pantry: List[str], dietary: List[str], time_limit: Optional[int], cuisine: Optional[str]) -> List[Dict[str, Any]]:
    candidates = []
    for r in recipes:
        if cuisine and cuisine.lower() not in r.get("cuisine","").lower():
            continue
        if not matches_diet(r, dietary):
            continue
        if not matches_time(r, time_limit):
            continue
        score = matches_pantry(r, pantry)
        candidates.append((score, r))
    # ordena por maior score de interseção com a despensa
    candidates.sort(key=lambda x: (-x[0], x[1].get("time_minutes", 10**9)))
    return [r for _, r in candidates][:5]

def build_llm_messages(system_prompt: str, user_guidance: str, context: Dict[str, Any], candidates: List[Dict[str, Any]]):
    ctx = user_guidance.format(**context)
    ctext = ""
    if candidates:
        ctext = "\nReceitas candidatas locais:\n" + "\n".join(
            [f"- {c['title']} ({c.get('time_minutes','?')} min) | ingredientes: {', '.join(c.get('ingredients', []))}" for c in candidates]
        )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": ctx + ctext}
    ]
    return messages
