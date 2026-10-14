"""
Generates 50 realistic customer emails across 6 categories for Task 2 Inbox Agent.
Categories:
- how_to (15)
- new_project (10)
- refund (8)
- complaint (7)
- quote (5)
- follow_up (5)
"""

import json
import os

EMAILS = [
    # 1. HOW TO (15 emails)
    {
        "id": "EM-001",
        "customer_name": "Elena Rostova",
        "customer_email": "elena@denverwellnessdirectory.com",
        "company_name": "Denver Wellness Directory",
        "category": "how_to",
        "subject": "How to set up Stripe billing for monthly member renewals?",
        "body": "Hi team, we just moved to Brilliant Directories and we want to configure Stripe for automatic monthly recurring payments for our Premium Practitioner tier. Could you guide us on where in the admin portal we enter the Stripe API keys and enable auto-renewals?",
        "urgency": "medium",
        "date": "2026-10-10T14:30:00Z"
    },
    {
        "id": "EM-002",
        "customer_name": "Marcus Vance",
        "customer_email": "mvance@texastrades.org",
        "company_name": "Texas Trades Network",
        "category": "how_to",
        "subject": "Changing search radius from miles to kilometers",
        "body": "Hello, our directory is expanding into Canada and northern Mexico. Currently the location search defaults to miles. How do we change the default distance measurement from miles to kilometers across the entire directory?",
        "urgency": "low",
        "date": "2026-10-10T15:10:00Z"
    },
    {
        "id": "EM-003",
        "customer_name": "Sophie Martin",
        "customer_email": "smartin@parischefs.fr",
        "company_name": "Paris Culinary Collective",
        "category": "how_to",
        "subject": "Adding custom fields to the member registration form",
        "body": "We need to collect food hygiene certification numbers during chef registration. Is there a way to add a custom text field or document upload field into the standard member signup form without custom code?",
        "urgency": "medium",
        "date": "2026-10-10T16:00:00Z"
    },
    {
        "id": "EM-004",
        "customer_name": "David O'Connor",
        "customer_email": "david@dublincontractors.ie",
        "company_name": "Dublin Contractor Index",
        "category": "how_to",
        "subject": "Setting up lead distribution auto-routing",
        "body": "When a homeowner submits a lead inquiry on our site, we want it automatically forwarded to top 3 matching certified contractors in their postal code. How do we configure the Auto-Lead Distribution settings in Brilliant Directories?",
        "urgency": "high",
        "date": "2026-10-10T16:45:00Z"
    },
    {
        "id": "EM-005",
        "customer_name": "Priya Sharma",
        "customer_email": "priya@bengalurutechfounders.in",
        "company_name": "Bengaluru Tech Founders",
        "category": "how_to",
        "subject": "Bulk importing 500 members from CSV",
        "body": "We have a CSV spreadsheet with 500 tech companies and contacts. What is the recommended column header format for importing these members, and how do we prevent duplicate email records during import?",
        "urgency": "medium",
        "date": "2026-10-11T09:15:00Z"
    },
    {
        "id": "EM-006",
        "customer_name": "Lucas Becker",
        "customer_email": "lucas@berlinstartuphub.de",
        "company_name": "Berlin Startup Hub",
        "category": "how_to",
        "subject": "How to connect Google Tag Manager and GA4?",
        "body": "Hi, where do we place our Google Tag Manager container snippet (GTM-XXXXX) in the Brilliant Directories settings so it applies to both public and member portal pages?",
        "urgency": "low",
        "date": "2026-10-11T10:30:00Z"
    },
    {
        "id": "EM-007",
        "customer_name": "Chloe Bennett",
        "customer_email": "chloe@sydneycreatives.au",
        "company_name": "Sydney Creatives Co",
        "category": "how_to",
        "subject": "Enabling member review moderation before publishing",
        "body": "Can reviews posted by clients on member profiles be held in a moderation queue for admin approval before they appear live on the site? Where do we turn this on?",
        "urgency": "medium",
        "date": "2026-10-11T11:20:00Z"
    },
    {
        "id": "EM-008",
        "customer_name": "Carlos Gomez",
        "customer_email": "carlos@madridlegal.es",
        "company_name": "Madrid Legal Advisors",
        "category": "how_to",
        "subject": "Configuring custom email templates for welcome sequences",
        "body": "We would like to customize the automated welcome email sent immediately upon member account activation. Which menu controls the email templates and can we use merge tags for member name and membership level?",
        "urgency": "low",
        "date": "2026-10-11T13:40:00Z"
    },
    {
        "id": "EM-009",
        "customer_name": "Rachel Adams",
        "customer_email": "rachel@torontophysio.ca",
        "company_name": "Ontario Physio Network",
        "category": "how_to",
        "subject": "How do members claim existing unverified listings?",
        "body": "We pre-loaded 1,000 clinic listings into our directory as unclaimed profiles. How does a practitioner click 'Claim This Profile', verify ownership, and convert it to a paid plan?",
        "urgency": "high",
        "date": "2026-10-11T15:00:00Z"
    },
    {
        "id": "EM-010",
        "customer_name": "Ahmed Mansour",
        "customer_email": "ahmed@dubaibusinesshub.ae",
        "company_name": "Gulf Commerce Directory",
        "category": "how_to",
        "subject": "Setting up multi-level category hierarchies",
        "body": "We need Top Category > Sub Category > Sub-Sub Category (e.g. Construction > Electrical > Industrial High Voltage). Does Brilliant Directories support 3-tier category depth out of the box?",
        "urgency": "medium",
        "date": "2026-10-12T08:30:00Z"
    },
    {
        "id": "EM-011",
        "customer_name": "Yuki Tanaka",
        "customer_email": "yuki@tokyofreelance.jp",
        "company_name": "Tokyo Designers Guild",
        "category": "how_to",
        "subject": "How to embed video reels on member profile pages?",
        "body": "Our members want to embed YouTube and Vimeo video portfolios on their listing tabs. Where is the setting to enable rich media embeds for tier 2 and tier 3 members?",
        "urgency": "low",
        "date": "2026-10-12T10:00:00Z"
    },
    {
        "id": "EM-012",
        "customer_name": "Brenda Walsh",
        "customer_email": "brenda@chicagoarts.org",
        "company_name": "Chicago Cultural Exchange",
        "category": "how_to",
        "subject": "Restricting member search results to logged-in users only",
        "body": "We want our member directory to be private so only logged-in active members can view contact numbers and email addresses. Is there a native privacy setting for this?",
        "urgency": "high",
        "date": "2026-10-12T11:15:00Z"
    },
    {
        "id": "EM-013",
        "customer_name": "Felipe Ramos",
        "customer_email": "felipe@saopaulobiz.br",
        "company_name": "Brasil B2B Portal",
        "category": "how_to",
        "subject": "Setting up webhook notification on new member signup",
        "body": "We use HubSpot for CRM and want a webhook triggered every time a member signs up or upgrades. Where in Brilliant Directories do we configure outbound webhooks?",
        "urgency": "medium",
        "date": "2026-10-12T14:10:00Z"
    },
    {
        "id": "EM-014",
        "customer_name": "Hannah Lindqvist",
        "customer_email": "hannah@nordicartisans.se",
        "company_name": "Nordic Crafts Guild",
        "category": "how_to",
        "subject": "Configuring SEO meta tags and sitemap submission",
        "body": "How do we customize dynamic meta titles and descriptions for individual city and category landing pages to optimize our search ranking on Google?",
        "urgency": "low",
        "date": "2026-10-12T16:20:00Z"
    },
    {
        "id": "EM-015",
        "customer_name": "Liam Murphy",
        "customer_email": "liam@corkhospitality.ie",
        "company_name": "Munster Tourism Directory",
        "category": "how_to",
        "subject": "How to create coupon codes for 20% discount on annual plan?",
        "body": "We are running a Black Friday promo. How do we create discount promo codes in the Finance section that automatically apply a 20% discount to our annual plan checkout page?",
        "urgency": "medium",
        "date": "2026-10-13T09:00:00Z"
    },

    # 2. NEW PROJECT (10 emails)
    {
        "id": "EM-016",
        "customer_name": "Victoria Sterling",
        "customer_email": "victoria@luxuryconcierge.co.uk",
        "company_name": "Mayfair Luxury Services",
        "category": "new_project",
        "subject": "New Project Request: Complete VIP portal redesign & custom booking engine",
        "body": "Dear team, we are preparing to launch our ultra-luxury directory in London and Dubai. We need a custom homepage aesthetic, an interactive concierge booking calendar widget, and customized member cards. Can we schedule a scoping session?",
        "urgency": "high",
        "date": "2026-10-11T09:40:00Z"
    },
    {
        "id": "EM-017",
        "customer_name": "Jonathan Reed",
        "customer_email": "jreed@medtechdirectory.com",
        "company_name": "MedTech Global Directory",
        "category": "new_project",
        "subject": "Custom API integration with Salesforce Health Cloud",
        "body": "We have 15,000 healthcare suppliers and need a bidirectional sync between Brilliant Directories and Salesforce Health Cloud. When a supplier profile updates in BD, it must reflect in Salesforce and vice versa.",
        "urgency": "medium",
        "date": "2026-10-11T12:00:00Z"
    },
    {
        "id": "EM-018",
        "customer_name": "Ananya Patel",
        "customer_email": "ananya@indiasolarconnect.com",
        "company_name": "Solar Energy India",
        "category": "new_project",
        "subject": "Building a custom RFQ (Request for Quote) bidding marketplace",
        "body": "We want commercial property owners to post solar installation tenders, and certified vendors to submit private bids with milestone quotes. Can your team build this custom marketplace extension on top of our directory?",
        "urgency": "high",
        "date": "2026-10-11T14:40:00Z"
    },
    {
        "id": "EM-019",
        "customer_name": "Trevor Philips",
        "customer_email": "tphilips@autocarenetwork.org",
        "company_name": "National Auto Care Network",
        "category": "new_project",
        "subject": "Mobile application development for iOS & Android",
        "body": "We want a dedicated mobile app wrapped around our Brilliant Directories portal with geolocation push alerts, offline member search, and native biometric login. What would the timeline and development architecture look like?",
        "urgency": "medium",
        "date": "2026-10-12T11:00:00Z"
    },
    {
        "id": "EM-020",
        "customer_name": "Nathalie Dupont",
        "customer_email": "ndupont@swissfintech.ch",
        "company_name": "Swiss FinTech Directory",
        "category": "new_project",
        "subject": "Multilingual implementation (English, German, French, Italian)",
        "body": "We are launching a nationwide Swiss FinTech hub and require full multilingual switching across all navigation, member fields, category taxonomy, and static content. We need a quote and technical architecture plan.",
        "urgency": "high",
        "date": "2026-10-12T13:30:00Z"
    },
    {
        "id": "EM-021",
        "customer_name": "Sean MacBride",
        "customer_email": "smacbride@bostonbuilders.com",
        "company_name": "Boston General Contractors Guild",
        "category": "new_project",
        "subject": "Automated contractor license verification integration",
        "body": "We need to connect our directory signup workflow to the Massachusetts state license verification API so builder license numbers are checked automatically before listings are published. Can you build this custom webhook microservice?",
        "urgency": "high",
        "date": "2026-10-13T10:15:00Z"
    },
    {
        "id": "EM-022",
        "customer_name": "Isabella Rossi",
        "customer_email": "irossi@milanofashionindex.it",
        "company_name": "Milano Fashion Index",
        "category": "new_project",
        "subject": "Digital showroom feature development",
        "body": "We represent 400 indie fashion designers. We want to develop an interactive Lookbook/Digital Showroom feature where buyers can click hotspots on model photos to view product details and contact the designer directly.",
        "urgency": "medium",
        "date": "2026-10-13T11:45:00Z"
    },
    {
        "id": "EM-023",
        "customer_name": "George Hamilton",
        "customer_email": "ghamilton@aussievets.com.au",
        "company_name": "Australian Veterinary Association Directory",
        "category": "new_project",
        "subject": "Migration from legacy WordPress GeoDirectory to Brilliant Directories",
        "body": "We have 4,500 active veterinary clinics, reviews, and transaction history on WordPress GeoDirectory that has become too slow and buggy. We need complete turnkey migration into Brilliant Directories including SEO URL redirects.",
        "urgency": "high",
        "date": "2026-10-13T14:00:00Z"
    },
    {
        "id": "EM-024",
        "customer_name": "Miriam Al-Hassan",
        "customer_email": "miriam@qatararchitects.qa",
        "company_name": "Doha Architecture & Design Registry",
        "category": "new_project",
        "subject": "Interactive BIM / 3D model viewer on listing portfolio pages",
        "body": "Can we integrate an interactive Three.js / Sketchfab viewer into our architectural directory listings so clients can inspect 3D architectural renders directly on member profile pages?",
        "urgency": "medium",
        "date": "2026-10-14T08:50:00Z"
    },
    {
        "id": "EM-025",
        "customer_name": "Peter Van Dijk",
        "customer_email": "peter@amsterdamgreen.nl",
        "company_name": "Amsterdam Eco Directory",
        "category": "new_project",
        "subject": "Carbon offset calculator integration on member checkout",
        "body": "We want an optional carbon offset fee calculated dynamically via an external API and added to the member registration checkout total. Can your engineering team build this checkout customisation?",
        "urgency": "low",
        "date": "2026-10-14T10:20:00Z"
    },

    # 3. REFUND & CANCELLATION (8 emails)
    {
        "id": "EM-026",
        "customer_name": "Bradley Cooper",
        "customer_email": "bcooper@cooperlaw.com",
        "company_name": "Cooper Legal Associates",
        "category": "refund",
        "subject": "Request for refund: Accidental double charge on annual renewal",
        "body": "Hi, I just noticed our credit card was charged twice on October 12th for our annual premium directory listing ($499 x 2). Transaction IDs are TX-88219 and TX-88220. Please issue a refund for the duplicate transaction as soon as possible.",
        "urgency": "high",
        "date": "2026-10-12T17:10:00Z"
    },
    {
        "id": "EM-027",
        "customer_name": "Samantha Jenkins",
        "customer_email": "samantha@floridabridal.com",
        "company_name": "Sunshine State Weddings",
        "category": "refund",
        "subject": "Cancel subscription and refund unused monthly fee",
        "body": "We closed our wedding planning agency at the end of last month. Our account renewed automatically for $89 yesterday. We have not used the service this month. Please cancel our account immediately and refund the $89 fee.",
        "urgency": "medium",
        "date": "2026-10-13T08:15:00Z"
    },
    {
        "id": "EM-028",
        "customer_name": "Gerald Hopkins",
        "customer_email": "ghopkins@hopkinselectric.com",
        "company_name": "Hopkins Electrical Contractors",
        "category": "refund",
        "subject": "Downgrade plan and refund prorated difference",
        "body": "We upgraded to the Platinum tier two weeks ago but decided that Gold tier is sufficient for our small team. Can you downgrade our subscription back to Gold and credit/refund the prorated difference to our card on file?",
        "urgency": "medium",
        "date": "2026-10-13T12:30:00Z"
    },
    {
        "id": "EM-029",
        "customer_name": "Olga Petrova",
        "customer_email": "olga@vancouveryoga.ca",
        "company_name": "Lotus Yoga Collective",
        "category": "refund",
        "subject": "Cancellation confirmation and billing dispute",
        "body": "I sent an email requesting cancellation 3 weeks ago before the billing cycle ended, but I was still charged $120 yesterday. Please reverse this charge immediately and confirm that our account will not be billed again.",
        "urgency": "high",
        "date": "2026-10-13T15:45:00Z"
    },
    {
        "id": "EM-030",
        "customer_name": "Arthur Pendelton",
        "customer_email": "art@pendeltonantiques.co.uk",
        "company_name": "Cotswolds Antique Dealers",
        "category": "refund",
        "subject": "Refund request: Custom setup package not delivered on time",
        "body": "We purchased the 10-day VIP onboarding package for $750 three weeks ago, but our initial call was postponed twice by your team and our launch deadline has passed. We request a full refund of the onboarding fee.",
        "urgency": "high",
        "date": "2026-10-14T09:10:00Z"
    },
    {
        "id": "EM-031",
        "customer_name": "Kavita Rao",
        "customer_email": "kavita@mumbaitutors.in",
        "company_name": "Apex Tutoring Network",
        "category": "refund",
        "subject": "Cancel automatic renewal for next quarter",
        "body": "Please ensure that our quarterly subscription ending on November 15th does not renew automatically. Keep our listing active until the end of the current term. No refund requested for this quarter.",
        "urgency": "low",
        "date": "2026-10-14T11:40:00Z"
    },
    {
        "id": "EM-032",
        "customer_name": "Darren Walsh",
        "customer_email": "dwalsh@sydneyplumbing.com.au",
        "company_name": "Walsh Emergency Plumbing",
        "category": "refund",
        "subject": "Refund request for unused featured boost credits",
        "body": "We bought a 10-pack of homepage featured listing credits ($300) but only used 2 credits. We are shifting our marketing strategy and want a refund for the remaining 8 unused credits.",
        "urgency": "medium",
        "date": "2026-10-14T13:20:00Z"
    },
    {
        "id": "EM-033",
        "customer_name": "Claire Delacroix",
        "customer_email": "claire@bordeauxwineguide.com",
        "company_name": "Bordeaux Vintners Association",
        "category": "refund",
        "subject": "VAT invoice required and tax refund adjustment",
        "body": "We were billed $500 including 20% VAT, but our EU VAT ID (FR12345678901) was not entered at checkout. Please issue a corrected reverse-charge VAT invoice and refund the tax amount of $83.33.",
        "urgency": "medium",
        "date": "2026-10-14T16:05:00Z"
    },

    # 4. COMPLAINTS (7 emails)
    {
        "id": "EM-034",
        "customer_name": "Robert Chen",
        "customer_email": "rchen@bayareadental.com",
        "company_name": "SF Bay Dental Directory",
        "category": "complaint",
        "subject": "URGENT: Directory search is down for all visitors!",
        "body": "Our members are calling us non-stop. Whenever someone types a zip code in the main search bar, the page spins for 30 seconds and throws a 504 Gateway Timeout. This is our peak advertising week. Fix this immediately!",
        "urgency": "high",
        "date": "2026-10-12T15:20:00Z"
    },
    {
        "id": "EM-035",
        "customer_name": "Melissa Taylor",
        "customer_email": "melissa@austincreatives.com",
        "company_name": "Austin Creative Network",
        "category": "complaint",
        "subject": "Member emails going to spam folder - SPF/DKIM broken?",
        "body": "None of our automated member registration emails or password resets are reaching customer inboxes; they are all landing in spam or being rejected by Gmail. Did your recent DNS migration break our SPF and DKIM records?",
        "urgency": "high",
        "date": "2026-10-13T09:30:00Z"
    },
    {
        "id": "EM-036",
        "customer_name": "Jason Briggs",
        "customer_email": "jason@coloradooutdoors.net",
        "company_name": "Rocky Mountain Guides",
        "category": "complaint",
        "subject": "Mobile layout looks completely broken on iPhone 15",
        "body": "The filter sidebar covers the entire screen on mobile and there is no close or back button, making the site unusable for phone users. Over 60% of our traffic is mobile. This has been broken since Tuesday.",
        "urgency": "high",
        "date": "2026-10-13T14:15:00Z"
    },
    {
        "id": "EM-037",
        "customer_name": "Fatima Zahra",
        "customer_email": "fzahra@casablancabusiness.ma",
        "company_name": "Morocco Export Directory",
        "category": "complaint",
        "subject": "Slow support turnaround times on ticket #4492",
        "body": "I opened high-priority ticket #4492 four days ago regarding payment webhook failures and have received nothing but generic automated responses. We are losing paying members every day this remains unresolved.",
        "urgency": "high",
        "date": "2026-10-14T08:40:00Z"
    },
    {
        "id": "EM-038",
        "customer_name": "Gordon Ramsey Jr",
        "customer_email": "gramsey@londonhospitality.co.uk",
        "company_name": "London Chef & Sommelier Guild",
        "category": "complaint",
        "subject": "Members unable to upload profile avatar pictures",
        "body": "Whenever members try to upload a PNG or JPG avatar greater than 1MB, the uploader fails with 'Upload Error: File too large' even though our plan setting states a 5MB limit. Please fix this bug.",
        "urgency": "medium",
        "date": "2026-10-14T11:10:00Z"
    },
    {
        "id": "EM-039",
        "customer_name": "Alicia Mendez",
        "customer_email": "alicia@miamirealestate.com",
        "company_name": "South Florida Realtors Alliance",
        "category": "complaint",
        "subject": "Lead notification emails arriving with 4-hour delay",
        "body": "Real estate leads are time-sensitive. If our agents don't receive buyer inquiries within 5 minutes, clients go elsewhere. For the past 48 hours, lead alerts have been lagging by 3 to 5 hours. What is happening?",
        "urgency": "high",
        "date": "2026-10-14T14:20:00Z"
    },
    {
        "id": "EM-040",
        "customer_name": "Kenneth Wright",
        "customer_email": "kwright@ohioinsurance.org",
        "company_name": "Midwest Insurance Broker Network",
        "category": "complaint",
        "subject": "Inaccurate location pins on interactive Google Map",
        "body": "Several member pins are appearing in the middle of Lake Erie or in Kansas instead of their Columbus address. It looks like the Google Maps Geocoding API key has exceeded its quota or is misconfigured.",
        "urgency": "medium",
        "date": "2026-10-14T15:50:00Z"
    },

    # 5. QUOTES & PRICING (5 emails)
    {
        "id": "EM-041",
        "customer_name": "Dmitri Volkov",
        "customer_email": "dmitri@cyprusinvestors.com",
        "company_name": "Limassol Investment Portal",
        "category": "quote",
        "subject": "Quote request: Custom multi-currency payment checkout",
        "body": "We need our members to be able to pay in USD, EUR, and GBP with automatic currency conversion and localized Stripe checkout. Could you provide a formal quote and estimated timeline for implementing this?",
        "urgency": "medium",
        "date": "2026-10-12T16:40:00Z"
    },
    {
        "id": "EM-042",
        "customer_name": "Tara Fitzpatrick",
        "customer_email": "tara@irishweddings.ie",
        "company_name": "Ireland Wedding Venues",
        "category": "quote",
        "subject": "Quote for data migration of 2,200 venues and 8,000 photos",
        "body": "We have 2,200 venue profiles and approx 8,000 high-res gallery images on an old custom MySQL database. We need a quote to clean, map, and import all venues and photos into Brilliant Directories.",
        "urgency": "medium",
        "date": "2026-10-13T10:40:00Z"
    },
    {
        "id": "EM-043",
        "customer_name": "Simon Cowell",
        "customer_email": "scowell@musictalentuk.com",
        "company_name": "UK Talent & Booking Directory",
        "category": "quote",
        "subject": "Quote for custom audio streaming player on profiles",
        "body": "We want musicians and voice actors to upload MP3 demo reels with a waveform audio player embedded directly in search results and profiles. Please send a quote and estimated development hours.",
        "urgency": "low",
        "date": "2026-10-13T13:10:00Z"
    },
    {
        "id": "EM-044",
        "customer_name": "Leila Farhat",
        "customer_email": "leila@beirutdesign.org",
        "company_name": "Levant Creative Exchange",
        "category": "quote",
        "subject": "Annual maintenance and VIP support retainer quote",
        "body": "We are seeking a 12-month technical retainer covering ongoing monthly software updates, security audits, and 10 hours of minor design adjustments per month. What are your retainer packages?",
        "urgency": "medium",
        "date": "2026-10-14T09:30:00Z"
    },
    {
        "id": "EM-045",
        "customer_name": "Benjamin Cole",
        "customer_email": "bcole@seattleconsultants.com",
        "company_name": "Pacific Northwest Advisors",
        "category": "quote",
        "subject": "Quote for custom LinkedIn OAuth Social Login",
        "body": "Our enterprise consultants only want to log in using their corporate LinkedIn accounts. Can you quote the custom integration for 'Sign In With LinkedIn' and auto-populating their BD profile?",
        "urgency": "low",
        "date": "2026-10-14T12:00:00Z"
    },

    # 6. FOLLOW-UP (5 emails)
    {
        "id": "EM-046",
        "customer_name": "Dr. Gregory House",
        "customer_email": "ghouse@princetonplainsboro.org",
        "company_name": "NJ Specialists Directory",
        "category": "follow_up",
        "subject": "Follow-up on Ticket #3891: Custom search filter dropdown",
        "body": "Hi team, following up on our ticket from last Thursday regarding the medical sub-specialty cascading dropdown. Your team mentioned you were deploying the staging build on Monday. Is it ready for our review?",
        "urgency": "medium",
        "date": "2026-10-13T15:20:00Z"
    },
    {
        "id": "EM-047",
        "customer_name": "Angela Martin",
        "customer_email": "angela@scrantoncpas.com",
        "company_name": "Pennsylvania Accounting Society",
        "category": "follow_up",
        "subject": "Status update on QuickBooks recurring invoice sync",
        "body": "Just checking in on the custom Zapier/API bridge for QuickBooks sync that we approved two weeks ago. When can we expect the sandbox credentials to run our initial test transactions?",
        "urgency": "low",
        "date": "2026-10-14T10:00:00Z"
    },
    {
        "id": "EM-048",
        "customer_name": "Oscar Martinez",
        "customer_email": "oscar@latinobusinesscoalition.org",
        "company_name": "Latino Chamber of Commerce",
        "category": "follow_up",
        "subject": "Follow-up: Homepage banner mobile responsiveness fix",
        "body": "Thanks for updating the hero banner yesterday! It looks great on desktop, but on mobile portrait mode the call-to-action button is still slightly cut off at the bottom. Could you adjust the padding?",
        "urgency": "medium",
        "date": "2026-10-14T13:45:00Z"
    },
    {
        "id": "EM-049",
        "customer_name": "Phyllis Vance",
        "customer_email": "phyllis@vancerefrigeration.com",
        "company_name": "Northeast Appliance Technicians",
        "category": "follow_up",
        "subject": "Update on CSV export feature for member badges",
        "body": "Checking in to see if the custom member badge CSV export script is completed. Our annual convention is next Friday and we need to export the approved attendee roster for printing.",
        "urgency": "high",
        "date": "2026-10-14T15:10:00Z"
    },
    {
        "id": "EM-050",
        "customer_name": "Stanley Hudson",
        "customer_email": "stanley@crosswordclub.net",
        "company_name": "Florida Crossword & Games Guild",
        "category": "follow_up",
        "subject": "Follow-up on domain SSL certificate renewal",
        "body": "Our browser is showing an SSL certificate expiring in 5 days warning on our custom directory domain. Just confirming whether your automated renewal has processed or if we need to take action.",
        "urgency": "high",
        "date": "2026-10-14T16:30:00Z"
    }
]

def main():
    target_path = os.path.join("shared", "data", "emails_50.json")
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(EMAILS, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated {len(EMAILS)} customer emails in {target_path}")

if __name__ == "__main__":
    main()
