import random
import spacy
import json

# MODELİ YÜKLE
nlp = spacy.load("en_core_web_lg")

# KELİME HAVUZU OKU
with open("word_pool.json", "r") as f:
    word_pool = json.load(f)["words"]
selected_words = random.sample(word_pool, 25)

# ROLLERİ ATA
roles = ["red"] * 9 + ["blue"] * 8 + ["neutral"] * 7 + ["black"]
random.shuffle(roles)
board = [{"word": selected_words[i], "role": roles[i]} for i in range(25)]

# RENKLİ TAHTAYI GÖSTER
print("\n\U0001F3AF Complete 5x5 Board:")
for i in range(5):
    row = board[i*5:(i+1)*5]
    display_row = []
    for cell in row:
        word = cell["word"].ljust(12)
        role = cell["role"]
        if role == "red":
            tag = "[RED]   "
        elif role == "blue":
            tag = "[BLUE]  "
        elif role == "black":
            tag = "[BLACK] "
        else:
            tag = "[NEUTRAL]"
        display_row.append(f"{tag} {word}")
    print("  ".join(display_row))

# CLUE SKORLAMA (profil bazlı)
def role_weighted_score(clue, board, profile):
    clue_vec = nlp(clue)
    score = 0
    for cell in board:
        word = cell["word"]
        role = cell["role"]
        sim = clue_vec.similarity(nlp(word))
        if profile == "EXPERT":
            weights = {"red": 1.0, "blue": -1.5, "black": -2.5, "neutral": -0.4}
        elif profile == "GOOD":
            weights = {"red": 1.0, "blue": -1.2, "black": -2.5, "neutral": -0.4}
        elif profile == "MID":
            weights = {"red": 1.0, "blue": -1.0, "black": -2.0, "neutral": -0.4}
        elif profile == "BAD":
            weights = {"red": 0.8, "blue": -0.8, "black": -2.0, "neutral": -0.3}
        else:
            weights = {"red": 0.6, "blue": -0.5, "black": -1.5, "neutral": -0.2}
        score += sim * weights[role]
    return score

# CLUE KELİMELERİ
clue_candidates = [word for word in word_pool if word not in selected_words]
spymaster_profiles = ["EXPERT", "GOOD", "MID", "BAD", "TERRIBLE"]
spymaster_type = random.choice(spymaster_profiles)

scored_clues = [(clue, role_weighted_score(clue, board, spymaster_type)) for clue in clue_candidates]
scored_clues.sort(key=lambda x: x[1], reverse=True)

print("\n\U0001F4C8 Top 10 Clue Suggestions:")
for clue, score in scored_clues[:10]:
    print(f"Clue: {clue:12} → Score: {score:.4f}")

print(f"\n\U0001F9D1‍\U0001F4BC Spymaster Profile: {spymaster_type}")
best_clue, best_score = scored_clues[0]
print(f"\U0001F4A1 Best Clue Suggestion: '{best_clue}' with score: {best_score:.4f}")

if spymaster_type == "EXPERT":
    selected_clue = scored_clues[0]
elif spymaster_type == "GOOD":
    selected_clue = random.choice(scored_clues[:3])
elif spymaster_type == "MID":
    selected_clue = random.choice(scored_clues[3:6])
elif spymaster_type == "BAD":
    selected_clue = random.choice(scored_clues[6:9])
else:
    selected_clue = random.choice(scored_clues[8:15])

print(f"\U0001F3AF Selected Clue by Spymaster: '{selected_clue[0]}' with score: {selected_clue[1]:.4f}")

# GUESSER TAHMİN

def guess_words(clue, board):
    clue_vec = nlp(clue)
    similarities = [(cell["word"], cell["role"], clue_vec.similarity(nlp(cell["word"]))) for cell in board]
    similarities.sort(key=lambda x: x[2], reverse=True)
    return similarities[:20]

# YÜZDE HESAPLA

def evaluate_guesses_with_percent(guesses):
    red = sum(1 for _, role, _ in guesses if role == "red")
    blue = sum(1 for _, role, _ in guesses if role == "blue")
    neutral = sum(1 for _, role, _ in guesses if role == "neutral")
    black = sum(1 for _, role, _ in guesses if role == "black")
    total = len(guesses)
    if total == 0:
        return 0, 0, 0, 0
    return (
        (red / total) * 100,
        (neutral / total) * 100,
        (blue / total) * 100,
        (black / total) * 100
    )

# GUESSER PROFİLİ

profiles = ["EXPERT", "GOOD", "MID", "BAD", "TERRIBLE"]
guesser_type = random.choice(profiles)
thresholds = {
    "EXPERT": 0.28,
    "GOOD": 0.20,
    "MID": 0.15,
    "BAD": 0.10,
    "TERRIBLE": 0.07
}

# GUESSING AŞAMASI

print(f"\n\U0001F9E0 Guesser Profile: {guesser_type}")
guesses = guess_words(selected_clue[0], board)
cutoff = thresholds[guesser_type]
qualified = [i for i, (_, _, sim) in enumerate(guesses) if sim >= cutoff]
if not qualified:
    marked_indices = list(range(min(2, len(guesses))))
else:
    marked_indices = random.sample(qualified, min(2, len(qualified)))

print("\U0001F916 Guesser Predictions:")
for idx, (word, role, sim) in enumerate(guesses):
    marker = "\U0001F3AF" if idx in marked_indices else "   "
    print(f"{marker} Guessed: {word:12} | Role: {role:7} | Similarity: {sim:.4f}")

# SKOR HESAPLAMA

final_score = 0
black_triggered = any(guesses[i][1] == "black" for i in marked_indices)
if black_triggered:
    score_display = "X"
else:
    final_score = sum(1 if guesses[i][1] == "red" else -1 if guesses[i][1] == "blue" else 0 for i in marked_indices)
    score_display = str(final_score)

percent_success, percent_natural, percent_fail, percent_lose = evaluate_guesses_with_percent([guesses[i] for i in marked_indices])

print(f"\n\U0001F3AF Guess Score: {score_display}")
print(f"✅ Percent Success:  {percent_success:.2f}%")
print(f"\U0001F7E8 Percent Natural:  {percent_natural:.2f}% (Losing Turn)")
print(f"❌ Percent Fail:     {percent_fail:.2f}% (Enemy Team +1 Point)")
print(f"☠ Percent Lose:     {percent_lose:.2f}% (Assassin Word)")