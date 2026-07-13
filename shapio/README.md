# Shap.IO — AI Nutrition & Training iOS App (Shipped Solo)

> A native iOS app I designed and built **end to end, alone** — UI/UX, mobile, backend, infrastructure and App Store release. It uses AI vision to turn a photo of a meal into calories and macros, and generates personalized meal and training plans.

📲 **Live on the App Store** · Launched June 2026 · ~3 months of solo development

<!-- ![Shap.IO](./images/01-app.jpg) -->
<!-- App screenshots to be added -->

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

App screenshots will live in [`images/`](./images).

> **Note:** send me current Shap.IO screenshots (or confirm which screens to feature) and I'll drop them in.
