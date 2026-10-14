"""
Generates 3 realistic, detailed meeting transcripts for Task 3:
1. meeting_1_discovery.txt: Initial discovery meeting for LegalMatch Pro
2. meeting_2_followup_changes.txt: Follow-up meeting changing requirements and introducing Scope Creep
3. meeting_3_directory_marketplace.txt: Alternative discovery meeting for BioTech Supply Hub
"""

import os

MEETING_1 = """[00:00:05] Alex Rivera (Consultant): Good morning Sarah! Thanks for hopping on the call today. I'm excited to dive into LegalMatch Pro and map out how we can get your attorney directory launched.
[00:00:18] Sarah Jenkins (Client): Good morning Alex! Thanks for making time. We have a lot of moving parts. Right now we have about 400 attorney profiles in an Excel sheet, and we want to launch a professional directory where people can find vetted lawyers across Texas, California, and New York.
[00:00:38] Alex: Fantastic. Let's walk through the user journey for both the public visitor looking for an attorney and the attorney creating their profile.
[00:00:52] Sarah: Okay, so a regular person lands on the home page. They should see a clean search bar. They need to filter by practice area—like Criminal Defense, Family Law, Estate Planning, Corporate—and then type their city or zip code.
[00:01:14] Alex: Understood. Brilliant Directories has a built-in search widget specifically for Category plus Location with radius filtering. We can configure that right out of the box in the Design Settings.
[00:01:28] Sarah: Oh, that's great that we don't have to code that from scratch. Now, when the search results appear, we want the premium paid attorneys to always show up at the top with a distinct 'Featured Counselor' badge and a direct phone number. The free basic profiles should show up below, with just their name and contact button.
[00:01:52] Alex: Absolutely. In Brilliant Directories, that's controlled natively by Membership Plans and Search Priority order. We can assign Priority 1 to Tier 1 Premium at $99/month, and Priority 10 to Free listings. That's a zero-code configuration.
[00:02:12] Sarah: Perfect. Now here is something specific we do need custom help with. For our 'Vetted Counselor' verification, we want attorneys to submit their State Bar number during onboarding. We want a backend verification workflow or webhook that flags the profile as 'Bar Verified' once our admin verifies it against the state bar records.
[00:02:37] Alex: Got it. We can add a custom State Bar field to the Member Signup Form, set default status to 'Pending Bar Review', and build a lightweight admin verification toggle with an automated email trigger to notify the attorney once approved. That will require about 8 to 12 hours of custom form scripting and webhook setup.
[00:03:02] Sarah: That sounds reasonable. What about lead generation? When a potential client clicks 'Contact Lawyer' on a profile, what happens?
[00:03:15] Alex: Brilliant Directories has a native Lead Management system. The visitor fills out a quick inquiry modal: their name, phone, brief case description. BD immediately emails that lead directly to that specific attorney, and also logs it in the attorney's private dashboard. You can even monetize it if you want per-lead pricing later.
[00:03:41] Sarah: Wow, so the lead dispatching and notification emails are already built-in?
[00:03:46] Alex: Yes, 100% native. We just need to brand the email template and configure the form fields.
[00:03:54] Sarah: Excellent. In terms of design, we don't want a cookie-cutter look. We need our navy blue (#0A192F) and gold (#C5A880) branding, custom typography (Playfair Display for headings and Inter for body text), a tailored hero section with our logo, and client testimonials on the homepage.
[00:04:18] Alex: Completely doable. We can do that through Brilliant Directories Theme Settings, custom CSS injection, and homepage widget layout styling. Usually that's around 15 hours of front-end styling.
[00:04:35] Sarah: And what about payment processing for the attorney subscriptions?
[00:04:40] Alex: Brilliant Directories integrates natively with Stripe. We enter your Stripe API keys in the Payment Settings, configure monthly recurring billing for $99/mo, and Stripe handles recurring chargebacks, receipts, and retries automatically.
[00:04:58] Sarah: Terrific. And what about importing our 400 attorneys from our Excel spreadsheet?
[00:05:05] Alex: We clean the spreadsheet, map the columns to BD user schema (first name, last name, firm name, address, phone, category), and run it through the BD CSV Import tool. We'll verify geocoding and test 10 records first. That's about 6 hours of data cleaning and import testing.
[00:05:27] Sarah: Wonderful. Can you send over a formal scope of work, hour estimates, and proposal so we can get started?
[00:05:35] Alex: I will generate the complete Scope of Work, breakdown of native features vs custom development hours, and client proposal right away.
[00:05:45] Sarah: Thanks Alex, talk soon!
"""

MEETING_2 = """[00:00:04] Alex Rivera (Consultant): Hi Sarah! Great to connect again for our follow-up review on LegalMatch Pro.
[00:00:12] Sarah Jenkins (Client): Hi Alex! Thanks for hopping on. So we had our board meeting yesterday with our seed angel investors, and there are several major updates and pivots from what we discussed last week.
[00:00:26] Alex: Alright, let's go through them one by one so we can adjust our scope.
[00:00:32] Sarah: First, regarding the search: previously we said standard zip code radius search was fine. But our investors were insistent that users shouldn't have to reload the page when filtering. They want a reactive slider where you slide from 5 miles to 100 miles, and the Google Map pins must update dynamically in real time without refreshing the browser.
[00:00:58] Alex: Okay, that is a change from the out-of-the-box BD search. The native search does a standard form POST/GET reload. To do a real-time reactive slider with client-side map pin redraw, we would need to build a custom JavaScript/Vue/React search widget that queries the BD REST API. That will add approximately 18 to 22 custom development hours.
[00:01:25] Sarah: Okay, that's fine, we definitely need that. Second change: remember the custom State Bar verification workflow we talked about?
[00:01:34] Alex: Yes, the 8-12 hour custom form and webhook integration.
[00:01:38] Sarah: Let's actually DROP that for Phase 1. To keep launch fast and avoid regulatory friction, we will just have attorneys upload a PDF copy of their bar card, and our intern will manually look at it. We don't need any automated bar checking or custom webhook code right now.
[00:01:58] Alex: Perfect, dropping that will save 10 hours from the original custom estimate and simplify the signup form.
[00:02:06] Sarah: Now, here are the two big things our investors insisted on having immediately. Number one: they said having a web-only directory in 2026 is not enough. We MUST launch native iOS and Android apps on the Apple App Store and Google Play Store at the same time, complete with push notifications whenever a lawyer gets a new client lead.
[00:02:33] Alex: Sarah, I need to be completely transparent here. A native iOS and Android mobile app suite with push notification infrastructure and App Store review management was not part of our original web directory scope. That is a completely separate engineering project—typically requiring React Native or Flutter, push notification servers via Firebase, and Apple Developer provisioning. That falls squarely into Scope Creep and would need to be quoted as a separate phase or dedicated add-on project.
[00:03:07] Sarah: I understand. What would that take in terms of timeline and hours if we quote it separately?
[00:03:14] Alex: A cross-platform mobile wrapper with native push notifications, offline caching, and biometric authentication is typically 80 to 120 hours minimum. I will itemize it clearly in the updated proposal as an Optional Phase 2 Add-On so your board can see the exact cost difference without stalling our Phase 1 web launch.
[00:03:38] Sarah: That makes a lot of sense. Don't let it delay the web launch. What about the second item?
[00:03:44] Sarah: Our accountants want bidirectional synchronization with QuickBooks Online. Whenever an attorney pays their $99 subscription in Stripe through the directory, or when we issue a manual refund, it must sync into QuickBooks Online with custom chart of accounts mapping and sales tax breakdown.
[00:04:06] Alex: Again, that is brand new scope that wasn't in the original meeting. Stripe handles basic payment receipts natively, but bidirectional syncing into QuickBooks Online chart-of-accounts requires an accounting middleware (like Zapier Webhook or custom Intuit OAuth API microservice). We can quote that as a 20-hour specialized integration add-on.
[00:04:33] Sarah: Got it. Can you update our Scope of Work to clearly show: what changed in the search, the removal of the bar verification, and separate out the mobile app and QuickBooks sync as out-of-scope extra quotes?
[00:04:49] Alex: Absolutely. I will run the delta analysis and generate an updated Scope of Work with explicit line items for Baseline Changes, Dropped Features, and Out-of-Scope Add-ons with separate quotes.
[00:05:04] Sarah: Brilliant. Talk to you soon Alex!
"""

MEETING_3 = """[00:00:05] Elena Rostova (Consultant): Hello Marcus, welcome to our discovery call for BioTech Supply Hub!
[00:00:15] Marcus Thorne (Client): Hello Elena, glad to be here. We are building a specialized supplier directory for certified biotechnology lab equipment, reagents, and cleanroom consumables across North America.
[00:00:30] Elena: Wonderful. Tell me about the vendors and how they interact with the portal.
[00:00:36] Marcus: We have about 650 pre-screened biotech vendors. We want three membership tiers: Free Bronze, Silver ($199/month), and Gold ($499/month). Gold vendors get featured placement on the homepage, ability to upload 50 product catalogs, and direct inquiry forms.
[00:00:58] Elena: That aligns cleanly with Brilliant Directories' native Membership Plans and Photo/Product Album feature. We can configure the plan restrictions, pricing, and album limits directly in the admin panel with no custom code required.
[00:01:14] Marcus: Great. Now, for buyer inquiries, biotech buyers often need a formal Request For Quote (RFQ) sent to multiple vendors simultaneously based on equipment category (e.g. Centrifuges, PCR machines).
[00:01:31] Elena: Brilliant Directories has a built-in Lead Match and Distribution system where a single buyer RFQ can automatically route to all active Gold & Silver vendors in that specific sub-category. We just need to configure the lead category rules.
[00:01:48] Marcus: What about compliance badges? Biotech buyers need to know if a vendor is ISO 9001 or ISO 13485 certified, or FDA registered.
[00:01:59] Elena: We can add custom checkbox fields for ISO 9001, ISO 13485, and FDA registration in the BD Member Profile form, and display visual certification badges right below the vendor title using custom HTML/CSS badge snippets. That is roughly 6 to 8 hours of frontend template customization.
[00:02:22] Marcus: Excellent. And we need our corporate brand colors: sterile lab teal (#008080) and crisp slate gray (#2F4F4F).
[00:02:34] Elena: Perfect, that's standard Theme Settings and CSS styling, about 12 hours. We can also handle the bulk import of your 650 vendor records via CSV.
[00:02:46] Marcus: Terrific, let's put together the proposal!
"""

def main():
    folder = os.path.join("shared", "data", "transcripts")
    os.makedirs(folder, exist_ok=True)
    
    with open(os.path.join(folder, "meeting_1_discovery.txt"), "w", encoding="utf-8") as f:
        f.write(MEETING_1.strip())
        
    with open(os.path.join(folder, "meeting_2_followup_changes.txt"), "w", encoding="utf-8") as f:
        f.write(MEETING_2.strip())
        
    with open(os.path.join(folder, "meeting_3_directory_marketplace.txt"), "w", encoding="utf-8") as f:
        f.write(MEETING_3.strip())
        
    print(f"Generated 3 meeting transcripts in {folder}")

if __name__ == "__main__":
    main()
