# Shap.IO — AI Nutrition & Training iOS App (Shipped Solo)

> A native iOS app I designed and built **end to end, alone** — UI/UX, mobile, backend, infrastructure and App Store release. It uses AI vision to turn a photo of a meal into calories and macros, and generates personalized meal and training plans.

📲 **Live on the App Store** · Launched June 2026 · ~3 months of solo development

<table>
<tr>
<td align="center"><img src="./Simulator%20Screenshot%20-%20iPhone%2014%20Plus%20-%202026-06-19%20at%2012.54.55.png" width="230"><br><sub><b>Home</b> — calories & macros ring</sub></td>
<td align="center"><img src="./Simulator%20Screenshot%20-%20iPhone%2014%20Plus%20-%202026-06-19%20at%2012.55.14.png" width="230"><br><sub><b>Profile</b> — metabolism & 4-language toggle</sub></td>
<td align="center"><img src="./Simulator%20Screenshot%20-%20iPhone%2014%20Plus%20-%202026-06-19%20at%2012.56.12.png" width="230"><br><sub><b>AI recipe</b> — post-workout, macro-matched</sub></td>
<td align="center"><img src="./Simulator%20Screenshot%20-%20iPhone%2014%20Plus%20-%202026-06-19%20at%2012.56.40.png" width="230"><br><sub><b>Workout</b> — logged & synced to nutrition</sub></td>
</tr>
</table>

---

## What it does

- **Photo → nutrition.** Take a photo of a plate and get instant **calories and macros** via AI vision.
- **Personalized weekly meal plan.** Generated from age, weight, goal, allergies, budget and cooking time.
- **Weekly training plan** with progressive overload.
- **Gym session logging** (sets, reps, weight, rest) — and it suggests the next set's weight from your history plus a mood check-in.
- **Post-workout recipe** wired into the nutrition module.
- **Automatic shopping list** from the weekly plan.
- **Localized in 4 languages:** English, Spanish, German, Portuguese.

## Tech stack

| Layer | Technology |
|---|---|
| Mobile | React Native + Expo (SDK 52) |
| Backend | Node.js / Express on Railway |
| Database / Auth | Supabase |
| AI | Anthropic Claude (vision + generation) |
| Monetization | RevenueCat (in-app purchases), AdMob (free tier) |
| Platform | Native iOS, App Store |

## Why it matters (as an engineering project)

- **Full-stack, solo.** I owned every layer: design, front end, API, database, third-party integrations, infrastructure and the App Store submission/review process.
- **Real AI integration** in production — image understanding and structured plan generation, with cost per user tracked and controlled.
- **Real product constraints** — free vs. premium tiers, IAP, ads, localization in four languages, and a sustainable margin after platform and AI costs.

## What I learned

- Shipping a **real product to real users** is a different discipline from building a prototype: reliability, cost control, store review, and localization all matter.
- Designing an **AI pipeline that stays cheap and fast** at scale.
- Owning the **entire stack** end to end as a single developer.

## Media

App screenshots are in this folder (iPhone and iPad).
