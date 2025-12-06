import random
import spacy
import json

# spaCy modelini yüklüyoruz
nlp = spacy.load("en_core_web_lg")

# Kelime havuzunu okuyoruz
with open("word_pool.json", "r") as f:
    word_pool = json.load(f)["words"]

# Kullanacağımız profil listeleri
spymaster_profiles = ["EXPERT", "GOOD", "MID", "BAD", "TERRIBLE"]
guesser_profiles = ["EXPERT", "GOOD", "MID", "BAD", "TERRIBLE"]

# Benzerlik eşikleri (guesser profilleri için)
thresholds = {
    "EXPERT": 0.28,
    "GOOD": 0.20,
    "MID": 0.15,
    "BAD": 0.10,
    "TERRIBLE": 0.07
}

# Clue skorunu hesaplayan fonksiyon
# Burada role göre farklı ağırlıklar uyguluyoruz
def role_weighted_score(clue, board, profile):
    clue_vec = nlp(clue)
    score = 0
    for cell in board:
        word = cell["word"]
        role = cell["role"]
        sim = clue_vec.similarity(nlp(word))

        # Profilin hassasiyetine göre ağırlıklar
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

# Guesser'ın clue'ya göre en çok benzeyen kelimeleri bulması
def guess_words(clue, board):
    clue_vec = nlp(clue)
    similarities = [
        (cell["word"], cell["role"], clue_vec.similarity(nlp(cell["word"])))
        for cell in board
    ]
    similarities.sort(key=lambda x: x[2], reverse=True)
    return similarities[:20]  # en yüksek 20 benzerlik

# Tahminlerin yüzde dağılımını hesaplama
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

# Konsolda ilerleme çubuğu için basit bir fonksiyon
def print_progress(current, total, bar_length=30):
    percent = current / total
    filled = int(bar_length * percent)
    bar = "█" * filled + "-" * (bar_length - filled)
    print(f"\rProgress: [{bar}] {percent*100:.0f}%", end="")

results = []

# Kaç oyun simülasyonu yapılacağını buradan ayarlıyoruz
NUM_GAMES = 100

# Tüm kombinasyonlar için simülasyon
for spymaster in spymaster_profiles:
    for guesser in guesser_profiles:
        total_score = 0
        success = 0
        fail = 0
        natural = 0
        lose = 0

        print(f"\nRunning Simulation for Spymaster: {spymaster}, Guesser: {guesser}")

        for i in range(NUM_GAMES):
            # Rastgele 25 kelimelik board oluşturuyoruz
            selected_words = random.sample(word_pool, 25)
            roles = ["red"] * 9 + ["blue"] * 8 + ["neutral"] * 7 + ["black"]
            random.shuffle(roles)
            board = [{"word": selected_words[i], "role": roles[i]} for i in range(25)]

            # Clue adaylarını oluşturuyoruz
            clue_candidates = [word for word in word_pool if word not in selected_words]
            scored_clues = [
                (clue, role_weighted_score(clue, board, spymaster))
                for clue in clue_candidates
            ]
            scored_clues.sort(key=lambda x: x[1], reverse=True)

            # Spymaster profilinin davranışı
            if spymaster == "EXPERT":
                selected_clue = scored_clues[0]
            elif spymaster == "GOOD":
                selected_clue = random.choice(scored_clues[:3])
            elif spymaster == "MID":
                selected_clue = random.choice(scored_clues[3:6])
            elif spymaster == "BAD":
                selected_clue = random.choice(scored_clues[6:9])
            else:
                selected_clue = random.choice(scored_clues[8:15])

            # Guesser tahminleri
            guesses = guess_words(selected_clue[0], board)
            cutoff = thresholds[guesser]
            qualified = [i for i, (_, _, sim) in enumerate(guesses) if sim >= cutoff]

            # Guesser iki tahmin yapıyor
            if not qualified:
                marked_indices = list(range(min(2, len(guesses))))
            else:
                marked_indices = random.sample(qualified, min(2, len(qualified)))

            marked_guesses = [guesses[i] for i in marked_indices]

            # Siyah kelimeye denk gelirse skor direkt 0 oluyor
            if any(role == "black" for _, role, _ in marked_guesses):
                round_score = 0
                lose += 1
            else:
                round_score = sum(
                    1 if role == "red" else -1 if role == "blue" else 0
                    for _, role, _ in marked_guesses
                )

            total_score += round_score

            # Yüzdeleri ekliyoruz
            r_pct, n_pct, b_pct, bl_pct = evaluate_guesses_with_percent(marked_guesses)
            success += r_pct
            fail += b_pct
            natural += n_pct
            lose += bl_pct

            print_progress(i + 1, NUM_GAMES)

        # Sonuçları kaydediyoruz
        results.append(
            (spymaster, guesser,
             total_score / NUM_GAMES,
             success / 100,
             fail / 100,
             natural / 100,
             lose / 100)
        )

# Tüm sonuçları dosyaya yazıyoruz
with open("simulation_results.txt", "w", encoding="utf-8") as f:
    for spymaster, guesser, avg, succ, fail, nat, lose in results:
        f.write(f"\nSpymaster: {spymaster}, Guesser: {guesser}\n")
        f.write(f"- Avg Score: {avg:.2f}\n")
        f.write(f"- % Success: {succ:.2f}%\n")
        f.write(f"- % Fail (Blue): {fail:.2f}%\n")
        f.write(f"- % Natural (Neutral): {nat:.2f}%\n")
        f.write(f"- % Lose (Black): {lose:.2f}%\n")
        f.write(f"- Num of Games: {NUM_GAMES}\n")