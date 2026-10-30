# Genre labeling guide v1.0 (FROZEN 2026-10-13)

**Status: FROZEN.** This is the genre list and rule set for both datasets (golden rule 2). It was frozen
before any judge was run. If a gap is found later, write v1.1 with the date and the reason, relabel the
affected questions, and do it **before any judge result is seen**.

**What to look at:** the question and the passage only, never the answer. Decide from the question first.
Use the passage only to understand what or who the question is about. Background knowledge may be used to
recognize a person or a place, as any human labeler would.

## How this guide was made

1. **v0.1:** Claude read 120 random BenHalluEval QA questions (seed 13) and drafted the genres and rules.
2. **v0.2:** Claude labeled all 997 unique questions and sharpened rules 5–8 along the way.
3. **Blind check:** Mahdi labeled 200 random questions (seed 2026) without seeing Claude's labels.
   - Agreement with Claude's v0.2 draft: **85.0%**, Cohen's kappa **0.806** (95% range 0.737 to 0.866), using
     the v1.0 genre names. This is the clean number.
   - On questions Claude marked high confidence: 92% agreement. On questions marked low confidence: 41%.
4. **v1.0:** the disagreements showed four rule gaps.
   - Mahdi decided all four: word meaning/origin, buildings/opening dates, schools and colleges, and merging
     Sports.
   - Two more rules were adopted from Mahdi's blind labels: mythology goes to Religion, philosophy goes to
     Arts.
   - 43 draft labels changed (`data/labels/genre_rule_changes_v1.txt`).
   - Agreement of the blind sheet with the v1.0 draft is kappa 0.817. That number is optimistic, because
     the rules were revised using this same sheet.

## Genres (5 + Other)

| Genre | What belongs here | Examples |
|---|---|---|
| **History, Politics & Education** | Past events, eras, dynasties, empires, rulers, wars, colonial history, the language movement and the liberation war. Government, constitutions, laws, elections, political parties and officeholders. Administration, the military, the police and intelligence services. National symbols. Schools, colleges, universities and libraries (founding, heads, students, affiliation). People mainly known for any of these. | খিলজি রাজবংশের প্রতিষ্ঠাতা কে ? · বাংলাদেশ জাতীয়তাবাদী দলের সর্বপ্রথম চেয়ারম্যান কে ছিলেন ? · কুমিল্লা ভিক্টোরিয়া কলেজের প্রথম অধ্যক্ষ কে ছিলেন ? |
| **Arts, Culture & Sports** | Literature (books, poems, plays), film and TV, music and dance, painting and sculpture, theatre, folk culture, festivals and food. Language features, grammar and scripts. Philosophy. Sports: games, teams, clubs, tournaments, the Olympics, players, coaches and sports bodies. People mainly known for any of these. | শরৎচন্দ্র চট্টোপাধ্যায়ের রচিত "শ্রীকান্ত" উপন্যাসটির মোট কতগুলি খণ্ড আছে ? · চঞ্চল চৌধুরী অভিনীত সর্বপ্রথম বাংলাদেশি চলচ্চিত্র কোনটি ? · আন্তর্জাতিক ক্রিকেট কাউন্সিলের মোট সদস্য ভুক্ত দেশ কয়টি ? |
| **Science & Technology** | Physics, chemistry, biology, the human body, medicine and health, mathematics, computing and the internet, inventions and engineering, agriculture, animals, plants and general natural phenomena. Technology companies. Scientists and inventors. | ছত্রাক কোন কোষ দ্বারা গঠিত হয় ? · কত সালে সর্বপ্রথম ডেটাবেজ আবিষ্কার করা হয় ? |
| **Geography & Places** | Countries, regions, cities, districts, capitals and headquarters. Rivers, mountains, glaciers and seas. Area, population and administrative units. Landmarks, buildings and infrastructure: location, size, when built, opened or renamed, who designed them, old names. The languages a country speaks; a country's currency. | হুগলী নদীর দৈর্ঘ্য কত ? · পূর্ব মেদিনীপুর জেলার সদর শহর কোনটি ? · কলকাতা মেট্রো প্রথম কবে থেকে চালু হয় ? |
| **Religion** | Religions and beliefs, scriptures and religious terms. Gods, prophets, caliphs of early Islam, gurus, saints and monks. Characters and events of epics, Puranas and mythologies. Temples, mosques, monasteries, religious groups and reform movements. | হিন্দুধর্মের প্রাচীন নাম কী ? · গুরু নানকের বাবার নাম কী ? · হিন্দু পুরাণ মতে সীতার মায়ের নাম কী ? |
| **Other** | Only when nothing above fits: economy, banks and business (non-technology), banknotes, media, accidents and disasters, everyday life. Should stay small. | বর্তমানে (২০১৯) বাংলাদেশে মোট কতগুলি ওষুধ কোম্পানি আছে ? · তাজরীন ফ্যাশন অগ্নিকাণ্ডে মোট কত জন নিহত হয় ? |

## Rules for unsure cases (apply in this order)

1. **Questions about a person** (birth, death, parents, spouse, education, career) → the field the person is
   mainly known for. Example: হুমায়ূন আহমেদ কবে জন্মগ্রহণ করেন → Arts, Culture & Sports (writer). If the person
   is known for several fields, use the one the question or the passage's first description names first.
2. **Places:** a named place and its properties (location, area, length, height, population, headquarters,
   administrative units, when built, opened or renamed, who designed it, old names) → Geography & Places.
   Exceptions:
   - religious buildings → Religion;
   - sports venues → Arts, Culture & Sports;
   - an *event* that happened at a place → History, Politics & Education;
   - schools and universities follow rule 5.
3. **General natural concepts** (layers of the atmosphere, cells, genes) → Science & Technology. A specific
   named geographic feature (a river, a glacier) → Geography & Places.
4. **"Who was first / what was first / who invented"** → the field of the thing (first computer → Science &
   Technology; first Bangla rock band → Arts, Culture & Sports; first independent king → History, Politics &
   Education).
5. **Organizations** → the field they work in:
   - ICC → Arts, Culture & Sports; MI6 → History, Politics & Education; a technology company → Science &
     Technology; other companies and banks → Other.
   - Schools, colleges, universities and libraries → History, Politics & Education. If the question asks
     about one as a place (area, location), use Geography & Places.
   - Museums → the field of their collection (a Liberation War museum or a university museum → History,
     Politics & Education).
6. **Words and languages:**
   - The meaning or origin of a word → the field of the word (পাপ, জৈন → Religion; জমিদার → History, Politics &
     Education; জিন → Science & Technology).
   - Grammar terms, and words that belong to no other field → Arts, Culture & Sports.
   - A language's own features, script or history → Arts, Culture & Sports. Which languages a country or
     people speaks → Geography & Places.
7. **National symbols** (flag, anthem, emblem) → History, Politics & Education.
   **Mythology:** gods, characters and events of the Ramayana, the Mahabharata, the Puranas and other
   mythologies → Religion. Literary works that retell them (for example *Meghnadbadh Kavya*) and their
   translations → Arts, Culture & Sports.
8. **Still unsure:** pick the best fit and mark confidence `low`. If the passage does not say who a person
   is, use what the person is best known for; if that is unknown too, mark `low`.

## Confidence

- `high`: one genre clearly fits.
- `low`: two genres fit about equally, or the topic is unclear. Checkers should look at these first.

## Counts (Claude's v1.0 draft, 997 unique questions, before human verification)

| Genre | Questions | Share | Low confidence |
|---|---|---|---|
| History, Politics & Education | 306 | 30.7% | 36 |
| Arts, Culture & Sports | 301 | 30.2% | 21 |
| Science & Technology | 153 | 15.3% | 23 |
| Geography & Places | 120 | 12.0% | 19 |
| Religion | 102 | 10.2% | 21 |
| Other | 15 | 1.5% | 11 |
| **Total** | **997** | | **131** |

Every genre except Other has at least 100 questions. 57 of the Arts, Culture & Sports questions are sports
questions; the column `genre_fine` keeps that detail for exploratory analysis only. Recount after human
verification.
